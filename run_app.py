#!/usr/bin/env python3
"""
SentinelAI — portable entry point (Linux + Windows).

Usage:
    python run_app.py

Requires: Python 3.10+, PyQt6
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Portable path / environment setup (must run before Qt imports)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Avoid OpenMP / MKL DLL clashes on Windows (torch, openvino, etc.)
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
# Prefer Basic style so QML Controls look identical on Linux & Windows
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")
# High-DPI
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")


def main() -> int:
    from PyQt6.QtCore import Qt, QCoreApplication
    from PyQt6.QtGui import QFont, QIcon
    from app.desktop.application import Application

    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

    app = Application()
    app.setApplicationName("SentinelAI")
    app.setApplicationVersion("4.2.1")
    app.setOrganizationName("Axyris Security")
    app.setOrganizationDomain("axyris.security")

    if sys.platform == "win32":
        app.setFont(QFont("Segoe UI", 10))
    elif sys.platform == "darwin":
        app.setFont(QFont("SF Pro Text", 10))
    else:
        app.setFont(QFont("Inter", 10))

    icon_path = ROOT / "app" / "desktop" / "assets" / "icons" / "shield.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    print(f"SentinelAI 4.2.1-stable  |  Python {sys.version.split()[0]}  |  {sys.platform}")
    print("Starting QML engine…")

    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[FATAL] {exc}", file=sys.stderr)
        raise
