"""Única puerta para modificar cantidades del inventario.

Toda variación de stock pasa por `aplicar_movimiento`, que valida la operación,
bloquea la fila del elemento (SELECT ... FOR UPDATE en PostgreSQL) y deja el
movimiento con el saldo resultante.
"""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Elemento, Movimiento, TipoMovimiento, Usuario


def bloquear_elemento(db: Session, elemento_id: int) -> Elemento:
    elemento = db.scalar(select(Elemento).where(Elemento.id == elemento_id).with_for_update())
    if elemento is None:
        raise HTTPException(404, f"No existe el elemento {elemento_id}.")
    return elemento


def aplicar_movimiento(
    db: Session,
    elemento: Elemento,
    tipo: TipoMovimiento,
    cantidad: int,
    usuario: Usuario,
    motivo: str | None = None,
    prestamo_id: int | None = None,
) -> Movimiento:
    if cantidad == 0:
        raise HTTPException(422, "La cantidad no puede ser cero.")
    if tipo != TipoMovimiento.ajuste and cantidad < 0:
        raise HTTPException(422, "La cantidad debe ser positiva.")

    delta_total, delta_disp = 0, 0
    if tipo == TipoMovimiento.entrada:
        delta_total = delta_disp = cantidad
    elif tipo in (TipoMovimiento.salida, TipoMovimiento.baja):
        if tipo == TipoMovimiento.salida and not elemento.es_consumible:
            raise HTTPException(422, "Las salidas por consumo solo aplican a elementos consumibles. Use 'baja'.")
        delta_total = delta_disp = -cantidad
    elif tipo == TipoMovimiento.ajuste:
        delta_total = delta_disp = cantidad
    elif tipo == TipoMovimiento.prestamo:
        delta_disp = -cantidad
    elif tipo == TipoMovimiento.devolucion:
        delta_disp = cantidad

    nuevo_total = elemento.cantidad_total + delta_total
    nuevo_disp = elemento.cantidad_disponible + delta_disp
    if nuevo_disp < 0:
        raise HTTPException(
            409,
            f"Stock insuficiente de {elemento.codigo} ({elemento.nombre}): "
            f"disponibles {elemento.cantidad_disponible}, solicitados {abs(delta_disp)}.",
        )
    if nuevo_total < 0 or nuevo_disp > nuevo_total:
        raise HTTPException(409, f"La operación deja el inventario de {elemento.codigo} en un estado inválido.")

    elemento.cantidad_total = nuevo_total
    elemento.cantidad_disponible = nuevo_disp
    mov = Movimiento(
        elemento_id=elemento.id,
        tipo=tipo,
        cantidad=delta_disp if delta_disp else delta_total,
        motivo=motivo,
        saldo_total=nuevo_total,
        saldo_disponible=nuevo_disp,
        usuario_id=usuario.id,
        prestamo_id=prestamo_id,
    )
    db.add(mov)
    return mov
