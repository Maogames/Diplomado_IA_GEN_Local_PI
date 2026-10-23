"""Registro de auditoría (RSG-03).

Las denegaciones y errores se guardan en una sesión propia para que queden
registrados aunque la transacción de la petición se revierta.
"""

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import RegistroAuditoria, Usuario

CANALES_VALIDOS = {"web", "whatsapp", "agente", "api"}


def canal_de(request: Request | None) -> str:
    if request is None:
        return "api"
    canal = (request.headers.get("X-Canal") or "api").lower()
    return canal if canal in CANALES_VALIDOS else "api"


def _armar(
    request: Request | None,
    usuario: Usuario | None,
    accion: str,
    resultado: str,
    recurso: str | None,
    recurso_id,
    detalle: dict | None,
) -> RegistroAuditoria:
    return RegistroAuditoria(
        usuario_id=usuario.id if usuario else None,
        rol=usuario.rol.value if usuario else None,
        canal=canal_de(request),
        accion=accion,
        recurso=recurso,
        recurso_id=str(recurso_id) if recurso_id is not None else None,
        resultado=resultado,
        detalle=jsonable_encoder(detalle) if detalle else None,
        ip=request.client.host if request and request.client else None,
        request_id=getattr(request.state, "request_id", None) if request else None,
    )


def registrar(
    db: Session,
    request: Request | None,
    usuario: Usuario | None,
    accion: str,
    *,
    recurso: str | None = None,
    recurso_id=None,
    detalle: dict | None = None,
    resultado: str = "ok",
) -> None:
    """Agrega el registro a la transacción en curso: se guarda solo si la operación se confirma."""
    db.add(_armar(request, usuario, accion, resultado, recurso, recurso_id, detalle))


def registrar_aparte(
    request: Request | None,
    usuario: Usuario | None,
    accion: str,
    *,
    resultado: str,
    recurso: str | None = None,
    recurso_id=None,
    detalle: dict | None = None,
) -> None:
    """Guarda el registro en su propia transacción (para denegaciones y errores)."""
    db = SessionLocal()
    try:
        db.add(_armar(request, usuario, accion, resultado, recurso, recurso_id, detalle))
        db.commit()
    finally:
        db.close()
