# Architecture SentinelAI

## Vue d'Ensemble

SentinelAI est une application de vidéosurveillance multi-caméras avec détection IA en temps réel, construite avec PyQt6 et Python.

## Composants Principaux

### 1. Interface Utilisateur (PyQt6)

```
app/desktop/
├── main_window.py         # Fenêtre principale
├── pages/                 # Pages (Caméras, Alertes, Utilisateurs)
│   ├── cameras.py         # Gestion des caméras
│   ├── alerts.py          # Gestion des alertes
│   └── users.py           # Gestion des utilisateurs
└── widgets/               # Widgets personnalisés
```

### 2. Couche Services

```
app/desktop/services/
└── analytics_service.py   # Statistiques temps réel
```

### 3. Workers (QThread)

```
app/desktop/workers/
├── base_worker.py         # Worker de base
├── camera_worker.py       # Capture vidéo
├── detection_worker.py    # Inférence IA
├── websocket_worker.py    # Communication WebSocket
└── recording_worker.py    # Enregistrement vidéo
```

### 4. Pipeline Vidéo

```
app/desktop/pipeline/
├── stages.py              # Étapes du pipeline
├── video_pipeline.py      # Orchestration
└── bounded_queue.py       # Files d'attente bornées
```

### 5. Gestion Multi-Caméras

```
app/desktop/
├── camera_manager.py      # Gestionnaire multi-caméras
├── camera_state_machine.py  # Machine à états
└── state_manager.py       # État partagé
```

### 6. Intelligence Artificielle

```
app/ai/
├── base_detector.py       # Interface détecteurs
├── yolo_detector.py       # YOLO (Ultralytics)
├── mediapipe_detector.py  # MediaPipe
├── classifier.py          # Classificateur PyTorch
├── scheduler/             # Ordonnanceur d'inférence
│   └── inference_scheduler.py
└── rules/                 # Moteur de règles
    ├── base_rule.py
    ├── intrusion.py
    ├── fall_detection.py
    ├── loitering.py
    └── crowding.py
```

### 7. Bus d'Événements

```
app/events/
├── event_types.py         # Types d'événements
├── event_bus.py           # Bus publish/subscribe
└── handlers.py            # Handlers d'événements
```

### 8. Stockage

```
app/storage/
└── storage_manager.py     # Gestionnaire centralisé
```

### 9. Base de Données

```
app/database/
└── __init__.py            # Modèles SQLAlchemy
```

### 10. Fonctionnalités Transversales

```
app/core/
├── constants.py           # Constantes globales
├── logger.py              # Logger centralisé
├── exceptions.py          # Exceptions personnalisées
├── settings.py           # Configuration persistante
└── config_loader.py       # Chargeur de configuration YAML
```

### 11. Observabilité

```
app/desktop/
├── observability.py       # Service d'observabilité
└── health_service.py      # Service de diagnostic
```

### 12. Plugins

```
plugins/
├── plugin_manager.py      # Gestionnaire de plugins
├── detectors/             # Détecteurs personnalisés
├── rules/                 # Règles personnalisées
└── notifications/         # Canaux de notification personnalisés
```

## Flux de Données

### Flux Vidéo

```
RTSP/Webcam → CameraWorker → FrameQueue → DetectionWorker → RuleEngine → AlertService → EventBus → UI/Recording/Notifications
```

### Flux d'Événements

```
EventBus → Handlers → UI Updates / Database / WebSocket / Notifications
```

## Patterns Utilisés

- **Singleton** : StateManager, EventBus, CameraManager, AnalyticsService, ObservabilityService, HealthService
- **Observer** : PyQt6 signals/slots, EventBus publish/subscribe
- **Strategy** : InferenceScheduler (sélection backend IA)
- **Chain of Responsibility** : Pipeline vidéo (étapes enchaînées)
- **State Machine** : CameraStateMachine
- **Factory** : PluginManager (création de plugins)
- **Repository** : StorageManager (accès stockage)

## Séparation des Responsabilités

- **UI** : Affichage et interaction utilisateur
- **Services** : Logique métier et traitement
- **Workers** : Opérations asynchrones
- **AI** : Inférence et règles
- **Events** : Communication entre composants
- **Storage** : Persistance des données
- **Core** : Fonctionnalités partagées

## Extensibilité

- **Plugins** : Ajout de détecteurs, règles et notifications sans modifier le cœur
- **Configuration** : Fichiers YAML modifiables sans recompilation
- **Backend IA** : Sélection automatique CPU/OpenVINO/CUDA/DirectML
- **Règles** : Configuration YAML ou plugins personnalisés
