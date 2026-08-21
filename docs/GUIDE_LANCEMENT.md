# Guide de lancement — SentinelAI

Système intelligent de détection de chutes (PyQt6/QML · FastAPI · YOLO + MediaPipe · ML)

---

## 1. État de la partie apprentissage & backend

### Apprentissage modèle — présent

| Élément | Statut | Emplacement |
|---------|--------|-------------|
| Fragmentation vidéos | ✅ | `ml/fragment.py` |
| Features image (21) | ✅ | `ml/features.py` |
| Features squelette MediaPipe | ✅ | `ml/skeleton_features.py` |
| Checklist données (10 points) | ✅ | `ml/data_checklist.py` |
| EDA + fuites + visualisations | ✅ | `ml/eda.py`, `ml/leakage.py`, `ml/visualize_leakage.py` |
| Prétraitement ordonné | ✅ | `ml/preprocess.py` |
| sklearn Pipeline anti-fuite | ✅ | `ml/sklearn_pipeline.py` |
| Optimisation hyperparams multi-pipelines | ✅ | `ml/pipeline_optimize.py` |
| Courbes d’apprentissage | ✅ | `ml/learning_curves.py` |
| Rééquilibrage classes | ✅ | `ml/imbalance.py` |
| Sauvegarde versionnée | ✅ | `data/models/pipelines/` |
| Tri normal / urgent / critique | ✅ | `ml/triage.py`, `ml/trees.py` |

### Améliorations backend — présentes

| Élément | Statut | Emplacement |
|---------|--------|-------------|
| FastAPI unifié | ✅ | `backend/main.py` |
| Auth JWT + MFA admin | ✅ | `backend/security/` |
| YOLO + MediaPipe hybrid | ✅ | `backend/ai/manager.py`, `yolo.py`, `mediapipe.py` |
| Critères de chute formalisés | ✅ | `backend/ai/fall_criteria.py` |
| Score de gravité | ✅ | `backend/services/severity_engine.py` |
| DetectionPipelineService | ✅ | `backend/services/detection_pipeline.py` |
| Prometheus / métriques | ✅ | `backend/core/prometheus_metrics.py` |
| RTSP / réseau caméras | ✅ | `backend/services/camera_network.py` (si présent) |
| Notifications Telegram | ✅ | `backend/notifications/` |

### Frontend desktop

| Élément | Statut |
|---------|--------|
| PyQt6 + QML | ✅ `desktop/`, `run_app.py` |
| Connexion API (`BACKEND_URL`) | ✅ |
| Lancement joint backend→frontend | ✅ `start.py` |

---

## 2. Structure du projet

```
detection/
├── start.py                 # Backend puis Frontend (recommandé)
├── start.sh                 # Wrapper shell
├── start_train.py           # Apprentissage classique
├── run_app.py               # Frontend seul (PyQt6/QML)
├── requirements.txt
├── .env.example
│
├── backend/                 # API FastAPI
│   ├── main.py              # Point d’entrée uvicorn
│   ├── api/                 # Routes / endpoints
│   ├── ai/                  # YOLO, MediaPipe, fall_criteria, manager
│   ├── services/            # detection_pipeline, severity_engine, …
│   ├── security/            # Auth, MFA, crypto
│   ├── database/            # SQLAlchemy / SQLite
│   ├── notifications/       # Telegram, email sim
│   └── core/                # config, logger, prometheus
│
├── desktop/                 # Frontend
│   ├── application.py       # Application PyQt6
│   ├── qml/                 # Pages QML
│   ├── controllers/         # Bridge Python ↔ QML
│   └── services/            # ApiClient
│
├── ml/                      # Apprentissage
│   ├── pipeline.py          # Orchestration train
│   ├── preprocess.py        # Prétraitement ordonné
│   ├── sklearn_pipeline.py  # Pipeline sklearn
│   ├── pipeline_optimize.py # Hyperparams + variantes
│   ├── skeleton_features.py
│   ├── learning_curves.py
│   └── …
│
├── scripts/
│   ├── run_preprocess_ml.py
│   ├── optimize_pipeline.py
│   ├── plot_learning_curves.py
│   ├── run_data_qa.py
│   ├── verify_connections.py
│   └── test_rtsp.py
│
├── docs/                    # Documentation
├── data/                    # Généré : features, models, db, fragments
└── données/vidéo/           # Vidéos source pour l’apprentissage
```

---

## 3. Prérequis

