import pytest

from app.database import SessionLocal
from app.models import RegistroAuditoria

from .conftest import CLAVE, CORREOS


def test_login_y_perfil(client, login):
    r = client.get("/api/v1/auth/me", headers=login("estudiante"))
    assert r.status_code == 200
    perfil = r.json()
    assert perfil["rol"] == "estudiante"
    assert "prestamos:solicitar" in perfil["permisos"]
    assert "inventario:escribir" not in perfil["permisos"]
    assert "password_hash" not in perfil


def test_login_incorrecto_no_revela_si_existe(client):
    a = client.post("/api/v1/auth/login", json={"email": "nadie@t.co", "password": "x"})
    b = client.post("/api/v1/auth/login", json={"email": CORREOS["docente"], "password": "x"})
    assert a.status_code == b.status_code == 401
    assert a.json() == b.json()


def test_bloqueo_por_intentos_fallidos(client):
    for _ in range(5):
        assert client.post("/api/v1/auth/login", json={"email": CORREOS["docente"], "password": "mala"}).status_code == 401
    r = client.post("/api/v1/auth/login", json={"email": CORREOS["docente"], "password": CLAVE})
    assert r.status_code == 429


def test_sin_token_401(client):
    assert client.get("/api/v1/elementos").status_code == 401
    assert client.get("/api/v1/elementos", headers={"Authorization": "Bearer basura"}).status_code == 401


def test_formulario_oauth2_para_swagger(client):
    r = client.post("/api/v1/auth/token", data={"username": CORREOS["tecnico"], "password": CLAVE})
    assert r.status_code == 200 and r.json()["token_type"] == "bearer"


@pytest.mark.parametrize(
    "quien,metodo,ruta,esperado",
    [
        ("estudiante", "post", "/api/v1/categorias", 403),
        ("docente", "post", "/api/v1/categorias", 403),
        ("admin", "post", "/api/v1/categorias", 403),  # mínimo privilegio: el admin no toca inventario
        ("tecnico", "post", "/api/v1/categorias", 201),
        ("estudiante", "get", "/api/v1/reportes/resumen", 403),
        ("docente", "get", "/api/v1/reportes/resumen", 200),
        ("estudiante", "get", "/api/v1/auditoria", 403),
        ("tecnico", "get", "/api/v1/auditoria", 403),
        ("coordinador", "get", "/api/v1/auditoria", 200),
        ("tecnico", "get", "/api/v1/usuarios", 403),
        ("admin", "get", "/api/v1/usuarios", 200),
        ("coordinador", "get", "/api/v1/elementos", 200),
    ],
)
def test_matriz_de_permisos(client, login, quien, metodo, ruta, esperado):
    kwargs = {"json": {"nombre": "Nueva categoría"}} if metodo == "post" else {}
    r = getattr(client, metodo)(ruta, headers=login(quien), **kwargs)
    assert r.status_code == esperado, r.text


def test_denegacion_queda_en_auditoria(client, login, ids):
    client.post("/api/v1/categorias", json={"nombre": "X1"}, headers=login("estudiante"))
    with SessionLocal() as db:
        reg = db.query(RegistroAuditoria).filter_by(accion="permiso_denegado").one()
    assert reg.resultado == "denegado"
    assert reg.usuario_id == ids["estudiante"]
    assert reg.detalle["permiso"] == "inventario:escribir"


def test_canal_se_registra(client, login):
    client.post("/api/v1/categorias", json={"nombre": "Redes"}, headers={**login("tecnico"), "X-Canal": "whatsapp"})
    with SessionLocal() as db:
        reg = db.query(RegistroAuditoria).filter_by(accion="crear_categoria").one()
    assert reg.canal == "whatsapp"


def test_admin_gestiona_usuarios(client, login):
    nuevo = {"nombre": "Nuevo Estudiante", "email": "NUEVO@t.co", "password": "Segura-123", "rol": "estudiante"}
    r = client.post("/api/v1/usuarios", json=nuevo, headers=login("admin"))
    assert r.status_code == 201
    assert r.json()["email"] == "nuevo@t.co"
    assert client.post("/api/v1/usuarios", json=nuevo, headers=login("admin")).status_code == 409
    uid = r.json()["id"]
    r = client.patch(f"/api/v1/usuarios/{uid}", json={"activo": False}, headers=login("admin"))
    assert r.json()["activo"] is False
    assert client.post("/api/v1/auth/login", json={"email": "nuevo@t.co", "password": "Segura-123"}).status_code == 401


def test_admin_no_puede_desactivarse(client, login, ids):
    r = client.patch(f"/api/v1/usuarios/{ids['admin']}", json={"activo": False}, headers=login("admin"))
    assert r.status_code == 409


def test_cambiar_clave(client, login):
    h = login("estudiante")
    assert client.post("/api/v1/auth/cambiar-clave", json={"actual": "mala", "nueva": "Otra-clave-1"}, headers=h).status_code == 400
    assert client.post("/api/v1/auth/cambiar-clave", json={"actual": CLAVE, "nueva": "Otra-clave-1"}, headers=h).status_code == 204
    r = client.post("/api/v1/auth/login", json={"email": CORREOS["estudiante"], "password": "Otra-clave-1"})
    assert r.status_code == 200


def test_listado_de_docentes_visible_para_estudiantes(client, login):
    r = client.get("/api/v1/usuarios/docentes", headers=login("estudiante"))
    assert r.status_code == 200
    assert {d["rol"] for d in r.json()} == {"docente"}
    assert "email" not in r.json()[0]
