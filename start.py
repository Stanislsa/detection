#!/usr/bin/env python3
"""
SentinelAI — lancement unique (backend puis frontend).

Usage:
    python start.py
    python start.py --backend-only
    python start.py --frontend-only
    python start.py --port 8000 --no-reload
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
HEALTH_PATH = "/api/v1/health/"
MAX_WAIT_S = 60


def _backend_url(host: str, port: int) -> str:
    return f"http://{host}:{port}"


def wait_for_backend(base: str, timeout: float = MAX_WAIT_S) -> bool:
    url = base.rstrip("/") + HEALTH_PATH
    deadline = time.time() + timeout
    last_err = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if 200 <= resp.status < 300:
                    return True
        except Exception as exc:
            last_err = str(exc)
        time.sleep(0.5)
    print(f"[start] Backend health timeout ({url}): {last_err}", file=sys.stderr)
    return False


def start_backend(host: str, port: int, reload: bool) -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("SECRET_KEY", "dev-only-change-me-sentinelai-2026-insecure")
    env["BACKEND_URL"] = _backend_url(host, port)
    cmd = [
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", host,
        "--port", str(port),
    ]
    if reload:
        cmd.append("--reload")
    print(f"[start] Backend → {' '.join(cmd)}")
    return subprocess.Popen(cmd, cwd=str(ROOT), env=env, stdout=sys.stdout, stderr=sys.stderr)


def start_frontend(host: str, port: int) -> int:
    env = os.environ.copy()
    env["BACKEND_URL"] = _backend_url(host, port)
    print(f"[start] Frontend → python run_app.py  (BACKEND_URL={env['BACKEND_URL']})")
    return subprocess.call([sys.executable, str(ROOT / "run_app.py")], cwd=str(ROOT), env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="SentinelAI launcher (backend then frontend)")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-reload", action="store_true")
    parser.add_argument("--backend-only", action="store_true")
    parser.add_argument("--frontend-only", action="store_true")
    parser.add_argument("--wait", type=float, default=MAX_WAIT_S)
    args = parser.parse_args()

    base = _backend_url(args.host, args.port)
    os.environ["BACKEND_URL"] = base
    backend_proc: subprocess.Popen | None = None

    def shutdown(*_a):
        if backend_proc and backend_proc.poll() is None:
            print("\n[start] Arrêt du backend…")
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                backend_proc.kill()

    signal.signal(signal.SIGINT, lambda *_: (shutdown(), sys.exit(130)))
    signal.signal(signal.SIGTERM, lambda *_: (shutdown(), sys.exit(143)))

    try:
        if not args.frontend_only:
            backend_proc = start_backend(args.host, args.port, reload=not args.no_reload)
            print(f"[start] Attente health {base}{HEALTH_PATH} …")
            if not wait_for_backend(base, timeout=args.wait):
                shutdown()
                return 1
            print("[start] Backend OK")
            if args.backend_only:
                print("[start] --backend-only : Ctrl+C pour arrêter")
                return backend_proc.wait()
        return start_frontend(args.host, args.port)
    finally:
        shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
