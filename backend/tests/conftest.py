import os
import tempfile
from datetime import timedelta

# La configuración debe quedar fijada antes de importar la aplicación.
_tmp = tempfile.mkdtemp(prefix="lab-pruebas-")
os.environ["LAB_DATABASE_URL"] = f"sqlite:///{_tmp}/pruebas.db"
os.environ["LAB_ENTORNO"] = "pruebas"
os.environ["LAB_ITERACIONES_HASH"] = "1000"
os.environ["LAB_CREAR_TABLAS_AL_INICIAR"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Categoria, Elemento, Rol, TipoMovimiento, Usuario  # noqa: E402
from app.security import hash_password  # noqa: E402
from app.services.inventario import aplicar_movimiento  # noqa: E402
from app.tiempo import hoy_local  # noqa: E402

CLAVE = "Clave-Prueba-1"
CORREOS = {
    "admin": "admin@t.co",
    "coordinador": "coord@t.co",
    "tecnico": "tec@t.co",
    "tecnico2": "tec2@t.co",
    "docente": "doc@t.co",
    "docente2": "doc2@t.co",
    "estudiante": "est@t.co",
    "estudiante2": "est2@t.co",
}


@pytest.fixture(autouse=True)
def base_limpia():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        h = hash_password(CLAVE)
        ids = {}
        for clave, email in CORREOS.items():
            rol = Rol(clave.rstrip("2"))
            u = Usuario(nombre=clave.title(), email=email, rol=rol, password_hash=h)
            db.add(u)
            db.flush()
            ids[clave] = u.id
        cat = Categoria(nombre="Instrumentos")
        db.add(cat)
        db.flush()
        tec = db.get(Usuario, ids["tecnico"])
        for codigo, nombre, cant, minimo, consumible in [
            ("MED-001", "Multímetro", 5, 1, False),
            ("MED-002", "Osciloscopio", 1, 0, False),
            ("CON-001", "Soldadura", 10, 3, True),
        ]:
            e = Elemento(codigo=codigo, nombre=nombre, categoria_id=cat.id, stock_minimo=minimo,
                         es_consumible=consumible, cantidad_total=0, cantidad_disponible=0)
            db.add(e)
            db.flush()
            aplicar_movimiento(db, e, TipoMovimiento.entrada, cant, tec, motivo="inicial")
        db.commit()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def login(client):
    cache: dict[str, dict] = {}

    def _login(quien: str) -> dict:
        if quien not in cache:
            r = client.post("/api/v1/auth/login", json={"email": CORREOS[quien], "password": CLAVE})
            assert r.status_code == 200, r.text
            cache[quien] = {"Authorization": f"Bearer {r.json()['access_token']}"}
        return cache[quien]

    return _login


@pytest.fixture
def ids():
    with SessionLocal() as db:
        usuarios = {u.email: u.id for u in db.query(Usuario)}
        elementos = {e.codigo: e.id for e in db.query(Elemento)}
    return {**{k: usuarios[v] for k, v in CORREOS.items()}, **elementos}


@pytest.fixture
def nuevo_prestamo(client, login, ids):
    def _crear(quien="estudiante", docente="docente", cantidad=2, codigo="MED-001", dias=3, headers=None):
        cuerpo = {
            "practica": "Circuitos - Práctica 1",
            "docente_responsable_id": ids[docente] if docente else None,
            "fecha_devolucion_prevista": (hoy_local() + timedelta(days=dias)).isoformat(),
            "detalles": [{"elemento_id": ids[codigo], "cantidad": cantidad}],
        }
        return client.post("/api/v1/prestamos", json=cuerpo, headers={**login(quien), **(headers or {})})

    return _crear


def stock(client, login, ids, codigo):
    r = client.get(f"/api/v1/elementos/{ids[codigo]}", headers=login("tecnico"))
    return r.json()
