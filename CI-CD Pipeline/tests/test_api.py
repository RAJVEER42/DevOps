import json
import threading
from http.server import HTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import pytest

from app.main import Handler


@pytest.fixture(scope="module")
def server_url():
    srv = HTTPServer(("127.0.0.1", 0), Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield "http://127.0.0.1:%d" % srv.server_address[1]
    srv.shutdown()


def test_health(server_url):
    with urlopen(server_url + "/health") as r:
        assert r.status == 200
        assert json.load(r)["status"] == "ok"


def test_quote(server_url):
    req = Request(server_url + "/quote", data=json.dumps([{"price": 100, "qty": 3}]).encode(),
                  headers={"Content-Type": "application/json"})
    with urlopen(req) as r:
        body = json.load(r)
    assert body["subtotal"] == "300.00"
    assert body["total"] == "354.00"


def test_quote_rejects_bad_payload(server_url):
    req = Request(server_url + "/quote", data=b'[{"price": "abc"}]',
                  headers={"Content-Type": "application/json"})
    with pytest.raises(HTTPError) as exc:
        urlopen(req)
    assert exc.value.code == 400
