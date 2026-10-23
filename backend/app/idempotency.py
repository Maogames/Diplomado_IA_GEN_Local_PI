"""Soporte para el encabezado Idempotency-Key en operaciones que crean o modifican stock.

Si el cliente (la web o el agente) reintenta una petición con la misma clave, se
devuelve la respuesta original en lugar de repetir la operación.
"""

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ClaveIdempotencia, Usuario


def leer_clave(request: Request) -> str | None:
    clave = request.headers.get("Idempotency-Key")
    if clave is None:
        return None
    clave = clave.strip()
    if not 8 <= len(clave) <= 80:
        raise HTTPException(400, "Idempotency-Key debe tener entre 8 y 80 caracteres.")
    return clave


def respuesta_previa(db: Session, usuario: Usuario, clave: str | None, ruta: str) -> JSONResponse | None:
    if clave is None:
        return None
    previa = db.scalar(
        select(ClaveIdempotencia).where(ClaveIdempotencia.usuario_id == usuario.id, ClaveIdempotencia.clave == clave)
    )
    if previa is None:
        return None
    if previa.ruta != ruta:
        raise HTTPException(409, "Esta Idempotency-Key ya se usó en otra operación.")
    return JSONResponse(previa.respuesta, status_code=previa.codigo_http, headers={"Idempotent-Replay": "true"})


def guardar(db: Session, usuario: Usuario, clave: str | None, ruta: str, codigo: int, cuerpo) -> None:
    if clave is None:
        return
    db.add(
        ClaveIdempotencia(
            usuario_id=usuario.id, clave=clave, ruta=ruta, codigo_http=codigo, respuesta=jsonable_encoder(cuerpo)
        )
    )