```bash
# Python 3.10+
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
# Optionnel ML / viz
pip install matplotlib imbalanced-learn

# Copier la config
cp .env.example .env
# Éditer SECRET_KEY, DATABASE_URL, BACKEND_URL, TELEGRAM_* si besoin
```

**Comptes démo**
- Connecté backend : `admin` / `admin123` (ou selon seed)
- Mode offline UI : `admin` / `azerty`

---

## 4. Apprentissage du modèle

### 4.1 Préparer les vidéos

```text
données/vidéo/
  ├── chute1.mp4
  ├── normal_marche.mp4
  └── …
```

### 4.2 Commandes d’apprentissage

```bash
# Pipeline classique (fragment → features → tri → arbres)
python start_train.py

# Avec options
python -m ml.pipeline --video-dir données/vidéo
python -m ml.pipeline --skip-hyper          # plus rapide
python -m ml.pipeline --ordered-preprocess  # preprocess + sklearn Pipeline

# Prétraitement ordonné + modèle (recommandé)
python scripts/run_preprocess_ml.py
python scripts/run_preprocess_ml.py --skip-hyper

# Optimisation multi-pipelines + sauvegarde versionnée
python scripts/optimize_pipeline.py --n-iter 20
python scripts/optimize_pipeline.py --list

# QA données seule (checklist + EDA + fuites)
python scripts/run_data_qa.py

# Courbes d’apprentissage
python scripts/plot_learning_curves.py
python scripts/plot_learning_curves.py --from-saved
```

### 4.3 Artefacts générés

```text
data/fragments/          # clips
data/features/           # indicateurs + table CSV
data/models/
  severity_trees.joblib
  sklearn_pipeline.joblib
  pipelines/             # versions datées
  plots/                 # fuites, balance, learning curves
  *.json                 # logs checklist, EDA, hyperparams
```

---

## 5. Lancement Backend

### 5.1 Backend total (développement — tout inclus)

```bash
# Via lanceur unique (attend le health puis peut lancer le front)
python start.py --backend-only

# Ou directement uvicorn
export SECRET_KEY="dev-only-change-me"
export ENVIRONMENT=development
export DEBUG=true
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- API : http://127.0.0.1:8000/api/v1  
- Docs : http://127.0.0.1:8000/api/docs  
- Health : http://127.0.0.1:8000/api/v1/health/  
- Metrics : http://127.0.0.1:8000/metrics  

### 5.2 Backend IA (focus détection)

Le backend charge automatiquement les modèles au démarrage (`ai_manager` dans `lifespan`).

```bash
# S’assurer que les poids / pipeline ML existent
python start_train.py          # ou scripts/run_preprocess_ml.py

# Puis backend (YOLO + MediaPipe + fall_criteria + severity)
ENVIRONMENT=development uvicorn backend.main:app --port 8000 --reload
```

Endpoints utiles (selon routes) : détection, caméras, alertes, KPI dashboard.

Vérifier :

```bash
python scripts/verify_connections.py
curl -s http://127.0.0.1:8000/api/v1/health/
```

### 5.3 Backend en test

```bash
export ENVIRONMENT=development
export DEBUG=true
export DATABASE_URL="sqlite:///data/db/sentinel_ai_test.db"
export SECRET_KEY="test-secret-key"

# Health + tests manuels
uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload

# Vérifications
python scripts/run_data_qa.py
python scripts/verify_connections.py
python scripts/test_rtsp.py   # si caméra RTSP de test
```

### 5.4 Backend en production

```bash
# .env production
SECRET_KEY=<clé-longue-aléatoire>
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=sqlite:///data/db/sentinel_ai.db   # ou PostgreSQL
BACKEND_URL=http://0.0.0.0:8000
# TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID si alertes

uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 2 \
  --no-access-log
```

Recommandations prod :
- Ne pas utiliser `--reload`
- HTTPS via reverse proxy (nginx / Caddy)
- Rotation `SECRET_KEY` et clés vidéo AES
- MFA admin activé
- Sauvegardes `data/db/` et `data/models/`

### 5.5 Paramétrage C++ / accélération native (ONNX, OpenVINO)

Le cœur temps réel est en **Python** (OpenCV, Ultralytics YOLO, MediaPipe, OpenVINO).  
Un module **C++** optionnel peut accélérer l’inférence ONNX Runtime.

**Si vous ajoutez un binding C++** (non obligatoire pour démarrer) :

```bash
# Exemple structure recommandée
native/
  CMakeLists.txt
  src/onnx_infer.cpp
  include/onnx_infer.h

