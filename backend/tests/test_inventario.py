from .conftest import stock


def test_buscar_elementos(client, login):
    r = client.get("/api/v1/elementos", params={"q": "multí"}, headers=login("estudiante"))
    assert r.status_code == 200
    assert [e["codigo"] for e in r.json()["items"]] == ["MED-001"]
    r = client.get("/api/v1/elementos/codigo/med-002", headers=login("estudiante"))
    assert r.json()["nombre"] == "Osciloscopio"


def test_crear_elemento_con_cantidad_inicial(client, login):
    datos = {"codigo": "her-001", "nombre": "Cautín", "cantidad_inicial": 4, "stock_minimo": 1}
    r = client.post("/api/v1/elementos", json=datos, headers=login("tecnico"))
    assert r.status_code == 201, r.text
    e = r.json()
    assert e["codigo"] == "HER-001" and e["cantidad_total"] == 4 and e["cantidad_disponible"] == 4
    assert client.post("/api/v1/elementos", json=datos, headers=login("tecnico")).status_code == 409
    movs = client.get("/api/v1/movimientos", params={"elemento_id": e["id"]}, headers=login("tecnico")).json()
    assert movs["total"] == 1 and movs["items"][0]["tipo"] == "entrada"


def test_editar_no_cambia_cantidades(client, login, ids):
    r = client.patch(f"/api/v1/elementos/{ids['MED-001']}", json={"ubicacion": "Gabinete 2", "cantidad_total": 999},
                     headers=login("tecnico"))
    assert r.status_code == 200
    assert r.json()["ubicacion"] == "Gabinete 2"
    assert r.json()["cantidad_total"] == 5


def test_movimientos_actualizan_saldos(client, login, ids):
    h = login("tecnico")
    r = client.post("/api/v1/movimientos", json={"elemento_id": ids["CON-001"], "tipo": "salida", "cantidad": 8,
                                                  "motivo": "Práctica de soldadura"}, headers=h)
    assert r.status_code == 201, r.text
    assert r.json()["saldo_disponible"] == 2 and r.json()["cantidad"] == -8
    e = stock(client, login, ids, "CON-001")
    assert e["cantidad_total"] == 2 and e["bajo_minimo"] is True

    r = client.post("/api/v1/movimientos", json={"elemento_id": ids["MED-001"], "tipo": "ajuste", "cantidad": -1,
                                                  "motivo": "Conteo físico"}, headers=h)
    assert r.status_code == 201 and r.json()["saldo_total"] == 4


def test_no_permite_stock_negativo(client, login, ids):
    r = client.post("/api/v1/movimientos", json={"elemento_id": ids["MED-002"], "tipo": "baja", "cantidad": 2,
                                                  "motivo": "Daño"}, headers=login("tecnico"))
    assert r.status_code == 409
    assert stock(client, login, ids, "MED-002")["cantidad_total"] == 1


def test_salida_solo_para_consumibles(client, login, ids):
    r = client.post("/api/v1/movimientos", json={"elemento_id": ids["MED-001"], "tipo": "salida", "cantidad": 1,
                                                  "motivo": "Uso"}, headers=login("tecnico"))
    assert r.status_code == 422


def test_movimiento_de_prestamo_no_es_manual(client, login, ids):
    r = client.post("/api/v1/movimientos", json={"elemento_id": ids["MED-001"], "tipo": "prestamo", "cantidad": 1,
                                                  "motivo": "x"}, headers=login("tecnico"))
    assert r.status_code == 422


def test_idempotencia_evita_duplicados(client, login, ids):
    h = {**login("tecnico"), "Idempotency-Key": "entrada-compra-0001"}
    cuerpo = {"elemento_id": ids["MED-001"], "tipo": "entrada", "cantidad": 3, "motivo": "Compra"}
    a = client.post("/api/v1/movimientos", json=cuerpo, headers=h)
    b = client.post("/api/v1/movimientos", json=cuerpo, headers=h)
    assert a.status_code == b.status_code == 201
    assert a.json()["id"] == b.json()["id"]
    assert b.headers.get("Idempotent-Replay") == "true"
    assert stock(client, login, ids, "MED-001")["cantidad_total"] == 8
