# API Interne

## Vue d'Ensemble

Ce document décrit l'API interne de SentinelAI, utilisée pour la communication entre les composants de l'application.

## Services Principaux

### StateManager

Gestionnaire d'état partagé (singleton).

```python
from app.desktop.state_manager import get_state_manager

state_manager = get_state_manager()

# Accéder à l'état
user = state_manager.get_user()
connection = state_manager.get_connection()
cameras = state_manager.get_cameras()
alerts = state_manager.get_alerts()
statistics = state_manager.get_statistics()

# Mettre à jour l'état
state_manager.set_user(user)
state_manager.set_connection(connection)
state_manager.add_camera(camera)
state_manager.add_alert(alert)

# Signaux
state_manager.user_changed.connect(callback)
state_manager.connection_changed.connect(callback)
state_manager.cameras_changed.connect(callback)
state_manager.alerts_changed.connect(callback)
```

### EventBus

Bus d'événements publish/subscribe (singleton).

```python
from app.events.event_bus import get_event_bus
from app.events.event_types import FrameReceivedEvent, DetectionResultEvent

event_bus = get_event_bus()

# Publier un événement
event = FrameReceivedEvent(camera_id="camera_1", frame=frame, frame_number=100)
event_bus.publish(event)

# S'abonner à un événement
def on_frame_received(event):
    print(f"Frame reçu: {event.camera_id}")

event_bus.subscribe(EventType.FRAME_RECEIVED, on_frame_received)

# Publication asynchrone
await event_bus.publish_async(event)
```

### CameraManager

Gestionnaire multi-caméras (singleton).

```python
from app.desktop.camera_manager import get_camera_manager

camera_manager = get_camera_manager()

# Ajouter une caméra
camera_manager.add_camera(
    camera_id="camera_1",
    source="rtsp://admin:password@192.168.1.100:554/stream",
    name="Caméra Entrée"
)

# Démarrer/arrêter la capture
camera_manager.start_capture("camera_1")
camera_manager.stop_capture("camera_1")

# Démarrer/arrêter la détection
camera_manager.start_detection("camera_1", detector=yolo_detector)
camera_manager.stop_detection("camera_1")

# Démarrer/arrêter l'enregistrement
camera_manager.start_recording("camera_1")
camera_manager.stop_recording("camera_1")

# Supprimer une caméra
camera_manager.remove_camera("camera_1")

# Signaux
camera_manager.camera_added.connect(callback)
camera_manager.camera_removed.connect(callback)
camera_manager.frame_received.connect(callback)
camera_manager.detection_result.connect(callback)
```

### AnalyticsService

Service de statistiques temps réel (singleton).

```python
from app.desktop.services.analytics_service import get_analytics_service

analytics = get_analytics_service()

# Métriques par caméra
metrics = analytics.get_camera_metrics("camera_1")
print(f"FPS: {metrics.fps}")
print(f"Détections: {metrics.detection_count}")
print(f"Alertes: {metrics.alert_count}")

# Métriques système
system_metrics = analytics.get_system_metrics()
print(f"Caméras actives: {system_metrics.active_cameras}")
print(f"Total détections: {system_metrics.total_detections}")

# Tendances
trends = analytics.get_alert_trends(hours=24)
print(f"Alertes par heure: {trends}")

# Signaux
analytics.metrics_updated.connect(callback)
analytics.camera_metrics_updated.connect(callback)
```

### ObservabilityService

Service d'observabilité (singleton).

```python
from app.desktop.observability import get_observability_service

observability = get_observability_service()

# Enregistrer une caméra pour le monitoring
observability.register_camera("camera_1")

# Mettre à jour les métriques
observability.update_camera_fps("camera_1", fps=30.0)
observability.update_camera_inference("camera_1", inference_time_ms=50.0)
observability.update_camera_queue("camera_1", queue_size=2, queue_dropped=5)
observability.update_camera_state("camera_1", state="streaming")

# Métriques système
system_metrics = observability.get_system_metrics()
print(f"CPU: {system_metrics.cpu_percent}%")
print(f"Mémoire: {system_metrics.memory_percent}%")
print(f"GPU: {system_metrics.gpu_percent}%")

# Signaux
observability.metrics_updated.connect(callback)
observability.camera_metrics_updated.connect(callback)
observability.alert_triggered.connect(callback)
```

### HealthService

Service de diagnostic (singleton).

