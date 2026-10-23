"""Reportes trazables (RF-04).

Cada reporte indica quién lo generó, cuándo, con qué parámetros y de qué fuente
salen los datos, y su generación queda en auditoría. Con ?formato=csv se
descarga la tabla en CSV.
"""

import csv
import io
from datetime import date, datetime, time, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ..audit import registrar
from ..config import get_settings
from ..deps import DB, requiere
from ..models import (
    Elemento,
    EstadoPrestamo,
    Movimiento,
    Prestamo,
    PrestamoDetalle,
    Rol,
    TipoMovimiento,
    Usuario,
)
from ..tiempo import ahora, hoy_local

router = APIRouter(prefix="/reportes", tags=["Reportes"])

FUENTE = "Base de datos de inventario del laboratorio (API v1)"
Formato = Literal["json", "csv"]


def _limites(desde: date | None, hasta: date | None) -> tuple[datetime, datetime, date, date]:
    """Convierte fechas locales del laboratorio a un rango [inicio, fin) en UTC."""
    tz = ZoneInfo(get_settings().zona_horaria)
    hasta = hasta or hoy_local()
    desde = desde or (hasta - timedelta(days=30))
    inicio = datetime.combine(desde, time.min, tzinfo=tz)
    fin = datetime.combine(hasta + timedelta(days=1), time.min, tzinfo=tz)
    return inicio, fin, desde, hasta


def _responder(db, request: Request, usuario: Usuario, nombre: str, parametros: dict, filas: list[dict],
               formato: Formato, resumen: dict | None = None):
    registrar(db, request, usuario, "generar_reporte", recurso="reporte", recurso_id=nombre,
              detalle={"parametros": parametros, "filas": len(filas), "formato": formato})
    db.commit()
    if formato == "csv":
        buffer = io.StringIO()
        if filas:
            writer = csv.DictWriter(buffer, fieldnames=list(filas[0].keys()))
            writer.writeheader()
            writer.writerows(filas)
        marca = ahora().strftime("%Y%m%d-%H%M")
        return StreamingResponse(
            iter(["﻿" + buffer.getvalue()]),  # BOM para que Excel lea bien las tildes
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="reporte-{nombre}-{marca}.csv"'},
        )
    return {
        "reporte": nombre,
        "generado_en": ahora(),
        "generado_por": {"id": usuario.id, "nombre": usuario.nombre, "rol": usuario.rol.value},
        "fuente": FUENTE,
        "parametros": parametros,
        "resumen": resumen or {},
        "total_filas": len(filas),
        "filas": filas,
    }


def _texto_detalles(p: Prestamo) -> str:
    return "; ".join(f"{d.elemento.codigo} x{d.cantidad}" for d in p.detalles)


def _filtrar_docente(consulta, usuario: Usuario):
    if usuario.rol == Rol.docente:
        return consulta.where(Prestamo.docente_responsable_id == usuario.id)
    return consulta


@router.get("/resumen", summary="Indicadores generales para el tablero")
def resumen(request: Request, db: DB, usuario: Usuario = requiere("reportes:ver")):
    elementos = db.execute(
        select(
            func.count(Elemento.id),
            func.coalesce(func.sum(Elemento.cantidad_total), 0),
            func.coalesce(func.sum(Elemento.cantidad_disponible), 0),
        ).where(Elemento.activo.is_(True))
    ).one()
    bajo_minimo = db.scalar(
        select(func.count(Elemento.id)).where(
            Elemento.activo.is_(True), Elemento.stock_minimo > 0, Elemento.cantidad_disponible <= Elemento.stock_minimo
        )
    )
    base = _filtrar_docente(select(Prestamo.estado, func.count(Prestamo.id)), usuario).group_by(Prestamo.estado)
    por_estado = {e.value: 0 for e in EstadoPrestamo}
    por_estado.update({estado.value: n for estado, n in db.execute(base).all()})
    vencidos = db.scalar(
        _filtrar_docente(select(func.count(Prestamo.id)), usuario).where(
            Prestamo.estado == EstadoPrestamo.entregado, Prestamo.fecha_devolucion_prevista < hoy_local()
        )
    )
    movimientos_7d = db.scalar(select(func.count(Movimiento.id)).where(Movimiento.creado_en >= ahora() - timedelta(days=7)))
    return {
        "generado_en": ahora(),
        "fuente": FUENTE,
        "elementos_activos": elementos[0],
        "unidades_totales": int(elementos[1]),
        "unidades_disponibles": int(elementos[2]),
        "unidades_prestadas": int(elementos[1]) - int(elementos[2]),
        "elementos_bajo_minimo": bajo_minimo,
        "prestamos_por_estado": por_estado,
        "prestamos_vencidos": vencidos,
        "movimientos_ultimos_7_dias": movimientos_7d,
    }


