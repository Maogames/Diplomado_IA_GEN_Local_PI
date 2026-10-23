from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select

from ..audit import registrar, registrar_aparte
from ..config import get_settings
from ..deps import DB, UsuarioActual
from ..models import Usuario
from ..schemas import CambioClave, LoginEntrada, PerfilSalida, TokenSalida, UsuarioSalida
from ..security import (
    crear_token,
    hash_password,
    permisos_de,
    verificar_password,
    verificar_password_falso,
)
from ..tiempo import ahora

router = APIRouter(prefix="/auth", tags=["Autenticación"])

CREDENCIALES_INVALIDAS = "Correo o contraseña incorrectos."


def _autenticar(db, request: Request, email: str, password: str) -> TokenSalida:
    s = get_settings()
    email = email.strip().lower()
    usuario = db.scalar(select(Usuario).where(func.lower(Usuario.email) == email))

    if usuario is None:
        verificar_password_falso(password)
        registrar_aparte(request, None, "login", resultado="denegado", detalle={"email": email, "motivo": "no existe"})
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, CREDENCIALES_INVALIDAS)

    if usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora():
        registrar_aparte(request, usuario, "login", resultado="denegado", detalle={"motivo": "cuenta bloqueada"})
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Demasiados intentos fallidos. Intente de nuevo en unos minutos.",
        )

    if not usuario.activo or not verificar_password(password, usuario.password_hash):
        if usuario.activo:
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= s.max_intentos_login:
                usuario.bloqueado_hasta = ahora() + timedelta(minutes=s.minutos_bloqueo_login)
                usuario.intentos_fallidos = 0
            db.commit()
        registrar_aparte(
            request, usuario, "login", resultado="denegado",
            detalle={"motivo": "inactivo" if not usuario.activo else "contraseña incorrecta"},
        )
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, CREDENCIALES_INVALIDAS)

    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    registrar(db, request, usuario, "login")
    db.commit()
    token, segundos = crear_token(usuario.id, usuario.rol)
    return TokenSalida(access_token=token, expira_en=segundos)


@router.post("/login", response_model=TokenSalida)
def login(datos: LoginEntrada, request: Request, db: DB):
    return _autenticar(db, request, datos.email, datos.password)


@router.post("/token", response_model=TokenSalida, include_in_schema=True, summary="Login con formulario (Swagger)")
def token_formulario(form: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request, db: DB):
    return _autenticar(db, request, form.username, form.password)


@router.get("/me", response_model=PerfilSalida)
def perfil(usuario: UsuarioActual):
    return PerfilSalida(**UsuarioSalida.model_validate(usuario).model_dump(), permisos=permisos_de(usuario.rol))


@router.post("/cambiar-clave", status_code=204)
def cambiar_clave(datos: CambioClave, request: Request, db: DB, usuario: UsuarioActual):
    if not verificar_password(datos.actual, usuario.password_hash):
        registrar_aparte(request, usuario, "cambiar_clave", resultado="denegado")
        raise HTTPException(400, "La contraseña actual no es correcta.")
    usuario.password_hash = hash_password(datos.nueva)
    registrar(db, request, usuario, "cambiar_clave", recurso="usuario", recurso_id=usuario.id)
    db.commit()
