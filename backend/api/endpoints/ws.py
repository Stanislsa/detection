from __future__ import annotations
import asyncio, json
from datetime import datetime
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.core.logger import get_logger
router=APIRouter(); logger=get_logger(__name__)
class ConnectionManager:
    def __init__(self): self.active: Set[WebSocket]=set()
    async def connect(self, ws): await ws.accept(); self.active.add(ws)
    def disconnect(self, ws): self.active.discard(ws)
manager=ConnectionManager()
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({"type":"connected","payload":{"timestamp":datetime.utcnow().isoformat()}}))
        while True:
            try: raw=await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"type":"ping","payload":{}})); continue
            try: msg=json.loads(raw)
            except json.JSONDecodeError: continue
            if msg.get("type")=="ping":
                await websocket.send_text(json.dumps({"type":"pong","payload":{"timestamp":datetime.utcnow().isoformat()}}))
    except WebSocketDisconnect: manager.disconnect(websocket)
    except Exception as e: logger.warning(str(e)); manager.disconnect(websocket)