@router.get("/inventario", summary="Estado actual del inventario")
def reporte_inventario(
    request: Request,
    db: DB,
    usuario: Usuario = requiere("reportes:ver"),
    categoria_id: int | None = None,
    solo_bajo_minimo: bool = False,
    formato: Formato = "json",
):
    consulta = select(Elemento).options(selectinload(Elemento.categoria)).where(Elemento.activo.is_(True))
    if categoria_id:
        consulta = consulta.where(Elemento.categoria_id == categoria_id)
    if solo_bajo_minimo:
        consulta = consulta.where(Elemento.stock_minimo > 0, Elemento.cantidad_disponible <= Elemento.stock_minimo)
    filas = [
        {
            "codigo": e.codigo,
            "nombre": e.nombre,
            "categoria": e.categoria.nombre if e.categoria else "",
            "ubicacion": e.ubicacion or "",
            "consumible": "sí" if e.es_consumible else "no",
            "total": e.cantidad_total,
            "disponible": e.cantidad_disponible,
            "prestado": e.cantidad_prestada,
            "stock_minimo": e.stock_minimo,
            "bajo_minimo": "sí" if e.bajo_minimo else "no",
        }
        for e in db.scalars(consulta.order_by(Elemento.codigo))
    ]
    resumen_ = {
        "elementos": len(filas),
        "bajo_minimo": sum(1 for f in filas if f["bajo_minimo"] == "sí"),
        "unidades_prestadas": sum(f["prestado"] for f in filas),
    }
    return _responder(db, request, usuario, "inventario",
                      {"categoria_id": categoria_id, "solo_bajo_minimo": solo_bajo_minimo}, filas, formato, resumen_)


@router.get("/prestamos", summary="Préstamos solicitados en un rango de fechas")
def reporte_prestamos(
    request: Request,
    db: DB,
    usuario: Usuario = requiere("reportes:ver"),
    desde: date | None = Query(None, description="Por defecto, hace 30 días"),
    hasta: date | None = Query(None, description="Por defecto, hoy"),
    estado: EstadoPrestamo | None = None,
    formato: Formato = "json",
):
    inicio, fin, desde, hasta = _limites(desde, hasta)
    consulta = (
        select(Prestamo)
        .options(selectinload(Prestamo.detalles).selectinload(PrestamoDetalle.elemento),
                 selectinload(Prestamo.solicitante), selectinload(Prestamo.docente_responsable))
        .where(Prestamo.creado_en >= inicio, Prestamo.creado_en < fin)
    )
    consulta = _filtrar_docente(consulta, usuario)
    if estado:
        consulta = consulta.where(Prestamo.estado == estado)
    prestamos = db.scalars(consulta.order_by(Prestamo.id)).all()
    filas = [
        {
            "id": p.id,
            "solicitado_en": p.creado_en.isoformat(timespec="minutes"),
            "solicitante": p.solicitante.nombre,
            "practica": p.practica,
            "docente_responsable": p.docente_responsable.nombre if p.docente_responsable else "",
            "estado": p.estado.value,
            "devolucion_prevista": p.fecha_devolucion_prevista.isoformat(),
            "vencido": "sí" if p.vencido else "no",
            "elementos": _texto_detalles(p),
            "canal": p.canal,
        }
        for p in prestamos
    ]
    conteo: dict[str, int] = {}
    for f in filas:
        conteo[f["estado"]] = conteo.get(f["estado"], 0) + 1
    return _responder(db, request, usuario, "prestamos",
                      {"desde": desde, "hasta": hasta, "estado": estado.value if estado else None},
                      filas, formato, {"por_estado": conteo, "vencidos": sum(f["vencido"] == "sí" for f in filas)})


