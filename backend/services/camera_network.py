"""Utilitaires réseau local caméras RTSP."""
from __future__ import annotations
import os, re, socket
from typing import Any, Dict, Optional
from urllib.parse import urlparse
from backend.core.config import settings
from backend.core.logger import get_logger
logger = get_logger(__name__)

def parse_rtsp_url(url: str) -> Dict[str, Any]:
    u = urlparse(url)
    return {"scheme": u.scheme, "host": u.hostname, "port": u.port or 554,
            "path": u.path or "/", "has_credentials": bool(u.username), "masked": _mask(url)}

def _mask(url: str) -> str:
    return re.sub(r"(rtsp://)([^:/@]+):([^@]+)@", r"\1***:***@", url)

def tcp_reachable(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False

def probe_rtsp(url: str, *, grab_frame: bool = True) -> Dict[str, Any]:
    info = parse_rtsp_url(url)
    result: Dict[str, Any] = {"ok": False, "url_masked": info["masked"], "host": info["host"],
        "port": info["port"], "tcp_open": False, "stream_open": False, "frame_ok": False,
        "error": None, "transport": getattr(settings, "RTSP_TRANSPORT", "tcp")}
    if not info["host"]:
        result["error"] = "host manquant"; return result
    result["tcp_open"] = tcp_reachable(info["host"], info["port"],
        timeout=max(1.0, getattr(settings, "RTSP_OPEN_TIMEOUT_MS", 5000) / 1000.0))
    if not result["tcp_open"]:
        result["error"] = f"TCP {info['host']}:{info['port']} injoignable"; return result
    if not grab_frame:
        result["ok"] = True; return result
    try:
        import cv2
        transport = str(getattr(settings, "RTSP_TRANSPORT", "tcp")).lower()
        os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS",
            f"rtsp_transport;{transport}|fflags;nobuffer|flags;low_delay")
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        try: cap.set(cv2.CAP_PROP_BUFFERSIZE, int(getattr(settings, "RTSP_BUFFER_SIZE", 1)))
        except Exception: pass
        if not cap.isOpened():
            result["error"] = "flux non ouvert (auth/path?)"; return result
        result["stream_open"] = True
        ok, frame = cap.read()
        result["frame_ok"] = bool(ok and frame is not None)
        if result["frame_ok"] and frame is not None:
            result["frame_shape"] = list(frame.shape)
        cap.release()
        result["ok"] = result["stream_open"] and result["frame_ok"]
        if not result["frame_ok"]: result["error"] = "aucune frame"
    except ImportError:
        result["ok"] = result["tcp_open"]; result["error"] = "opencv absent — test TCP seul"
    except Exception as e:
        result["error"] = str(e)
    return result
