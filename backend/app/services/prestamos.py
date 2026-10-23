"""Ciclo de vida de un préstamo.

pendiente ──aprobar──> aprobado ──entregar──> entregado ──devolver──> devuelto
    │                     │
    ├──rechazar──> rechazado
    └──cancelar──> cancelado <──cancelar──┘

El stock disponible solo se descuenta al entregar (cuando el elemento sale
físicamente del laboratorio) y se repone al devolver.
"""

from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..models import (
    Elemento,
    EstadoPrestamo,
    Prestamo,
    PrestamoDetalle,
    Rol,
    TipoMovimiento,
    Usuario,
)
from ..schemas import Devolucion, PrestamoCrear
from ..security import tiene_permiso
from ..tiempo import ahora, hoy_local
from .inventario import aplicar_movimiento, bloquear_elemento


def cargar(db: Session, prestamo_id: int, bloquear: bool = False) -> Prestamo:
    q = (
        select(Prestamo)
        .where(Prestamo.id == prestamo_id)
        .options(selectinload(Prestamo.detalles).selectinload(PrestamoDetalle.elemento))
    )
    if bloquear:
        q = q.with_for_update(of=Prestamo)
    prestamo = db.scalar(q)
    if prestamo is None:
        raise HTTPException(404, "Préstamo no encontrado.")
    return prestamo


def puede_ver(usuario: Usuario, prestamo: Prestamo) -> bool:
    return (
        tiene_permiso(usuario.rol, "prestamos:ver_todos")
        or prestamo.solicitante_id == usuario.id
        or prestamo.docente_responsable_id == usuario.id
    )


def _exigir_estado(prestamo: Prestamo, *estados: EstadoPrestamo) -> None:
    if prestamo.estado not in estados:
        permitidos = ", ".join(e.value for e in estados)
        raise HTTPException(
            409, f"El préstamo está en estado '{prestamo.estado.value}'; esta acción requiere: {permitidos}."
        )


def _verificar_disponibilidad(prestamo: Prestamo) -> None:
    faltantes = [
        f"{d.elemento.codigo} (pide {d.cantidad}, hay {d.elemento.cantidad_disponible})"
        for d in prestamo.detalles
        if d.cantidad > d.elemento.cantidad_disponible
    ]
    if faltantes:
        raise HTTPException(409, "Stock insuficiente: " + "; ".join(faltantes))


def crear(db: Session, solicitante: Usuario, datos: PrestamoCrear, canal: str) -> Prestamo:
    s = get_settings()
    hoy = hoy_local()
    if datos.fecha_devolucion_prevista < hoy:
        raise HTTPException(422, "La fecha de devolución no puede ser anterior a hoy.")
    if datos.fecha_devolucion_prevista > hoy + timedelta(days=s.dias_max_prestamo):
        raise HTTPException(422, f"El préstamo no puede superar {s.dias_max_prestamo} días.")
    if len(datos.detalles) > s.max_elementos_por_prestamo:
        raise HTTPException(422, f"Máximo {s.max_elementos_por_prestamo} elementos distintos por préstamo.")
    ids = [d.elemento_id for d in datos.detalles]
    if len(ids) != len(set(ids)):
        raise HTTPException(422, "Un elemento aparece repetido; indique la cantidad total en una sola línea.")

    if datos.docente_responsable_id is not None:
        docente = db.get(Usuario, datos.docente_responsable_id)
        if docente is None or docente.rol != Rol.docente or not docente.activo:
            raise HTTPException(422, "El docente responsable indicado no es válido.")

    elementos = {e.id: e for e in db.scalars(select(Elemento).where(Elemento.id.in_(ids)))}
    prestamo = Prestamo(
        solicitante_id=solicitante.id,
        docente_responsable_id=datos.docente_responsable_id,
        practica=datos.practica.strip(),
        fecha_devolucion_prevista=datos.fecha_devolucion_prevista,
        observaciones=datos.observaciones,
        canal=canal,
    )
    for d in datos.detalles:
        e = elementos.get(d.elemento_id)
        if e is None or not e.activo:
            raise HTTPException(422, f"El elemento {d.elemento_id} no existe o no está activo.")
        if e.es_consumible:
            raise HTTPException(422, f"{e.codigo} es consumible: se entrega como salida de material, no en préstamo.")
        prestamo.detalles.append(PrestamoDetalle(elemento=e, cantidad=d.cantidad))
    _verificar_disponibilidad(prestamo)
    db.add(prestamo)
    db.flush()
    return prestamo


