"""
Service d'analytique pour les statistiques temps réel et historiques.
Calcule et agrège les métriques de performance du système.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from app.desktop.models.alert import Alert, AlertSeverity, AlertType
from app.desktop.models.camera import Camera, CameraStatus
from app.desktop.camera_manager import CameraManager, CameraState
from app.events.event_bus import EventBus
from app.events.event_types import EventType, Event, DetectionResultEvent, AlertGeneratedEvent
from app.core.logger import get_logger


class TimeRange(Enum):
    """Plages de temps pour les statistiques."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class CameraMetrics:
    """Métriques pour une caméra."""
    camera_id: str
    camera_name: str
    
    # Détections
    total_detections: int = 0
    fall_detections: int = 0
    intrusion_detections: int = 0
    movement_detections: int = 0
    
    # Alertes
    total_alerts: int = 0
    critical_alerts: int = 0
    high_alerts: int = 0
    medium_alerts: int = 0
    low_alerts: int = 0
    
    # Performance
    avg_detection_time_ms: float = 0.0
    avg_fps: float = 0.0
    uptime_seconds: float = 0.0
    downtime_seconds: float = 0.0
    
    # Qualité
    false_positive_rate: float = 0.0
    detection_rate: float = 0.0
    
    # Timestamps
    last_detection: Optional[datetime] = None
    last_alert: Optional[datetime] = None
    last_online: Optional[datetime] = None
    last_offline: Optional[datetime] = None


@dataclass
class SystemMetrics:
    """Métriques système globales."""
    # Caméras
    total_cameras: int = 0
    online_cameras: int = 0
    offline_cameras: int = 0
    active_cameras: int = 0
    
    # Alertes
    total_alerts: int = 0
    critical_alerts: int = 0
    high_alerts: int = 0
    medium_alerts: int = 0
    low_alerts: int = 0
    resolved_alerts: int = 0
    
    # Détections
    total_detections: int = 0
    fall_detections: int = 0
    intrusion_detections: int = 0
    movement_detections: int = 0
    
    # Performance
    avg_detection_time_ms: float = 0.0
    avg_fps: float = 0.0
    total_uptime_seconds: float = 0.0
    
    # Stockage
    storage_used_gb: float = 0.0
    recording_hours: float = 0.0
    
    # Timestamp
    last_updated: datetime = field(default_factory=datetime.now)


