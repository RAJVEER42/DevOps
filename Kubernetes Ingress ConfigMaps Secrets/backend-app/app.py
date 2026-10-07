"""Tiny HTTP backend that reports its configuration.

Config comes from environment variables (ConfigMap + Secret) and from files mounted
into /etc/app-config, so both injection methods can be verified from a browser or curl.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

CONFIG_KEYS = ["APP_ENV", "LOG_LEVEL", "FEATURE_DARK_MODE", "ITEMS_PER_PAGE"]
SECRET_KEYS = ["DB_USER", "DB_PASSWORD", "API_TOKEN"]
MOUNT_DIR = "/etc/app-config"


def mounted_files():
    if not os.path.isdir(MOUNT_DIR):
        return {}
    out = {}
    for name in sorted(os.listdir(MOUNT_DIR)):
        path = os.path.join(MOUNT_DIR, name)
        if os.path.isfile(path):
            with open(path) as fh:
                out[name] = fh.read().strip()
    return out


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/health"):
            body = b"ok\n"
        else:
            payload = {
                "service": "catalog-api",
                "hostname": os.environ.get("HOSTNAME", "?"),
                "path": self.path,
                "from_configmap_env": {k: os.environ.get(k) for k in CONFIG_KEYS},
                "from_configmap_volume": mounted_files(),
                # Only report that the secret arrived; never echo the value itself.
                "from_secret_env": {k: ("set, %d chars" % len(os.environ[k])) if k in os.environ else None for k in SECRET_KEYS},
            }
            body = (json.dumps(payload, indent=2) + "\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("%s %s" % (self.address_string(), fmt % args), flush=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print("catalog-api listening on :%d" % port, flush=True)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
