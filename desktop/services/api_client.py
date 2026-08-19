from __future__ import annotations
import os
from typing import Any, Optional
import requests
try:
    from PyQt6.QtCore import QObject, pyqtSignal
except ImportError:
    class QObject:
        def __init__(self, parent=None): pass
    def pyqtSignal(*_a, **_k):
        class _Sig:
            def connect(self, *_a, **_k): pass
            def emit(self, *_a, **_k): pass
        return _Sig()
DEFAULT_BASE_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
class ApiError(Exception):
    def __init__(self, message, status_code=0, detail=None):
        super().__init__(message); self.status_code=status_code; self.detail=detail
class ApiClient(QObject):
    tokenChanged=pyqtSignal(); connectionChanged=pyqtSignal(bool)
    def __init__(self, base_url=DEFAULT_BASE_URL, parent=None):
        super().__init__(parent)
        self.base_url=base_url.rstrip("/")
        self._access_token=self._refresh_token=self._user=None
        self._session=requests.Session(); self._session.headers.update({"Accept":"application/json"})
        self._online=False
    @property
    def is_authenticated(self): return bool(self._access_token)
    @property
    def is_online(self): return self._online
    @property
    def user(self): return self._user
    def _url(self, path):
        if not path.startswith("/"): path="/"+path
        if not path.startswith("/api/"): path=f"/api/v1{path}"
        return f"{self.base_url}{path}"
    def request(self, method, path, *, data=None, json_body=None, params=None, auth=True, timeout=12.0, form=False):
        headers={}
        if auth and self._access_token: headers["Authorization"]=f"Bearer {self._access_token}"
        try:
            kw=dict(params=params, headers=headers, timeout=timeout)
            if form: kw["data"]=data
            else: kw.update(json=json_body, data=data)
            resp=self._session.request(method, self._url(path), **kw)
            self._online=True; self.connectionChanged.emit(True)
        except requests.RequestException as exc:
            self._online=False; self.connectionChanged.emit(False)
            raise ApiError(f"Backend unreachable: {exc}", 0) from exc
        if resp.status_code==204: return None
        try: body=resp.json() if resp.content else None
        except ValueError: body=resp.text
        if not resp.ok:
            detail=body.get("detail") if isinstance(body, dict) else body
            if isinstance(body, dict) and "error" in body: detail=body["error"].get("message", detail)
            raise ApiError(str(detail) if detail else f"HTTP {resp.status_code}", resp.status_code, detail)
        return body
    def get(self, path, **kw): return self.request("GET", path, **kw)
    def post(self, path, **kw): return self.request("POST", path, **kw)
    def patch(self, path, **kw): return self.request("PATCH", path, **kw)
    def delete(self, path, **kw): return self.request("DELETE", path, **kw)
    def login(self, username, password):
        body=self.request("POST","/auth/login", data={"username":username,"password":password}, form=True, auth=False)
        self._access_token=body.get("access_token"); self._refresh_token=body.get("refresh_token"); self._user=body.get("user")
        self.tokenChanged.emit(); return body
    def logout(self):
        self._access_token=self._refresh_token=self._user=None; self.tokenChanged.emit()
    def health(self): return self.get("/health/health", auth=False)
    def list_cameras(self): return self.get("/cameras") or []
    def create_camera(self, payload): return self.post("/cameras", json_body=payload)
    def list_alerts(self, skip=0, limit=100): return self.get("/alerts", params={"skip":skip,"limit":limit}) or []
    def dashboard_stats(self): return self.get("/dashboard/stats") or {}
    def dashboard_history(self, days=30):
        return self.get("/dashboard/history", params={"days": days}) or {}
    def dashboard_kpis(self, days=30):
        return self.get("/dashboard/kpis", params={"days": days}) or {}

    def system_metrics(self): return self.get("/system/metrics") or {}
    def ai_models(self): return self.get("/ai/models") or {}
    def start_training(self, payload): return self.post("/ai/train", json_body=payload)
    def telegram_config(self): return self.get("/telegram/config") or {}
    def telegram_test(self, message="🔔 test"): return self.post("/telegram/test", json_body={"message":message})
_api_client=None
def get_api_client(base_url=None):
    global _api_client
    if _api_client is None: _api_client=ApiClient(base_url or DEFAULT_BASE_URL)
    return _api_client
