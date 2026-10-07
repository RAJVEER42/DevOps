"""Prometheus instrumentation: request counter, latency histogram, in-flight gauge, /metrics."""
import time

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

REQUESTS = Counter("tracker_http_requests_total", "HTTP requests", ["method", "route", "status"])
LATENCY = Histogram("tracker_http_request_duration_seconds", "Request latency in seconds", ["method", "route"],
                    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5))
IN_FLIGHT = Gauge("tracker_http_in_flight_requests", "Requests currently being handled")
ISSUES_CREATED = Counter("tracker_issues_created_total", "Issues created via the API")


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", request.url.path)


def install(app: FastAPI) -> None:
    @app.middleware("http")
    async def record(request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        IN_FLIGHT.inc()
        start = time.perf_counter()
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception:
            status = 500
            raise
        finally:
            route = _route_template(request)
            LATENCY.labels(request.method, route).observe(time.perf_counter() - start)
            REQUESTS.labels(request.method, route, str(status)).inc()
            IN_FLIGHT.dec()
        return response

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