def aprobar(db: Session, prestamo: Prestamo, usuario: Usuario) -> None:
    _exigir_estado(prestamo, EstadoPrestamo.pendiente)
    _verificar_disponibilidad(prestamo)
    prestamo.estado = EstadoPrestamo.aprobado
    prestamo.aprobado_por_id = usuario.id
    prestamo.aprobado_en = ahora()


def rechazar(db: Session, prestamo: Prestamo, usuario: Usuario, motivo: str) -> None:
    _exigir_estado(prestamo, EstadoPrestamo.pendiente)
    prestamo.estado = EstadoPrestamo.rechazado
    prestamo.motivo_rechazo = motivo
    prestamo.aprobado_por_id = usuario.id
    prestamo.aprobado_en = ahora()


def cancelar(db: Session, prestamo: Prestamo) -> None:
    _exigir_estado(prestamo, EstadoPrestamo.pendiente, EstadoPrestamo.aprobado)
    prestamo.estado = EstadoPrestamo.cancelado


def entregar(db: Session, prestamo: Prestamo, usuario: Usuario) -> None:
    _exigir_estado(prestamo, EstadoPrestamo.aprobado)
    # Orden fijo de bloqueo para evitar interbloqueos entre entregas simultáneas.
    for d in sorted(prestamo.detalles, key=lambda x: x.elemento_id):
        elemento = bloquear_elemento(db, d.elemento_id)
        aplicar_movimiento(
            db, elemento, TipoMovimiento.prestamo, d.cantidad, usuario,
            motivo=f"Entrega del préstamo #{prestamo.id}", prestamo_id=prestamo.id,
        )
    prestamo.estado = EstadoPrestamo.entregado
    prestamo.entregado_por_id = usuario.id
    prestamo.entregado_en = ahora()


def devolver(db: Session, prestamo: Prestamo, usuario: Usuario, datos: Devolucion) -> None:
    _exigir_estado(prestamo, EstadoPrestamo.entregado)
    por_elemento = {d.elemento_id: d for d in prestamo.detalles}
    danados: dict[int, int] = {}
    for dano in datos.danados:
        detalle = por_elemento.get(dano.elemento_id)
        if detalle is None:
            raise HTTPException(422, f"El elemento {dano.elemento_id} no hace parte de este préstamo.")
        danados[dano.elemento_id] = danados.get(dano.elemento_id, 0) + dano.cantidad
        if danados[dano.elemento_id] > detalle.cantidad:
            raise HTTPException(422, f"Se reportan más unidades dañadas que prestadas de {detalle.elemento.codigo}.")

    for d in sorted(prestamo.detalles, key=lambda x: x.elemento_id):
        elemento = bloquear_elemento(db, d.elemento_id)
        aplicar_movimiento(
            db, elemento, TipoMovimiento.devolucion, d.cantidad, usuario,
            motivo=f"Devolución del préstamo #{prestamo.id}", prestamo_id=prestamo.id,
        )
        n = danados.get(d.elemento_id, 0)
        if n:
            d.cantidad_danada = n
            aplicar_movimiento(
                db, elemento, TipoMovimiento.baja, n, usuario,
                motivo=f"Dañado o faltante en devolución del préstamo #{prestamo.id}", prestamo_id=prestamo.id,
            )
    if datos.observaciones:
        previo = f"{prestamo.observaciones}\n" if prestamo.observaciones else ""
        prestamo.observaciones = f"{previo}Devolución: {datos.observaciones}"
    prestamo.estado = EstadoPrestamo.devuelto
    prestamo.recibido_por_id = usuario.id
    prestamo.devuelto_en = ahora()
