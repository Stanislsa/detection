from __future__ import annotations
from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, Depends
from backend.api.dependencies import get_current_user
from backend.core.config import settings
router=APIRouter()
def _collect():
    m={"timestamp": datetime.utcnow().isoformat(),"app":{"name":settings.APP_NAME,"version":settings.APP_VERSION,"environment":settings.ENVIRONMENT}}
    try:
        import psutil, os
        proc=psutil.Process(os.getpid()); vm=psutil.virtual_memory(); disk=psutil.disk_usage("/")
        m["cpu"]={"percent":psutil.cpu_percent(interval=0.2),"count":psutil.cpu_count() or 1}
        m["memory"]={"total_mb":round(vm.total/1e6,1),"used_mb":round(vm.used/1e6,1),"percent":vm.percent}
        m["disk"]={"total_gb":round(disk.total/1e9,2),"used_gb":round(disk.used/1e9,2),"percent":disk.percent}
        m["process"]={"pid":proc.pid,"rss_mb":round(proc.memory_info().rss/1e6,1)}
    except ImportError:
        m["cpu"]={"percent":0}; m["memory"]=m["disk"]=m["process"]={}
    m["gpu"]=[{"available":False}]
    return m
@router.get("/metrics")
async def system_metrics(current_user=Depends(get_current_user)): return _collect()
@router.get("/metrics/public")
async def system_metrics_public():
    d=_collect(); d.pop("process",None); return d
@router.get("/info")
async def system_info(current_user=Depends(get_current_user)):
    return {"app_name":settings.APP_NAME,"version":settings.APP_VERSION,"environment":settings.ENVIRONMENT,
            "ai_backend":settings.AI_BACKEND,"telegram_configured":bool(getattr(settings,"TELEGRAM_BOT_TOKEN","")),
            "timestamp":datetime.utcnow().isoformat()}
