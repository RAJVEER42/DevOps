"""Small Flask service: a status dashboard plus a couple of JSON endpoints.

Kept deliberately simple so the security tooling in the pipeline (SAST, SCA, secret
scanning, image scanning) has a realistic but readable target.
"""

import os
import platform
import time

from flask import Flask, jsonify, render_template, request

START = time.time()
VERSION = os.environ.get("APP_VERSION", "dev")


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html", version=VERSION, hostname=platform.node())

    @app.get("/health")
    def health():
        return jsonify(status="ok", version=VERSION)

    @app.get("/api/status")
    def status():
        return jsonify(
            version=VERSION,
            uptime_seconds=round(time.time() - START, 1),
            python=platform.python_version(),
            hostname=platform.node(),
        )

    @app.post("/api/convert")
    def convert():
        """Convert a temperature between C and F. Validates input instead of trusting it."""
        body = request.get_json(silent=True) or {}
        try:
            value = float(body["value"])
            unit = str(body["unit"]).upper()
        except (KeyError, TypeError, ValueError):
            return jsonify(error="expected {value: number, unit: 'C'|'F'}"), 400
        if unit == "C":
            return jsonify(value=value, unit="C", converted=round(value * 9 / 5 + 32, 2), to="F")
        if unit == "F":
            return jsonify(value=value, unit="F", converted=round((value - 32) * 5 / 9, 2), to="C")
        return jsonify(error="unit must be C or F"), 400

    return app


app = create_app()

if __name__ == "__main__":
    # Local development only. In the container gunicorn serves the app and owns the bind
    # address, so the dev server stays on loopback (Semgrep flagged 0.0.0.0 here in CI).
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")))
