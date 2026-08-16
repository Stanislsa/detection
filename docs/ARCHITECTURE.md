# Architecture SentinelAI

**Stack** : Python · PyQt6/QML · FastAPI · SQLAlchemy · C++ ONNX · YOLO/OpenVINO · Prometheus

## Desktop (`desktop/`)
`application.py`, `controllers/`, `services/` (api_client…), `workers/`, `qml/`

## Backend (`backend/`)
`main.py`, `api/endpoints/`, `database/`, `security/`, `ai/`, `core/` (exceptions, prometheus_metrics)

## Flux
```
QML ↔ Controllers ↔ Services ↔ ApiClient ↔ FastAPI /api/v1
                                         ↔ WebSocket /ws
                                         ↔ Prometheus /metrics
```

Auth : `POST /api/v1/auth/login` → JWT. Offline démo : admin / azerty.
