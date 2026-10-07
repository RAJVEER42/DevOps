"""HTTP server that burns a little CPU per request, so an HPA has something to react to."""
import hashlib
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = b"ok\n"
        else:
            data = b"burn"
            for _ in range(int(os.environ.get("WORK", "40000"))):
                data = hashlib.sha256(data).digest()
            body = ("burned on %s: %s\n" % (os.environ.get("HOSTNAME", "?"), data.hex()[:16])).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
