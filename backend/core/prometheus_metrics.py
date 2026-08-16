"""Prometheus metrics for SentinelAI."""
from __future__ import annotations
import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
try:
    from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
if PROMETHEUS_AVAILABLE:
    REQUEST_COUNT = Counter("sentinel_http_requests_total","Total HTTP requests",["method","endpoint","status_code"])
    REQUEST_LATENCY = Histogram("sentinel_http_request_duration_seconds","HTTP latency",["method","endpoint"],
        buckets=(0.005,0.01,0.025,0.05,0.1,0.25,0.5,1.0,2.5,5.0,10.0))
    REQUESTS_IN_PROGRESS = Gauge("sentinel_http_requests_in_progress","In-progress",["method"])
    ERROR_COUNT = Counter("sentinel_errors_total","Errors",["error_code","status_code"])
    DETECTION_COUNT = Counter("sentinel_detections_total","Detections",["detector","result"])
    DETECTION_LATENCY = Histogram("sentinel_detection_duration_seconds","Detection latency",["detector"],
        buckets=(0.01,0.025,0.05,0.1,0.25,0.5,1.0,2.0,5.0))
    ALERT_COUNT = Counter("sentinel_alerts_total","Alerts",["channel","priority"])
    ACTIVE_CAMERAS = Gauge("sentinel_cameras_active","Active cameras")
    WS_CONNECTIONS = Gauge("sentinel_websocket_connections","WS connections")
    APP_INFO = Info("sentinel_app","App info")
else:
    REQUEST_COUNT=REQUEST_LATENCY=REQUESTS_IN_PROGRESS=ERROR_COUNT=None
    DETECTION_COUNT=DETECTION_LATENCY=ALERT_COUNT=ACTIVE_CAMERAS=WS_CONNECTIONS=APP_INFO=None

def record_error(error_code, status_code):
    if ERROR_COUNT is not None: ERROR_COUNT.labels(error_code=error_code, status_code=str(status_code)).inc()
def record_detection(detector, result, duration):
    if DETECTION_COUNT is not None: DETECTION_COUNT.labels(detector=detector, result=result).inc()
    if DETECTION_LATENCY is not None: DETECTION_LATENCY.labels(detector=detector).observe(duration)
def record_alert(channel, priority):
    if ALERT_COUNT is not None: ALERT_COUNT.labels(channel=channel, priority=priority).inc()
def set_active_cameras(n):
    if ACTIVE_CAMERAS is not None: ACTIVE_CAMERAS.set(n)
def set_ws_connections(n):
    if WS_CONNECTIONS is not None: WS_CONNECTIONS.set(n)
def init_app_info(name, version, environment):
    if APP_INFO is not None: APP_INFO.info({"name":name,"version":version,"environment":environment})

def _normalize_path(path):
    parts=path.strip("/").split("/")
    out=["{id}" if (p.isdigit() or (len(p)==36 and p.count("-")==4)) else p for p in parts]
    return "/"+ "/".join(out) if out else "/"

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not PROMETHEUS_AVAILABLE: return await call_next(request)
        if request.url.path in ("/metrics","/api/v1/metrics"): return await call_next(request)
        method=request.method; endpoint=_normalize_path(request.url.path)
        REQUESTS_IN_PROGRESS.labels(method=method).inc()
        start=time.perf_counter(); status_code=500
        try:
            response=await call_next(request); status_code=response.status_code; return response
        except Exception:
            status_code=500; raise
        finally:
            elapsed=time.perf_counter()-start
            REQUESTS_IN_PROGRESS.labels(method=method).dec()
            REQUEST_COUNT.labels(method=method,endpoint=endpoint,status_code=str(status_code)).inc()
            REQUEST_LATENCY.labels(method=method,endpoint=endpoint).observe(elapsed)

def metrics_response() -> Response:
    if not PROMETHEUS_AVAILABLE:
        return Response(content=b"# prometheus_client not installed\n", media_type="text/plain", status_code=503)
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
