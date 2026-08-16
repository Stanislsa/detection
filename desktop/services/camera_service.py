from __future__ import annotations
from typing import Dict
from datetime import datetime
import uuid
from desktop.models.camera_model import Camera, CameraStatus
from desktop.services.api_client import get_api_client, ApiError
def _map(data):
    status_raw=data.get("status") or data.get("is_active")
    if isinstance(status_raw, bool): status=CameraStatus.ONLINE if status_raw else CameraStatus.OFFLINE
    elif isinstance(status_raw, str):
        try: status=CameraStatus(status_raw.lower())
        except ValueError: status=CameraStatus.ONLINE if str(status_raw).upper() in ("ACTIVE","ONLINE") else CameraStatus.OFFLINE
    else: status=CameraStatus.ONLINE
    return Camera(id=str(data.get("id","")), name=data.get("name") or "Camera",
        url=data.get("rtsp_url") or data.get("url") or "", location=data.get("room") or data.get("location") or "",
        status=status, last_activity=datetime.now())
class CameraService:
    def __init__(self):
        self._cameras={}; self._api=get_api_client(); self._use_api=False; self._init()
    def _init(self):
        try:
            raw=self._api.list_cameras()
            if isinstance(raw, list) and raw:
                self._cameras={str(c.id):c for c in map(_map, raw)}; self._use_api=True; return
        except ApiError: pass
        self._demo()
    def _demo(self):
        demos=[Camera(id=f"cam{i}", name=n, url=f"rtsp://demo{i}.example.com/stream", location=z,
            status=CameraStatus.ONLINE if i<4 else CameraStatus.OFFLINE, last_activity=datetime.now())
            for i,(n,z) in enumerate([("Entrance","Zone A"),("Parking","Zone B"),("Warehouse","Zone C"),("Office","Zone D")],1)]
        self._cameras={c.id:c for c in demos}; self._use_api=False
    def get_all_cameras(self): return list(self._cameras.values())
    def get_online_cameras(self): return [c for c in self._cameras.values() if c.status==CameraStatus.ONLINE]
    def get_cameras_with_alerts(self): return []
    def get_camera(self, cid): return self._cameras.get(str(cid))
    def add_camera(self, name, url, location):
        cam=Camera(id=str(uuid.uuid4())[:8], name=name, url=url, location=location, status=CameraStatus.ONLINE, last_activity=datetime.now())
        self._cameras[cam.id]=cam; return cam
    def update_camera(self, camera_id, name=None, url=None, location=None):
        cam=self._cameras.get(str(camera_id))
        if not cam: return None
        if name is not None: cam.name=name
        if url is not None: cam.url=url
        if location is not None: cam.location=location
        return cam
    def delete_camera(self, camera_id):
        cid=str(camera_id)
        if cid in self._cameras: del self._cameras[cid]; return True
        return False
