# Pipeline Vidéo

## Vue d'Ensemble

Le pipeline vidéo définit explicitement le flux de traitement des frames vidéo, de la capture à la génération d'alertes.

## Architecture du Pipeline

```
RTSP/Webcam
      │
      ▼
CaptureWorker
      │
      ▼
Frame Buffer (BoundedQueue)
      │
      ▼
DetectionWorker (IA)
      │
      ▼
Rule Engine (Évaluation des règles)
      │
      ▼
Alert Service (Génération d'alertes)
      │
      ▼
Event Bus (Publication)
      │
      ├── Dashboard (UI)
      ├── Recording (Stockage)
      ├── Notification (Alertes)
      └── Database (Persistance)
```

## Étapes du Pipeline

### 1. CaptureStage

**Responsabilité** : Capturer les frames depuis la source (RTSP, webcam, fichier).

**Entrée** : Source vidéo (URL, index webcam, chemin fichier)

**Sortie** : Frame numpy array + métadonnées

**Métriques** :
- FPS de capture
- Nombre de frames capturées
- Erreurs de connexion

### 2. BufferStage

**Responsabilité** : Gérer un buffer circulaire des frames récents.

**Configuration** :
- Taille du buffer (défaut: 30 frames)
- Politique de suppression (oldest, newest, none)

**Métriques** :
- Taille actuelle du buffer
- Taux de suppression (drop rate)
- Temps d'attente moyen

### 3. DetectionStage

**Responsabilité** : Exécuter l'inférence IA sur le frame.

**Backend** : Sélection automatique via InferenceScheduler (CPU/OpenVINO/CUDA/DirectML)

**Modèles** :
- YOLO (Ultralytics)
- MediaPipe (pose estimation)
- Classificateur PyTorch

**Métriques** :
- Temps d'inférence (ms)
- FPS de détection
- Nombre de détections

### 4. RuleEngineStage

**Responsabilité** : Évaluer les règles sur les détections.

**Règles disponibles** :
- Intrusion (zones interdites)
- Fall detection (chutes)
- Loitering (stationnement prolongé)
- Crowding (foule)

**Métriques** :
- Règles déclenchées
- Temps d'évaluation

### 5. AlertStage

**Responsabilité** : Générer les alertes basées sur les règles déclenchées.

**Types d'alertes** :
- Intrusion
- Fall
- Loitering
- Crowding
- Movement

**Métriques** :
- Alertes générées
- Sévérité des alertes

### 6. EventBusStage

**Responsabilité** : Publier les événements sur le bus d'événements.

**Événements publiés** :
- FrameReceivedEvent
- DetectionResultEvent
- AlertGeneratedEvent

**Métriques** :
- Événements publiqués
- Abonnés notifiés

### 7. RecordingStage

**Responsabilité** : Enregistrer les frames si nécessaire.

**Déclencheurs** :
- Enregistrement continu
- Enregistrement sur mouvement
- Enregistrement sur alerte

**Métriques** :
- Frames enregistrées
- Taille des fichiers
- Durée d'enregistrement

### 8. NotificationStage

**Responsabilité** : Envoyer les notifications aux opérateurs.

**Canaux** :
- Desktop (notifications in-app)
- Email
- Telegram
- Webhook

**Métriques** :
- Notifications envoyées
- Canaux utilisés

## Configuration

### Configuration du Pipeline

```python
from app.desktop.pipeline.video_pipeline import PipelineConfig, VideoPipeline

config = PipelineConfig(
    buffer_size=30,
    enable_detection=True,
    enable_recording=False,
    enable_notifications=True,
    enable_event_bus=True
)

pipeline = VideoPipeline(camera_id="camera_1", config=config)
```

### Configuration des Files d'Attente

```python
from app.desktop.pipeline.bounded_queue import BoundedQueue

queue = BoundedQueue(
    max_size=3,
    drop_policy="oldest"  # oldest, newest, none
)
```

## Métriques

### Métriques par Étape

Chaque étape expose des métriques :

```python
metrics = pipeline.get_metrics()
# {
#     "camera_id": "camera_1",
#     "frame_count": 1000,
#     "error_count": 5,
#     "error_rate": 0.005,
#     "stages": {
#         "Buffer": {...},
#         "Detection": {...},
#         "RuleEngine": {...},
#         ...
#     }
# }
```

### Métriques de Files d'Attente

```python
metrics = queue.get_metrics()
# {
#     "total_enqueued": 1000,
#     "total_dequeued": 995,
#     "total_dropped": 5,
#     "current_size": 2,
#     "max_size": 3,
#     "avg_wait_time_ms": 15.5,
#     "peak_size": 3
# }
```

## Optimisation

### Réduction de la Latence

1. **Réduire la taille du buffer** : `buffer_size=2` ou `3`
2. **Politique de suppression** : `drop_policy="oldest"`
3. **Backend IA optimal** : CUDA > OpenVINO > CPU

### Augmentation du Débit

1. **Backend GPU** : Utiliser CUDA si disponible
2. **Modèle léger** : YOLOv8n au lieu de YOLOv8l
3. **Workers multiples** : Un worker par caméra

### Gestion de la Charge

1. **Files bornées** : Éviter l'accumulation
2. **Suppression automatique** : Frames anciennes supprimées
3. **Métriques de drop** : Surveillance du taux de suppression
