"""Contraseñas, tokens JWT y matriz de permisos por rol (mínimo privilegio, RSG-01)."""

import base64
import hashlib
import hmac
import secrets
from datetime import timedelta

import jwt

from .config import get_settings
from .models import Rol
from .tiempo import ahora

# Cada permiso lista explícitamente los roles que lo tienen. Nada se hereda.
PERMISOS: dict[str, set[Rol]] = {
    "inventario:leer": {Rol.estudiante, Rol.docente, Rol.tecnico, Rol.coordinador, Rol.admin},
    "inventario:escribir": {Rol.tecnico},
    "prestamos:solicitar": {Rol.estudiante, Rol.docente, Rol.tecnico},
    "prestamos:ver_todos": {Rol.tecnico, Rol.coordinador, Rol.admin},
    "prestamos:aprobar": {Rol.docente, Rol.tecnico},
    "prestamos:entregar": {Rol.tecnico},
    "reportes:ver": {Rol.docente, Rol.tecnico, Rol.coordinador, Rol.admin},
    "auditoria:ver": {Rol.coordinador, Rol.admin},
    "usuarios:gestionar": {Rol.admin},
}


def tiene_permiso(rol: Rol, permiso: str) -> bool:
    return rol in PERMISOS.get(permiso, set())


def permisos_de(rol: Rol) -> list[str]:
    return sorted(p for p, roles in PERMISOS.items() if rol in roles)


def hash_password(password: str) -> str:
    iteraciones = get_settings().iteraciones_hash
    sal = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, iteraciones)
    return f"pbkdf2_sha256${iteraciones}${base64.b64encode(sal).decode()}${base64.b64encode(dk).decode()}"


def verificar_password(password: str, almacenado: str) -> bool:
    try:
        esquema, iteraciones, sal_b64, dk_b64 = almacenado.split("$")
        if esquema != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(sal_b64), int(iteraciones))
        return hmac.compare_digest(dk, base64.b64decode(dk_b64))
    except (ValueError, TypeError):
        return False


# Hash fijo para gastar el mismo tiempo cuando el usuario no existe (evita enumerar correos).
_HASH_FALSO: str | None = None


def verificar_password_falso(password: str) -> None:
    global _HASH_FALSO
    if _HASH_FALSO is None:
        _HASH_FALSO = hash_password(secrets.token_hex(8))
    verificar_password(password, _HASH_FALSO)


def crear_token(usuario_id: int, rol: Rol) -> tuple[str, int]:
    s = get_settings()
    segundos = s.token_minutos * 60
    payload = {
        "sub": str(usuario_id),
        "rol": rol.value,
        "iat": ahora(),
        "exp": ahora() + timedelta(seconds=segundos),
    }
    return jwt.encode(payload, s.jwt_secreto, algorithm=s.jwt_algoritmo), segundos


def decodificar_token(token: str) -> dict:
    s = get_settings()
    return jwt.decode(token, s.jwt_secreto, algorithms=[s.jwt_algoritmo])
