from datetime import datetime

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from ..dependencias import DB, requiere
from ..models import RegistroAuditoria, Usuario
from ..schemas import AuditoriaSalida, Pagina

router = APIRouter(prefix="/auditoria", tags=["Auditoría"])


@router.get("", response_model=Pagina[AuditoriaSalida])
def listar(
    db: DB,
    _: Usuario = requiere("auditoria:ver"),
    usuario_id: int | None = None,
    accion: str | None = Query(None, max_length=60),
    resultado: str | None = Query(None, pattern="^(ok|denegado|error)$"),
    canal: str | None = Query(None, max_length=20),
    desde_fecha: datetime | None = None,
    hasta_fecha: datetime | None = None,
    limite: int = Query(50, ge=1, le=200),
    desde: int = Query(0, ge=0),
):
    consulta = select(RegistroAuditoria)
    if usuario_id:
        consulta = consulta.where(RegistroAuditoria.usuario_id == usuario_id)
    if accion:
        consulta = consulta.where(RegistroAuditoria.accion == accion)
    if resultado:
        consulta = consulta.where(RegistroAuditoria.resultado == resultado)
    if canal:
        consulta = consulta.where(RegistroAuditoria.canal == canal)
    if desde_fecha:
        consulta = consulta.where(RegistroAuditoria.creado_en >= desde_fecha)
    if hasta_fecha:
        consulta = consulta.where(RegistroAuditoria.creado_en <= hasta_fecha)
    total = db.scalar(select(func.count()).select_from(consulta.subquery()))
    items = db.scalars(consulta.order_by(RegistroAuditoria.id.desc()).offset(desde).limit(limite)).all()
    return Pagina(total=total, items=items)
