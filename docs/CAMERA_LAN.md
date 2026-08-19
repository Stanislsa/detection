# Réseau local caméras (RTSP)
Voir aussi `scripts/test_rtsp.py` et `POST /api/v1/cameras/test-rtsp`.
- Même subnet/VLAN, IP fixes, Ethernet recommandé
- URL: `rtsp://USER:PASS@IP:554/path`
- Env: `RTSP_TRANSPORT=tcp`, `RTSP_BUFFER_SIZE=1`, `DETECTION_FPS=5`
