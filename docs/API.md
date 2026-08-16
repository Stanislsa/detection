# API SentinelAI

Base : `http://127.0.0.1:8000/api/v1` · Swagger : `/api/docs`

| Groupe | Routes |
|--------|--------|
| Auth | `/auth/login`, `/auth/refresh`, `/auth/me` |
| Ressources | `/cameras`, `/alerts`, `/falls`, `/users`, `/persons`, `/dashboard` |
| System | `/system/metrics`, `/system/info` |
| AI | `/ai/models`, `POST /ai/train` |
| Telegram | `/telegram/config`, `/test`, `/status` |
| Metrics | `/metrics` (Prometheus) |
| WS | `/ws` |

Client desktop : `from desktop.services.api_client import get_api_client`

Erreurs :
```json
{"error": {"code": "NOT_FOUND", "message": "..."}, "path": "...", "method": "GET"}
```
