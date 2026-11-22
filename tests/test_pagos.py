import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
URL = "/api/payments/process"


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "service": "pagos"}


def test_aprueba_un_monto_normal_con_transaccion_unica():
    r = client.post(URL, json={"order_id": 15, "monto": 370000.00})

    assert r.status_code == 200
    datos = r.json()
    assert datos["estado"] == "APROBADO"
    assert datos["mensaje"] == "Pago aprobado"
    uuid.UUID(datos["transaccion_id"])  # falla si no es un UUID válido


def test_cada_pago_tiene_un_comprobante_distinto():
    a = client.post(URL, json={"order_id": 1, "monto": 100}).json()
    b = client.post(URL, json={"order_id": 2, "monto": 100}).json()
    assert a["transaccion_id"] != b["transaccion_id"]


def test_aprueba_justo_en_el_limite():
    r = client.post(URL, json={"order_id": 1, "monto": 10_000_000})
    assert r.json()["estado"] == "APROBADO"


def test_rechaza_si_supera_el_limite():
    r = client.post(URL, json={"order_id": 1, "monto": 10_000_000.01})

    assert r.status_code == 200
    datos = r.json()
    assert datos["estado"] == "RECHAZADO"
    assert datos["transaccion_id"] is None


def test_el_limite_se_configura_desde_el_entorno(monkeypatch):
    monkeypatch.setenv("LIMITE_APROBACION", "1000")
    assert client.post(URL, json={"order_id": 1, "monto": 5000}).json()["estado"] == "RECHAZADO"
    assert client.post(URL, json={"order_id": 1, "monto": 500}).json()["estado"] == "APROBADO"


def test_monto_cero_o_negativo_es_error_400_con_formato_uniforme():
    for monto in [0, -50]:
        r = client.post(URL, json={"order_id": 1, "monto": monto})
        assert r.status_code == 400
        datos = r.json()
        assert datos["error"] is True
        assert datos["detalles"][0]["campo"] == "monto"


def test_order_id_invalido_es_error_400():
    r = client.post(URL, json={"order_id": 0, "monto": 100})
    assert r.status_code == 400
    assert r.json()["detalles"][0]["campo"] == "order_id"


def test_faltan_campos_es_error_400():
    r = client.post(URL, json={})
    assert r.status_code == 400
    campos = {d["campo"] for d in r.json()["detalles"]}
    assert campos == {"order_id", "monto"}


def test_json_mal_formado_es_error_400():
    r = client.post(URL, content="esto no es json", headers={"Content-Type": "application/json"})
    assert r.status_code == 400
    assert r.json()["error"] is True


def test_ruta_inexistente_responde_404_con_formato_uniforme():
    r = client.get("/api/no-existe")
    assert r.status_code == 404
    assert r.json()["error"] is True


def test_la_documentacion_openapi_esta_disponible():
    assert client.get("/docs").status_code == 200
    assert URL in client.get("/openapi.json").json()["paths"]
