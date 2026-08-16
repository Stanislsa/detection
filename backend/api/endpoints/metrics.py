from fastapi import APIRouter, Response
from backend.core.prometheus_metrics import metrics_response, PROMETHEUS_AVAILABLE
router=APIRouter()
@router.get("/metrics")
async def prometheus_metrics():
    r=metrics_response(); return Response(content=r.body, media_type=r.media_type, status_code=r.status_code)
@router.get("/metrics/health")
async def metrics_health():
    return {"prometheus_available": PROMETHEUS_AVAILABLE, "status": "ok" if PROMETHEUS_AVAILABLE else "unavailable"}