# Build Linux
mkdir -p native/build && cd native/build
cmake .. -DONNXRUNTIME_ROOT=/usr/local \
         -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
# Produit : libonnx_infer.so → placer dans backend/ai/native/
```

Exemple `CMakeLists.txt` minimal :

```cmake
cmake_minimum_required(VERSION 3.16)
project(sentinel_onnx)
find_package(onnxruntime REQUIRED)  # ou chemin manuel
add_library(onnx_infer SHARED src/onnx_infer.cpp)
target_link_libraries(onnx_infer onnxruntime)
```

Variables d’environnement utiles :

```bash
export OPENVINO_DEVICE=CPU          # ou GPU
export YOLO_MODEL_PATH=data/models/yolov8n.pt
export MEDIAPIPE_COMPLEXITY=1
export ONNX_MODEL_PATH=data/models/fall.onnx
```

Sans C++ compilé, le backend utilise les backends Python (YOLO/OpenVINO) déjà intégrés.

---

## 6. Lancement Frontend

### 6.1 Frontend seul (QML + PyQt6)

```bash
export BACKEND_URL=http://127.0.0.1:8000
python run_app.py
```

- UI QML dans `desktop/qml/`
- Contrôleurs Python dans `desktop/controllers/`
- Client HTTP : `desktop/services/` (ApiClient)

### 6.2 Frontend connecté au backend

1. Démarrer le backend (port 8000)
2. Vérifier health
3. Lancer le front avec la même URL

```bash
# Terminal 1
python start.py --backend-only

# Terminal 2
export BACKEND_URL=http://127.0.0.1:8000
python run_app.py
```

Ou **une seule commande** (ordre backend → health → front) :

```bash
python start.py
# équivalent
./start.sh
```

Options :

```bash
python start.py --port 8000
python start.py --backend-only
python start.py --frontend-only
python start.py --no-reload
```

---

## 7. Ordre recommandé (apprentissage → app)

```bash
# 0. Environnement
source .venv/bin/activate
cp .env.example .env
pip install -r requirements.txt

# 1. Placer les vidéos
mkdir -p données/vidéo
# copier les .mp4 / .avi

# 2. Apprentissage
python start_train.py
# ou (meilleure qualité)
python scripts/run_preprocess_ml.py
python scripts/optimize_pipeline.py --n-iter 16

# 3. Vérifier artefacts
ls data/models/*.joblib

# 4. Lancer backend + frontend ensemble
python start.py
```

---

## 8. Récapitulatif des commandes

| Objectif | Commande |
|---------|----------|
| **App complète** | `python start.py` |
| Backend seul | `python start.py --backend-only` |
| Frontend seul | `python start.py --frontend-only` ou `python run_app.py` |
| Train classique | `python start_train.py` |
| Train + preprocess sklearn | `python scripts/run_preprocess_ml.py` |
| Optim hyperparams | `python scripts/optimize_pipeline.py` |
| QA données | `python scripts/run_data_qa.py` |
| Courbes apprentissage | `python scripts/plot_learning_curves.py` |
| Vérifier connexions | `python scripts/verify_connections.py` |
| Backend prod | `ENVIRONMENT=production uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2` |
| Backend test | `DATABASE_URL=sqlite:///data/db/test.db uvicorn backend.main:app --port 8001` |

---

## 9. Dépannage rapide

| Problème | Action |
|----------|--------|
| Backend health timeout | Vérifier port 8000 libre, logs uvicorn, `SECRET_KEY` |
| Frontend sans données | `BACKEND_URL` correct ? CORS / backend démarré ? |
| Train « no videos » | Fichiers dans `données/vidéo/` (accents / chemin) |
| MediaPipe / YOLO manquant | `pip install mediapipe ultralytics opencv-python` |
| F1 bas | Plus de vidéos par classe ; `scripts/optimize_pipeline.py` |
| QML style cassé | `QT_QUICK_CONTROLS_STYLE=Basic` (déjà dans `start.py`) |

---

## 10. Liens docs internes

- Architecture : `docs/ARCHITECTURE.md`
- API : `docs/API.md`
- Pipeline ML : `docs/PIPELINE.md`, `docs/LEARNING_SKELETON.md`
- IA chute : `docs/IA_YOLO_MEDIAPIPE.md`, `docs/IA_CRITERES_CHUTE.md`
- CDC addendum : `docs/CDC_ADDENDUM_COMPLET.md`
- Caméras LAN : `docs/CAMERA_LAN.md`

---

*SentinelAI — guide de lancement unifié*
