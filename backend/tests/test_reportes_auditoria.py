from app.database import SessionLocal
from app.models import RegistroAuditoria


def test_reporte_inventario_trazable(client, login):
    r = client.get("/api/v1/reportes/inventario", headers=login("docente"))
    assert r.status_code == 200
    rep = r.json()
    assert rep["reporte"] == "inventario"
    assert rep["generado_por"]["rol"] == "docente"
    assert rep["fuente"] and rep["generado_en"]
    assert rep["total_filas"] == 3
    with SessionLocal() as db:
        reg = db.query(RegistroAuditoria).filter_by(accion="generar_reporte").one()
    assert reg.recurso_id == "inventario" and reg.detalle["filas"] == 3


def test_reporte_csv(client, login):
    r = client.get("/api/v1/reportes/inventario", params={"formato": "csv"}, headers=login("coordinador"))
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "attachment" in r.headers["content-disposition"]
    texto = r.content.decode("utf-8-sig")
    assert texto.splitlines()[0].startswith("codigo,nombre")
    assert "Multímetro" in texto


def test_reporte_prestamos_y_uso(client, login, nuevo_prestamo):
    p = nuevo_prestamo(cantidad=2).json()
    client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("docente"))
    client.post(f"/api/v1/prestamos/{p['id']}/entregar", headers=login("tecnico"))
    rep = client.get("/api/v1/reportes/prestamos", headers=login("tecnico")).json()
    assert rep["resumen"]["por_estado"] == {"entregado": 1}
    assert rep["filas"][0]["elementos"] == "MED-001 x2"
    # El otro docente no ve préstamos de prácticas que no tiene a cargo.
    assert client.get("/api/v1/reportes/prestamos", headers=login("docente2")).json()["total_filas"] == 0
    uso = client.get("/api/v1/reportes/uso-elementos", headers=login("tecnico")).json()
    assert uso["filas"][0] == {"codigo": "MED-001", "nombre": "Multímetro", "prestamos": 1, "unidades": 2, "danadas": 0}


def test_resumen(client, login, nuevo_prestamo):
    nuevo_prestamo()
    r = client.get("/api/v1/reportes/resumen", headers=login("coordinador")).json()
    assert r["elementos_activos"] == 3
    assert r["prestamos_por_estado"]["pendiente"] == 1


def test_errores_de_negocio_quedan_en_auditoria(client, login, nuevo_prestamo):
    nuevo_prestamo(codigo="MED-002", cantidad=5)  # stock insuficiente -> 409
    r = client.get("/api/v1/auditoria", params={"resultado": "error"}, headers=login("admin"))
    assert r.status_code == 200
    items = r.json()["items"]
    assert items and items[0]["detalle"]["codigo"] == 409


def test_auditoria_registra_flujo(client, login, nuevo_prestamo):
    p = nuevo_prestamo().json()
    client.post(f"/api/v1/prestamos/{p['id']}/aprobar", headers=login("docente"))
    acciones = [a["accion"] for a in client.get("/api/v1/auditoria", headers=login("coordinador")).json()["items"]]
    assert "solicitar_prestamo" in acciones and "aprobar_prestamo" in acciones and "login" in acciones


def test_health(client):
    assert client.get("/health").json()["estado"] == "ok"
