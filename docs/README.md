# Documentation SentinelAI

**Version** : 2.1.0

## Structure

```
desktop/     → PyQt6 + QML
backend/     → FastAPI (/api/v1)
cpp_backend/ → ONNX C++
plugins/     → Détecteurs / règles
config/      → YAML
```

> Ancien namespace `app/` retiré. Utiliser `desktop.*` et `backend.*`.

## Docs

| Fichier | Contenu |
|---------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Architecture |
| [API.md](API.md) | REST & WebSocket |
| [PIPELINE.md](PIPELINE.md) | Pipeline vidéo |
| [STATE_MACHINE.md](STATE_MACHINE.md) | Machines d'état |
| [../README.md](../README.md) | Démarrage |

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
python run_app.py
```
