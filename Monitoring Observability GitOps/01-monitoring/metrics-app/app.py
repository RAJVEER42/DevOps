"""Small web service instrumented with prometheus_client.

Exposes request count, latency histogram and in-flight gauge on /metrics, and a few routes
whose behaviour is deliberately uneven so the graphs have something to show.
"""
import os
import random
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUESTS = Counter("shop_http_requests_total", "HTTP requests", ["route", "status"])
LATENCY = Histogram("shop_http_request_duration_seconds", "Request latency", ["route"],
                    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2))
IN_FLIGHT = Gauge("shop_http_in_flight", "Requests being served right now")
ORDERS = Counter("shop_orders_total", "Orders placed")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            body = generate_latest()
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.end_headers()
            return self.wfile.write(body)
        route = self.path.split("?")[0]
        IN_FLIGHT.inc()
        start = time.time()
        try:
            if route == "/health":
                status, body = 200, b"ok\n"
            elif route == "/products":
                time.sleep(random.uniform(0.01, 0.08))
                status, body = 200, b'[{"id":1,"name":"kettle"},{"id":2,"name":"mug"}]\n'
            elif route == "/checkout":
                time.sleep(random.uniform(0.1, 0.6))
                if random.random() < 0.15:
                    status, body = 500, b"payment gateway timeout\n"
                else:
                    ORDERS.inc()
                    status, body = 200, b"order placed\n"
            else:
                status, body = 404, b"not found\n"
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        finally:
            LATENCY.labels(route).observe(time.time() - start)
            REQUESTS.labels(route, str(status)).inc()
            IN_FLIGHT.dec()

    def log_message(self, fmt, *args):
        print("%s %s" % (time.strftime("%H:%M:%S"), fmt % args), flush=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print("shop-metrics listening on :%d" % port, flush=True)
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