```python
from app.desktop.health_service import get_health_service

health = get_health_service()

# État de santé d'un composant
database_health = health.get_health("database")
print(f"Base de données: {database_health.status}")

# État de santé global
overall_health = health.get_overall_health()
print(f"Santé globale: {overall_health}")

# Tous les composants
all_health = health.get_all_health()
for component, check in all_health.items():
    print(f"{component}: {check.status}")

# Exécuter un check spécifique
health.run_check("database")

# Signaux
health.health_updated.connect(callback)
health.component_health_changed.connect(callback)
```

### StorageManager

Gestionnaire de stockage (singleton).

```python
from app.storage.storage_manager import get_storage_manager, StoragePolicy, CameraQuota

storage = get_storage_manager()

# Sauvegarder un snapshot
path = storage.save_snapshot("camera_1", image_data, timestamp=datetime.now())

# Sauvegarder un enregistrement
path = storage.save_recording("camera_1", video_data, timestamp=datetime.now())

# Lister les fichiers
snapshots = storage.list_snapshots("camera_1", limit=100)
recordings = storage.list_recordings("camera_1", limit=50)

# Définir la politique de stockage
policy = StoragePolicy(
    snapshots_retention_days=7,
    recordings_retention_days=30,
    global_max_size_gb=100.0
)
storage.set_storage_policy(policy)

# Définir un quota par caméra
quota = CameraQuota(
    camera_id="camera_1",
    max_recordings=50,
    max_recordings_size_gb=10.0
)
storage.set_camera_quota("camera_1", quota)

# Nettoyage
results = storage.cleanup_by_policy()
results = storage.cleanup_camera_quota("camera_1")
```

### ConfigLoader

Chargeur de configuration (singleton).

```python
from app.core.config_loader import get_config_loader

config = get_config_loader()

# Charger toutes les configurations
config.load_all()

# Accéder aux configurations
app_config = config.get_application_config()
cameras_config = config.get_cameras_config()
ai_config = config.get_ai_config()
notifications_config = config.get_notifications_config()
storage_config = config.get_storage_config()
logging_config = config.get_logging_config()

# Accéder à une valeur spécifique
backend_host = config.get("application", "backend.host", "localhost")
model_path = config.get("ai", "yolo.default_model", "yolov8n.pt")

# Recharger une configuration
config.reload("cameras")
```

### InferenceScheduler

Ordonnanceur d'inférence (singleton).

```python
from app.ai.scheduler.inference_scheduler import get_inference_scheduler

scheduler = get_inference_scheduler()

# Backend préféré
backend = scheduler.get_preferred_backend()
print(f"Backend: {backend.value}")

# Backends disponibles
available = scheduler.get_available_backends()
print(f"Backends: {[b.value for b in available]}")

# Informations système
info = scheduler.get_system_info()
print(info)

# Créer un détecteur
detector = scheduler.create_detector(
    backend=InferenceBackend.AUTO,
    model_path="yolov8n.pt"
)

# Forcer un backend
scheduler.set_preferred_backend(InferenceBackend.CUDA)
```

### PluginManager

Gestionnaire de plugins (singleton).

```python
from plugins.plugin_manager import get_plugin_manager

plugin_manager = get_plugin_manager()

# Charger tous les plugins
plugin_manager.load_all()

# Accéder aux plugins
detectors = plugin_manager.get_all_detectors()
rules = plugin_manager.get_all_rules()
notifications = plugin_manager.get_all_notifications()

# Initialiser un plugin
plugin_manager.initialize_plugin("my_detector", "detector", config={"param": "value"})

# Arrêter un plugin
plugin_manager.shutdown_plugin("my_detector", "detector")

# Recharger un plugin
plugin_manager.reload_plugin("my_detector", "detector")
```

## Workers

### CameraWorker

Worker de capture vidéo.

```python
from app.desktop.workers.camera_worker import CameraWorker

worker = CameraWorker(
    camera_id="camera_1",
    source="rtsp://...",
    resolution=(1920, 1080),
    fps=30
)

worker.start()
worker.stop()
worker.pause()
worker.resume()

# Signaux
worker.frame_received.connect(callback)
worker.error_occurred.connect(callback)
worker.connection_status_changed.connect(callback)
```

### DetectionWorker

Worker d'inférence IA.

```python
from app.desktop.workers.detection_worker import DetectionWorker

worker = DetectionWorker(
    camera_id="camera_1",
    detector=yolo_detector
)

worker.start()
worker.stop()
worker.pause()
worker.resume()

# Signaux
worker.detection_result.connect(callback)
worker.fps_updated.connect(callback)
worker.error_occurred.connect(callback)
```

### WebSocketWorker

Worker de communication WebSocket.

