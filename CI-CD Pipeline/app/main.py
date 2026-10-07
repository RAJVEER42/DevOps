"""HTTP front for the pricing module. POST /quote with JSON items, GET /health."""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.pricing import total

VERSION = os.environ.get("APP_VERSION", "dev")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"status": "ok", "version": VERSION})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/quote":
            return self._send(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length", "0"))
        try:
            items = json.loads(self.rfile.read(length) or b"[]")
            return self._send(200, total([(i["price"], i["qty"]) for i in items]))
        except (ValueError, KeyError, TypeError) as exc:
            return self._send(400, {"error": str(exc)})

    def log_message(self, fmt, *args):
        print("%s %s" % (self.address_string(), fmt % args), flush=True)


def serve(port=8000):
    print("pricing-api %s listening on :%d" % (VERSION, port), flush=True)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    serve(int(os.environ.get("PORT", "8000")))
