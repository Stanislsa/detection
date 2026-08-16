#!/usr/bin/env python3
"""Vérifie imports critiques et alignement des routes."""
from __future__ import annotations
import ast, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SECRET_KEY", "verify-only")

def ok(msg): print(f"  OK  {msg}")
def fail(msg): print(f"  FAIL {msg}"); return 1

def main() -> int:
    errors = 0
    print("=== Syntaxe ===")
    for p in ROOT.rglob("*.py"):
        if ".git" in str(p): continue
        try: ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as e:
            errors += fail(f"{p.relative_to(ROOT)}: {e}")
    if not errors: ok("tous les .py")

    print("=== Modules ===")
    for mod in ["desktop.services.api_client", "backend.core.config", "backend.core.exceptions", "backend.api.router"]:
        try:
            __import__(mod); ok(mod)
        except Exception as e:
            errors += fail(f"{mod}: {e}")

    print("=== FastAPI ===")
    try:
        from backend.main import app
        paths = set(app.openapi().get("paths", {}))
        for need in ["/api/v1/auth/login", "/api/v1/cameras/", "/api/v1/health/", "/metrics"]:
            if any(need.rstrip("/") in p for p in paths) or need in paths: ok(need)
            else: errors += fail(f"missing {need}")
    except Exception as e:
        errors += fail(f"backend.main: {e}")

    print("=== ApiClient ===")
    try:
        from desktop.services.api_client import ApiClient
        c = ApiClient()
        ok(f"login = {c._url('/auth/login')}")
        ok(f"cameras = {c._url('/cameras')}")
    except Exception as e:
        errors += fail(str(e))

    print("\nRésultat:", f"{errors} problème(s)" if errors else "connexions OK")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
