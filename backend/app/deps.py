from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .audit import registrar_aparte
from .database import get_db
from .models import Usuario
from .security import decodificar_token, tiene_permiso

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

DB = Annotated[Session, Depends(get_db)]


def get_usuario_actual(request: Request, db: DB, token: Annotated[str, Depends(oauth2)]) -> Usuario:
    no_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión no válida o expirada.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decodificar_token(token)
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise no_autorizado
    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo:
        raise no_autorizado
    request.state.usuario = usuario  # para que el manejador de errores lo registre en auditoría
    return usuario


UsuarioActual = Annotated[Usuario, Depends(get_usuario_actual)]


def denegar(
    request: Request,
    usuario: Usuario | None,
    accion: str,
    mensaje: str,
    *,
    codigo: int = status.HTTP_403_FORBIDDEN,
    recurso: str | None = None,
    recurso_id=None,
    detalle: dict | None = None,
) -> HTTPException:
    """Registra la denegación en auditoría y devuelve la excepción para lanzarla."""
    registrar_aparte(
        request,
        usuario,
        accion,
        resultado="denegado",
        recurso=recurso,
        recurso_id=recurso_id,
        detalle={"motivo": mensaje, **(detalle or {})},
    )
    return HTTPException(status_code=codigo, detail=mensaje)


def requiere(permiso: str):
    def dependencia(request: Request, usuario: UsuarioActual) -> Usuario:
        if not tiene_permiso(usuario.rol, permiso):
            raise denegar(
                request,
                usuario,
                "permiso_denegado",
                "No tiene permiso para esta operación.",
                detalle={"permiso": permiso, "ruta": request.url.path, "metodo": request.method},
            )
        return usuario

    return Depends(dependencia)
