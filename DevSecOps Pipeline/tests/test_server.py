import pytest

from app.server import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_index_renders(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Temp Service" in r.data


def test_health(client):
    assert client.get("/health").get_json()["status"] == "ok"


def test_status_has_uptime(client):
    body = client.get("/api/status").get_json()
    assert body["uptime_seconds"] >= 0
    assert "python" in body


@pytest.mark.parametrize("payload,expected", [
    ({"value": 100, "unit": "C"}, 212.0),
    ({"value": 32, "unit": "F"}, 0.0),
    ({"value": -40, "unit": "c"}, -40.0),
])
def test_convert(client, payload, expected):
    r = client.post("/api/convert", json=payload)
    assert r.status_code == 200
    assert r.get_json()["converted"] == expected


@pytest.mark.parametrize("payload", [{}, {"value": "hot", "unit": "C"}, {"value": 1, "unit": "K"}])
def test_convert_rejects_bad_input(client, payload):
    assert client.post("/api/convert", json=payload).status_code == 400
