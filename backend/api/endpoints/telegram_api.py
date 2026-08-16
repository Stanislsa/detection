from __future__ import annotations
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from backend.api.dependencies import get_current_user
from backend.core.config import settings
router=APIRouter()
class TelegramTestRequest(BaseModel):
    message: str=Field(default="🔔 SentinelAI test"); chat_id: Optional[str]=None
@router.get("/config")
async def get_telegram_config(current_user=Depends(get_current_user)):
    token=getattr(settings,"TELEGRAM_BOT_TOKEN","") or ""
    masked=(token[:6]+"…"+token[-4:]) if len(token)>12 else ("***" if token else "")
    chat=getattr(settings,"TELEGRAM_CHAT_ID","") or ""
    return {"enabled":bool(token and chat),"bot_token_masked":masked,"chat_id":chat,"is_configured":bool(token and chat)}
@router.post("/test")
async def test_telegram(body: TelegramTestRequest, current_user=Depends(get_current_user)):
    token=getattr(settings,"TELEGRAM_BOT_TOKEN","") or ""
    chat_id=body.chat_id or getattr(settings,"TELEGRAM_CHAT_ID","") or ""
    if not token: raise HTTPException(400,"TELEGRAM_BOT_TOKEN not configured")
    if not chat_id: raise HTTPException(400,"chat_id required")
    try:
        import urllib.request, urllib.parse, json
        url=f"https://api.telegram.org/bot{token}/sendMessage"
        payload=urllib.parse.urlencode({"chat_id":chat_id,"text":body.message,"parse_mode":"HTML"}).encode()
        req=urllib.request.Request(url,data=payload,method="POST")
        with urllib.request.urlopen(req,timeout=15) as resp:
            data=json.loads(resp.read().decode())
        if not data.get("ok"): raise HTTPException(502,str(data))
        return {"ok":True,"message_id":data.get("result",{}).get("message_id")}
    except HTTPException: raise
    except Exception as e: raise HTTPException(502,str(e))
@router.get("/status")
async def telegram_status(current_user=Depends(get_current_user)):
    token=getattr(settings,"TELEGRAM_BOT_TOKEN","") or ""
    if not token: return {"ok":False,"configured":False}
    try:
        import urllib.request, json
        with urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getMe",timeout=10) as resp:
            data=json.loads(resp.read().decode())
        return {"ok":bool(data.get("ok")),"configured":True,"bot":data.get("result")}
    except Exception as e: return {"ok":False,"configured":True,"detail":str(e)}