@router.get("/vencidos", summary="Préstamos entregados cuya fecha de devolución ya pasó")
def reporte_vencidos(request: Request, db: DB, usuario: Usuario = requiere("reportes:ver"), formato: Formato = "json"):
    hoy = hoy_local()
    consulta = (
        select(Prestamo)
        .options(selectinload(Prestamo.detalles).selectinload(PrestamoDetalle.elemento),
                 selectinload(Prestamo.solicitante))
        .where(Prestamo.estado == EstadoPrestamo.entregado, Prestamo.fecha_devolucion_prevista < hoy)
    )
    consulta = _filtrar_docente(consulta, usuario)
    filas = [
        {
            "id": p.id,
            "solicitante": p.solicitante.nombre,
            "correo": p.solicitante.email,
            "practica": p.practica,
            "devolucion_prevista": p.fecha_devolucion_prevista.isoformat(),
            "dias_retraso": (hoy - p.fecha_devolucion_prevista).days,
            "elementos": _texto_detalles(p),
        }
        for p in db.scalars(consulta.order_by(Prestamo.fecha_devolucion_prevista))
    ]
    return _responder(db, request, usuario, "vencidos", {"fecha_corte": hoy}, filas, formato,
                      {"vencidos": len(filas)})


@router.get("/uso-elementos", summary="Elementos más prestados en un rango de fechas")
def reporte_uso(
    request: Request,
    db: DB,
    usuario: Usuario = requiere("reportes:ver"),
    desde: date | None = None,
    hasta: date | None = None,
    limite: int = Query(10, ge=1, le=100),
    formato: Formato = "json",
):
    inicio, fin, desde, hasta = _limites(desde, hasta)
    consulta = (
        select(
            Elemento.codigo,
            Elemento.nombre,
            func.count(func.distinct(PrestamoDetalle.prestamo_id)).label("prestamos"),
            func.sum(PrestamoDetalle.cantidad).label("unidades"),
            func.sum(PrestamoDetalle.cantidad_danada).label("danadas"),
        )
        .join(PrestamoDetalle, PrestamoDetalle.elemento_id == Elemento.id)
        .join(Prestamo, Prestamo.id == PrestamoDetalle.prestamo_id)
        .where(Prestamo.entregado_en >= inicio, Prestamo.entregado_en < fin)
        .group_by(Elemento.id, Elemento.codigo, Elemento.nombre)
        .order_by(func.sum(PrestamoDetalle.cantidad).desc())
        .limit(limite)
    )
    consulta = _filtrar_docente(consulta, usuario)
    filas = [
        {"codigo": c, "nombre": n, "prestamos": int(p), "unidades": int(u or 0), "danadas": int(d or 0)}
        for c, n, p, u, d in db.execute(consulta).all()
    ]
    return _responder(db, request, usuario, "uso-elementos", {"desde": desde, "hasta": hasta, "limite": limite},
                      filas, formato)


@router.get("/movimientos", summary="Movimientos de inventario en un rango de fechas")
def reporte_movimientos(
    request: Request,
    db: DB,
    usuario: Usuario = requiere("reportes:ver"),
    desde: date | None = None,
    hasta: date | None = None,
    tipo: TipoMovimiento | None = None,
    formato: Formato = "json",
):
    inicio, fin, desde, hasta = _limites(desde, hasta)
    consulta = (
        select(Movimiento)
        .options(selectinload(Movimiento.elemento), selectinload(Movimiento.usuario))
        .where(Movimiento.creado_en >= inicio, Movimiento.creado_en < fin)
    )
    if tipo:
        consulta = consulta.where(Movimiento.tipo == tipo)
    filas = [
        {
            "id": m.id,
            "fecha": m.creado_en.isoformat(timespec="minutes"),
            "codigo": m.elemento.codigo,
            "elemento": m.elemento.nombre,
            "tipo": m.tipo.value,
            "cantidad": m.cantidad,
            "saldo_disponible": m.saldo_disponible,
            "saldo_total": m.saldo_total,
            "motivo": m.motivo or "",
            "registrado_por": m.usuario.nombre,
            "prestamo_id": m.prestamo_id or "",
        }
        for m in db.scalars(consulta.order_by(Movimiento.id))
    ]
    conteo: dict[str, int] = {}
    for f in filas:
        conteo[f["tipo"]] = conteo.get(f["tipo"], 0) + 1
    return _responder(db, request, usuario, "movimientos",
                      {"desde": desde, "hasta": hasta, "tipo": tipo.value if tipo else None},
                      filas, formato, {"por_tipo": conteo})
