from datetime import timedelta

from app.database import SessionLocal
from app.models import Prestamo
from app.tiempo import hoy_local

from .conftest import stock


def test_flujo_completo(client, login, ids, nuevo_prestamo):
    r = nuevo_prestamo(cantidad=2)
    assert r.status_code == 201, r.text
    p = r.json()
    assert p["estado"] == "pendiente" and p["canal"] == "api"
    # Solicitar no descuenta stock.
    assert stock(client, login, ids, "MED-001")["cantidad_disponible"] == 5

    r = client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("docente"))
    assert r.status_code == 200 and r.json()["estado"] == "aprobado"
    assert r.json()["aprobado_por"]["id"] == ids["docente"]

    r = client.post(f"/api/v1/prestamos/{p['id']}/entregar", headers=login("tecnico"))
    assert r.status_code == 200 and r.json()["estado"] == "entregado"
    e = stock(client, login, ids, "MED-001")
    assert e["cantidad_disponible"] == 3 and e["cantidad_prestada"] == 2

    r = client.post(f"/api/v1/prestamos/{p['id']}/devolver",
                    json={"observaciones": "Uno llegó con la pantalla rota",
                          "danados": [{"elemento_id": ids["MED-001"], "cantidad": 1}]},
                    headers=login("tecnico"))
    assert r.status_code == 200, r.text
    assert r.json()["estado"] == "devuelto"
    assert r.json()["detalles"][0]["cantidad_danada"] == 1
    e = stock(client, login, ids, "MED-001")
    assert e["cantidad_total"] == 4 and e["cantidad_disponible"] == 4

    tipos = [m["tipo"] for m in client.get("/api/v1/movimientos", params={"prestamo_id": p["id"]},
                                            headers=login("tecnico")).json()["items"]]
    assert sorted(tipos) == ["baja", "devolucion", "prestamo"]


def test_estudiante_no_puede_aprobar_ni_entregar(client, login, nuevo_prestamo):
    p = nuevo_prestamo().json()
    assert client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("estudiante")).status_code == 403
    assert client.post(f"/api/v1/prestamos/{p['id']}/entregar", headers=login("docente")).status_code == 403


def test_nadie_aprueba_su_propia_solicitud(client, login, nuevo_prestamo):
    p = nuevo_prestamo(quien="tecnico", docente=None).json()
    r = client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("tecnico"))
    assert r.status_code == 403
    assert client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("tecnico2")).status_code == 200


def test_solo_docente_responsable(client, login, nuevo_prestamo):
    p = nuevo_prestamo(docente="docente").json()
    assert client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("docente2")).status_code == 403
    assert client.post(f"/api/v1/prestamos/{p['id']}/rechazar", json={"motivo": "No aplica"},
                       headers=login("docente2")).status_code == 403
    r = client.post(f"/api/v1/prestamos/{p['id']}/rechazar", json={"motivo": "Práctica aplazada"},
                    headers=login("docente"))
    assert r.json()["estado"] == "rechazado" and r.json()["motivo_rechazo"] == "Práctica aplazada"


def test_no_se_salta_estados(client, login, nuevo_prestamo):
    p = nuevo_prestamo().json()
    assert client.post(f"/api/v1/prestamos/{p['id']}/entregar", headers=login("tecnico")).status_code == 409
    assert client.post(f"/api/v1/prestamos/{p['id']}/devolver", json={}, headers=login("tecnico")).status_code == 409
    client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("tecnico"))
    assert client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("tecnico")).status_code == 409


def test_stock_insuficiente(client, login, ids, nuevo_prestamo):
    assert nuevo_prestamo(codigo="MED-002", cantidad=2).status_code == 409
    a = nuevo_prestamo(codigo="MED-002", cantidad=1).json()
    b = nuevo_prestamo(quien="estudiante2", codigo="MED-002", cantidad=1).json()
    for p in (a, b):
        client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("tecnico"))
    assert client.post(f"/api/v1/prestamos/{a['id']}/entregar", headers=login("tecnico")).status_code == 200
    # El segundo ya no se puede entregar: el único osciloscopio salió.
    r = client.post(f"/api/v1/prestamos/{b['id']}/entregar", headers=login("tecnico"))
    assert r.status_code == 409
    assert stock(client, login, ids, "MED-002")["cantidad_disponible"] == 0


def test_validaciones_de_solicitud(client, login, ids, nuevo_prestamo):
    assert nuevo_prestamo(dias=-1).status_code == 422
    assert nuevo_prestamo(dias=60).status_code == 422
    assert nuevo_prestamo(codigo="CON-001").status_code == 422  # consumible
    assert nuevo_prestamo(docente="tecnico").status_code == 422  # no es docente
    cuerpo = {
        "practica": "Repetido",
        "fecha_devolucion_prevista": (hoy_local() + timedelta(days=2)).isoformat(),
        "detalles": [{"elemento_id": ids["MED-001"], "cantidad": 1}, {"elemento_id": ids["MED-001"], "cantidad": 1}],
    }
    assert client.post("/api/v1/prestamos", json=cuerpo, headers=login("estudiante")).status_code == 422


def test_visibilidad(client, login, nuevo_prestamo):
    p = nuevo_prestamo(quien="estudiante", docente="docente").json()
    assert client.get(f"/api/v1/prestamos/{p['id']}", headers=login("estudiante")).status_code == 200
    assert client.get(f"/api/v1/prestamos/{p['id']}", headers=login("docente")).status_code == 200
    assert client.get(f"/api/v1/prestamos/{p['id']}", headers=login("estudiante2")).status_code == 404
    assert client.get(f"/api/v1/prestamos/{p['id']}", headers=login("docente2")).status_code == 404
    assert client.get("/api/v1/prestamos", headers=login("estudiante2")).json()["total"] == 0
    assert client.get("/api/v1/prestamos", headers=login("coordinador")).json()["total"] == 1


def test_cancelar(client, login, nuevo_prestamo):
    p = nuevo_prestamo().json()
    assert client.post(f"/api/v1/prestamos/{p['id']}/cancelar", headers=login("estudiante2")).status_code == 404
    r = client.post(f"/api/v1/prestamos/{p['id']}/cancelar", headers=login("estudiante"))
    assert r.json()["estado"] == "cancelado"


def test_vencidos(client, login, ids, nuevo_prestamo):
    p = nuevo_prestamo(dias=1).json()
    client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("tecnico"))
    client.post(f"/api/v1/prestamos/{p['id']}/entregar", headers=login("tecnico"))
    with SessionLocal() as db:  # simula que la fecha ya pasó
        db.get(Prestamo, p["id"]).fecha_devolucion_prevista = hoy_local() - timedelta(days=2)
        db.commit()
    r = client.get("/api/v1/prestamos", params={"vencidos": True}, headers=login("tecnico"))
    assert r.json()["total"] == 1 and r.json()["items"][0]["vencido"] is True
    rep = client.get("/api/v1/reportes/vencidos", headers=login("coordinador")).json()
    assert rep["filas"][0]["dias_retraso"] == 2


def test_idempotencia_en_solicitud(client, login, nuevo_prestamo):
    h = {"Idempotency-Key": "whatsapp-msg-ABC123"}
    a = nuevo_prestamo(headers=h).json()
    b = nuevo_prestamo(headers=h).json()
    assert a["id"] == b["id"]
    assert client.get("/api/v1/prestamos", headers=login("tecnico")).json()["total"] == 1
