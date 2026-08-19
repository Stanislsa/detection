#!/usr/bin/env python3
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.services.camera_network import probe_rtsp
if len(sys.argv) < 2:
    print('Usage: python scripts/test_rtsp.py "rtsp://..."'); raise SystemExit(1)
r = probe_rtsp(sys.argv[1]); print(json.dumps(r, indent=2, ensure_ascii=False))
raise SystemExit(0 if r.get("ok") else 2)
