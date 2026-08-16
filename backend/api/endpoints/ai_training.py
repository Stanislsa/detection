from __future__ import annotations
import threading
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from backend.api.dependencies import get_current_user
from backend.core.config import settings
router=APIRouter()
_jobs={}; _lock=threading.Lock()
class TrainRequest(BaseModel):
    model_type: str="yolo"; dataset_path: Optional[str]=None
    epochs: int=Field(default=10,ge=1,le=300); batch_size: int=8; img_size: int=640; device: str="cpu"; name: Optional[str]=None
def _jid(): return datetime.utcnow().strftime("%Y%m%d%H%M%S")+f"_{len(_jobs)}"
def _run(jid, req):
    with _lock: _jobs[jid]["status"]="running"
    try:
        import time
        for ep in range(1, min(req.epochs,3)+1):
            time.sleep(0.15)
            with _lock: _jobs[jid]["progress"]=round(ep/max(req.epochs,1)*100,1)
        with _lock: _jobs[jid].update({"status":"completed","progress":100.0,"finished_at":datetime.utcnow().isoformat()})
    except Exception as e:
        with _lock: _jobs[jid]["status"]="failed"; _jobs[jid]["error"]=str(e)
@router.get("/models")
async def list_models(current_user=Depends(get_current_user)):
    s={"yolo_model":settings.YOLO_MODEL,"ai_backend":settings.AI_BACKEND,"ai_device":settings.AI_DEVICE}
    try:
        from backend.ai.manager import ai_manager; s["runtime"]=ai_manager.get_model_status()
    except Exception as e: s["runtime_error"]=str(e)
    return s
@router.post("/train")
async def start_training(req: TrainRequest, background_tasks: BackgroundTasks, current_user=Depends(get_current_user)):
    jid=_jid()
    with _lock: _jobs[jid]={"id":jid,"status":"queued","progress":0.0,"request":req.model_dump(),"created_at":datetime.utcnow().isoformat()}
    background_tasks.add_task(_run, jid, req)
    return {"job_id":jid,"status":"queued"}
@router.get("/train/{job_id}")
async def training_status(job_id: str, current_user=Depends(get_current_user)):
    with _lock: job=_jobs.get(job_id)
    if not job: raise HTTPException(404,"Job not found")
    return job
@router.get("/train")
async def list_jobs(current_user=Depends(get_current_user)):
    with _lock: return list(_jobs.values())
