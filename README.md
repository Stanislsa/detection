# SentinelAI 2.1.0
PyQt6/QML · FastAPI · Prometheus · YOLO/OpenVINO

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
python run_app.py
```
Backend: admin / admin123 · Offline: admin / azerty  
API: /api/v1 · Metrics: /metrics · Docs: /api/docs

## Lancement unique (recommandé)

```bash
pip install -r requirements.txt
python start.py
```

Ordre : **1. Backend** → **2. Health check** → **3. Frontend**

```bash
python start.py --backend-only
python start.py --frontend-only
./start.sh
python scripts/verify_connections.py
```


## Apprentissage (vidéos → tri)

Placez les vidéos dans `données/vidéo/` puis :

```bash
python start_train.py
```

Pipeline : fragmentation → **21 indicateurs** → stockage `data/features/` → tri normal/urgent/critique → **DecisionTree + RandomForest**.

Voir `docs/INDICATORS_AND_TREES.md`.