```python
from app.desktop.workers.websocket_worker import WebSocketWorker

worker = WebSocketWorker(
    url="ws://localhost:8001"
)

worker.connect()
worker.disconnect()
worker.send_message({"type": "hello"})

# Signaux
worker.message_received.connect(callback)
worker.connection_status_changed.connect(callback)
worker.error_occurred.connect(callback)
```

### RecordingWorker

Worker d'enregistrement vidéo.

```python
from app.desktop.workers.recording_worker import RecordingWorker

worker = RecordingWorker(
    output_path="output.mp4",
    fps=30,
    resolution=(1920, 1080)
)

worker.start()
worker.stop()
worker.add_frame(frame)

# Signaux
worker.recording_started.connect(callback)
worker.recording_stopped.connect(callback)
worker.error_occurred.connect(callback)
```

## Détecteurs IA

### YOLODetector

```python
from app.ai.yolo_detector import YOLODetector

detector = YOLODetector(
    model_path="yolov8n.pt",
    device="cuda"  # cpu, cuda, auto
)

detections = detector.detect(frame)
# [
#     DetectionResult(class_id=0, class_name="person", confidence=0.95, bbox=[x, y, w, h]),
#     ...
# ]
```

### MediaPipePoseDetector

```python
from app.ai.mediapipe_detector import MediaPipePoseDetector

detector = MediaPipePoseDetector(
    model_complexity=1,
    min_detection_confidence=0.5
)

landmarks = detector.detect(frame)
# List of landmarks
```

### MediaPipeFallDetector

```python
from app.ai.mediapipe_detector import MediaPipeFallDetector

detector = MediaPipeFallDetector(
    orientation_threshold=60,
    velocity_threshold=2.0
)

detections = detector.detect(frame)
# List of fall detections
```

## Moteur de Règles

### IntrusionRuleEngine

```python
from app.ai.rules.intrusion import IntrusionRuleEngine, Zone
from app.events.event_bus import get_event_bus

event_bus = get_event_bus()
engine = IntrusionRuleEngine(event_bus)

# Ajouter une zone
zone = Zone(
    id="zone_1",
    name="Entrée",
    polygon=[[100, 100], [300, 100], [300, 300], [100, 300]],
    max_persons=0
)
engine.add_zone(zone)

# Traiter les détections
engine.process_detections(detections, context={"camera_id": "camera_1", "frame": frame})
```

### FallDetectionRuleEngine

```python
from app.ai.rules.fall_detection import FallDetectionRuleEngine

engine = FallDetectionRuleEngine(event_bus)

engine.set_confidence_threshold(0.7)
engine.set_velocity_threshold(2.0)
engine.set_orientation_threshold(60)

engine.process_detections(detections, context={"camera_id": "camera_1"})
```

### LoiteringRuleEngine

```python
from app.ai.rules.loitering import LoiteringRuleEngine

engine = LoiteringRuleEngine(event_bus)

engine.set_loitering_threshold(60)  # secondes
engine.set_movement_threshold(50.0)  # pixels

engine.process_detections(detections, context={"camera_id": "camera_1", "zone_id": "zone_1"})
```

### CrowdingRuleEngine

```python
from app.ai.rules.crowding import CrowdingRuleEngine

engine = CrowdingRuleEngine(event_bus)

engine.set_crowding_threshold(5)  # personnes
engine.set_critical_threshold(10)  # personnes
engine.set_duration_threshold(30)  # secondes

engine.process_detections(detections, context={"camera_id": "camera_1", "zone_id": "zone_1"})
```

## Version

```python
from app.version import get_version, get_full_version, get_user_agent

version = get_version()
print(f"Version: {version.app_version}")
print(f"Build: {version.build_number}")

full_version = get_full_version()
print(f"Full version: {full_version}")

user_agent = get_user_agent()
print(f"User agent: {user_agent}")
```

## Exceptions

```python
from app.core.exceptions import (
    CameraException,
    StorageException,
    ConfigException,
    DatabaseException,
    AIServiceException
)

try:
    # Code
except CameraException as e:
    print(f"Erreur caméra: {e}")
except StorageException as e:
    print(f"Erreur stockage: {e}")
except ConfigException as e:
    print(f"Erreur configuration: {e}")
except DatabaseException as e:
    print(f"Erreur base de données: {e}")
except AIServiceException as e:
    print(f"Erreur IA: {e}")
```

## Logger

```python
from app.core.logger import get_logger

logger = get_logger(__name__)

logger.debug("Message debug")
logger.info("Message info")
logger.warning("Message warning")
logger.error("Message error")
logger.critical("Message critical")
```