class AnalyticsService(QObject):
    """
    Service d'analytique pour les statistiques temps réel.
    Calcule et agrège les métriques de performance.
    """
    
    # Signaux
    metrics_updated = pyqtSignal(object)  # SystemMetrics
    camera_metrics_updated = pyqtSignal(str, object)  # camera_id, CameraMetrics
    alert_trend_updated = pyqtSignal(object)  # trend data
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._camera_manager = CameraManager()
            self._event_bus = EventBus()
            self._logger = get_logger(__name__)
            
            # Métriques par caméra
            self._camera_metrics: Dict[str, CameraMetrics] = {}
            
            # Métriques système
            self._system_metrics = SystemMetrics()
            
            # Historique pour les tendances
            self._alert_history: deque = deque(maxlen=1000)
            self._detection_history: deque = deque(maxlen=10000)
            
            # Buffer de temps de détection
            self._detection_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
            
            # Timer pour les mises à jour périodiques
            self._update_timer = QTimer()
            self._update_timer.timeout.connect(self._update_metrics)
            self._update_timer.start(5000)  # Mise à jour toutes les 5 secondes
            
            # S'abonner aux événements
            self._subscribe_to_events()
            
            self._initialized = True
            self._logger.info("AnalyticsService initialisé")
    
    def _subscribe_to_events(self):
        """S'abonne aux événements pertinents."""
        self._event_bus.subscribe(EventType.DETECTION_RESULT, self._on_detection_result)
        self._event_bus.subscribe(EventType.ALERT_GENERATED, self._on_alert_generated)
        self._event_bus.subscribe(EventType.CAMERA_CONNECTED, self._on_camera_connected)
        self._event_bus.subscribe(EventType.CAMERA_DISCONNECTED, self._on_camera_disconnected)
    
    def _on_detection_result(self, event: DetectionResultEvent):
        """Traite un résultat de détection."""
        camera_id = event.camera_id
        
        # Ajouter à l'historique
        self._detection_history.append({
            "camera_id": camera_id,
            "timestamp": datetime.now(),
            "detection_count": len(event.detections),
            "processing_time_ms": event.processing_time_ms,
            "model_name": event.model_name
        })
        
        # Mettre à jour les métriques de la caméra
        if camera_id not in self._camera_metrics:
            self._camera_metrics[camera_id] = CameraMetrics(
                camera_id=camera_id,
                camera_name=f"Camera {camera_id}"
            )
        
        metrics = self._camera_metrics[camera_id]
        metrics.total_detections += len(event.detections)
        metrics.last_detection = datetime.now()
        
        # Compter par type
        for detection in event.detections:
            class_name = detection.get("class_name", "")
            if "fall" in class_name.lower():
                metrics.fall_detections += 1
            elif "person" in class_name.lower():
                metrics.intrusion_detections += 1
            else:
                metrics.movement_detections += 1
        
        # Mettre à jour le temps de détection
        self._detection_times[camera_id].append(event.processing_time_ms)
        if self._detection_times[camera_id]:
            metrics.avg_detection_time_ms = sum(self._detection_times[camera_id]) / len(self._detection_times[camera_id])
    
    def _on_alert_generated(self, event: AlertGeneratedEvent):
        """Traite la génération d'une alerte."""
        if not event.alert:
            return
        
        camera_id = str(event.alert.camera_id)
        
        # Ajouter à l'historique
        self._alert_history.append({
            "camera_id": camera_id,
            "timestamp": datetime.now(),
            "alert_type": event.alert.alert_type.value,
            "severity": event.alert.severity.value,
            "confidence": event.alert.confidence
        })
        
        # Mettre à jour les métriques de la caméra
        if camera_id not in self._camera_metrics:
            self._camera_metrics[camera_id] = CameraMetrics(
                camera_id=camera_id,
                camera_name=event.alert.camera_name or f"Camera {camera_id}"
            )
        
        metrics = self._camera_metrics[camera_id]
        metrics.total_alerts += 1
        metrics.last_alert = datetime.now()
        
        # Compter par gravité
        if event.alert.severity == AlertSeverity.CRITICAL:
            metrics.critical_alerts += 1
        elif event.alert.severity == AlertSeverity.HIGH:
            metrics.high_alerts += 1
        elif event.alert.severity == AlertSeverity.MEDIUM:
            metrics.medium_alerts += 1
        else:
            metrics.low_alerts += 1
    
    def _on_camera_connected(self, event: Event):
        """Traite une connexion de caméra."""
        camera_id = event.data.get("camera_id")
        
        if camera_id not in self._camera_metrics:
            self._camera_metrics[camera_id] = CameraMetrics(
                camera_id=camera_id,
                camera_name=event.data.get("camera_name", f"Camera {camera_id}")
            )
        
        self._camera_metrics[camera_id].last_online = datetime.now()
    
    def _on_camera_disconnected(self, event: Event):
        """Traite une déconnexion de caméra."""
        camera_id = event.data.get("camera_id")
        
        if camera_id in self._camera_metrics:
            self._camera_metrics[camera_id].last_offline = datetime.now()
    
    def _update_metrics(self):
        """Met à jour les métriques système."""
        # Récupérer les statistiques des caméras
        camera_stats = self._camera_manager.get_all_statistics()
        
        # Calculer les métriques système
        total_cameras = len(self._camera_metrics)
        online_cameras = 0
        offline_cameras = 0
        active_cameras = 0
        
        total_detections = 0
        total_alerts = 0
        critical_alerts = 0
        high_alerts = 0
        medium_alerts = 0
        low_alerts = 0
        
        avg_detection_time = 0.0
        avg_fps = 0.0
        
        for camera_id, metrics in self._camera_metrics.items():
            # État de la caméra
            camera_state = self._camera_manager.get_camera_state(camera_id)
            if camera_state == CameraState.CONNECTED:
                online_cameras += 1
                active_cameras += 1
            elif camera_state == CameraState.DETECTING:
                online_cameras += 1
                active_cameras += 1
            elif camera_state == CameraState.DISCONNECTED:
                offline_cameras += 1
            
            # Agréger les métriques
            total_detections += metrics.total_detections
            total_alerts += metrics.total_alerts
            critical_alerts += metrics.critical_alerts
            high_alerts += metrics.high_alerts
            medium_alerts += metrics.medium_alerts
            low_alerts += metrics.low_alerts
            
            avg_detection_time += metrics.avg_detection_time_ms
            avg_fps += metrics.avg_fps
        
        # Calculer les moyennes
        if total_cameras > 0:
            avg_detection_time /= total_cameras
            avg_fps /= total_cameras
        
        # Mettre à jour les métriques système
        self._system_metrics = SystemMetrics(
            total_cameras=total_cameras,
            online_cameras=online_cameras,
            offline_cameras=offline_cameras,
            active_cameras=active_cameras,
            total_alerts=total_alerts,
            critical_alerts=critical_alerts,
            high_alerts=high_alerts,
            medium_alerts=medium_alerts,
            low_alerts=low_alerts,
            total_detections=total_detections,
            avg_detection_time_ms=avg_detection_time,
            avg_fps=avg_fps,
            last_updated=datetime.now()
        )
        
        # Émettre le signal
        self.metrics_updated.emit(self._system_metrics)
    
    def get_system_metrics(self) -> SystemMetrics:
        """Retourne les métriques système actuelles."""
        return self._system_metrics
    
    def get_camera_metrics(self, camera_id: str) -> Optional[CameraMetrics]:
        """
        Retourne les métriques d'une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            Métriques ou None
        """
        return self._camera_metrics.get(camera_id)
    
    def get_all_camera_metrics(self) -> Dict[str, CameraMetrics]:
        """Retourne les métriques de toutes les caméras."""
        return self._camera_metrics.copy()
    
    def get_alert_trend(self, time_range: TimeRange = TimeRange.DAY) -> List[Dict[str, Any]]:
        """
        Retourne la tendance des alertes sur une période.
        
        Args:
            time_range: Plage de temps
        
        Returns:
            Liste de données de tendance
        """
        now = datetime.now()
        
        if time_range == TimeRange.HOUR:
            start_time = now - timedelta(hours=1)
            bucket_size = timedelta(minutes=5)
        elif time_range == TimeRange.DAY:
            start_time = now - timedelta(days=1)
            bucket_size = timedelta(hours=1)
        elif time_range == TimeRange.WEEK:
            start_time = now - timedelta(weeks=1)
            bucket_size = timedelta(days=1)
        else:  # MONTH
            start_time = now - timedelta(days=30)
            bucket_size = timedelta(days=1)
        
        # Filtrer l'historique
        filtered = [
            alert for alert in self._alert_history
            if alert["timestamp"] >= start_time
        ]
        
        # Agréger par buckets
        buckets = defaultdict(lambda: {"count": 0, "critical": 0, "high": 0})
        
        for alert in filtered:
            bucket_time = alert["timestamp"].replace(
                minute=0, second=0, microsecond=0
            )
            buckets[bucket_time]["count"] += 1
            
            if alert["severity"] == "critical":
                buckets[bucket_time]["critical"] += 1
            elif alert["severity"] == "high":
                buckets[bucket_time]["high"] += 1
        
        # Convertir en liste triée
        trend = [
            {
                "timestamp": bucket_time.isoformat(),
                "count": data["count"],
                "critical": data["critical"],
                "high": data["high"]
            }
            for bucket_time, data in sorted(buckets.items())
        ]
        
        return trend
    
    def get_detection_frequency(self, camera_id: Optional[str] = None, time_range: TimeRange = TimeRange.HOUR) -> Dict[str, float]:
        """
        Retourne la fréquence de détection par caméra.
        
        Args:
            camera_id: ID de la caméra (None pour toutes)
            time_range: Plage de temps
        
        Returns:
            Dictionnaire {camera_id: detections_per_minute}
        """
        now = datetime.now()
        
        if time_range == TimeRange.HOUR:
            start_time = now - timedelta(hours=1)
        elif time_range == TimeRange.DAY:
            start_time = now - timedelta(days=1)
        elif time_range == TimeRange.WEEK:
            start_time = now - timedelta(weeks=1)
        else:
            start_time = now - timedelta(days=30)
        
        # Filtrer l'historique
        filtered = [
            det for det in self._detection_history
            if det["timestamp"] >= start_time
            and (camera_id is None or det["camera_id"] == camera_id)
        ]
        
        # Compter par caméra
        counts = defaultdict(int)
        for det in filtered:
            counts[det["camera_id"]] += det["detection_count"]
        
        # Calculer la fréquence (detections per minute)
        duration_minutes = (now - start_time).total_seconds() / 60
        
        frequency = {
            cam_id: count / duration_minutes if duration_minutes > 0 else 0
            for cam_id, count in counts.items()
        }
        
        return frequency
    
    def calculate_false_positive_rate(self, camera_id: str, time_range: TimeRange = TimeRange.DAY) -> float:
        """
        Calcule le taux de faux positifs pour une caméra.
        
        Args:
            camera_id: ID de la caméra
            time_range: Plage de temps
        
        Returns:
            Taux de faux positifs (0.0 - 1.0)
        """
        # Pour une implémentation réelle, il faudrait comparer les alertes
        # avec les confirmations des utilisateurs
        # Ici, on retourne une valeur basée sur les alertes résolues comme faux positifs
        
        now = datetime.now()
        
        if time_range == TimeRange.HOUR:
            start_time = now - timedelta(hours=1)
        elif time_range == TimeRange.DAY:
            start_time = now - timedelta(days=1)
        elif time_range == TimeRange.WEEK:
            start_time = now - timedelta(weeks=1)
        else:
            start_time = now - timedelta(days=30)
        
        # Filtrer les alertes de la caméra
        filtered = [
            alert for alert in self._alert_history
            if alert["camera_id"] == camera_id
            and alert["timestamp"] >= start_time
        ]
        
        if not filtered:
            return 0.0
        
        # Pour l'exemple, on suppose que 10% sont des faux positifs
        # Dans une vraie implémentation, utiliser les données de résolution
        return 0.1
    
    def get_availability(self, camera_id: str, time_range: TimeRange = TimeRange.DAY) -> float:
        """
        Calcule le taux de disponibilité d'une caméra.
        
        Args:
            camera_id: ID de la caméra
            time_range: Plage de temps
        
        Returns:
            Taux de disponibilité (0.0 - 1.0)
        """
        metrics = self._camera_metrics.get(camera_id)
        if not metrics:
            return 0.0
        
        total_time = metrics.uptime_seconds + metrics.downtime_seconds
        
        if total_time == 0:
            return 1.0
        
        return metrics.uptime_seconds / total_time
    
    def get_ai_performance(self, camera_id: Optional[str] = None) -> Dict[str, float]:
        """
        Retourne les métriques de performance IA.
        
        Args:
            camera_id: ID de la caméra (None pour toutes)
        
        Returns:
            Dictionnaire de métriques
        """
        if camera_id:
            metrics = self._camera_metrics.get(camera_id)
            if not metrics:
                return {}
            
            return {
                "avg_detection_time_ms": metrics.avg_detection_time_ms,
                "avg_fps": metrics.avg_fps,
                "detection_rate": metrics.detection_rate,
                "false_positive_rate": metrics.false_positive_rate
            }
        else:
            # Moyennes sur toutes les caméras
            if not self._camera_metrics:
                return {}
            
            total_detection_time = sum(m.avg_detection_time_ms for m in self._camera_metrics.values())
            total_fps = sum(m.avg_fps for m in self._camera_metrics.values())
            count = len(self._camera_metrics)
            
            return {
                "avg_detection_time_ms": total_detection_time / count if count > 0 else 0,
                "avg_fps": total_fps / count if count > 0 else 0,
                "avg_detection_rate": sum(m.detection_rate for m in self._camera_metrics.values()) / count if count > 0 else 0,
                "avg_false_positive_rate": sum(m.false_positive_rate for m in self._camera_metrics.values()) / count if count > 0 else 0
            }


def get_analytics_service() -> AnalyticsService:
    """
    Fonction utilitaire pour récupérer l'AnalyticsService.
    
    Returns:
        Instance singleton du AnalyticsService
    """
    return AnalyticsService()
