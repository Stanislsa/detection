"""
Service d'observabilité pour le monitoring système.
Collecte et expose les métriques : FPS, temps d'inférence, mémoire, GPU, files, événements/sec.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import psutil
import threading

from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from app.core.logger import get_logger


@dataclass
class CameraMetrics:
    """Métriques pour une caméra spécifique."""
    camera_id: str
    
    # FPS
    fps: float = 0.0
    frame_count: int = 0
    last_frame_time: Optional[datetime] = None
    
    # Inférence
    inference_time_ms: float = 0.0
    inference_count: int = 0
    avg_inference_time_ms: float = 0.0
    
    # File d'attente
    queue_size: int = 0
    queue_dropped: int = 0
    queue_drop_rate: float = 0.0
    
    # État
    state: str = "unknown"
    uptime_seconds: float = 0.0
    
    # Historique pour les moyennes
    fps_history: deque = field(default_factory=lambda: deque(maxlen=60))
    inference_history: deque = field(default_factory=lambda: deque(maxlen=60))


@dataclass
class SystemMetrics:
    """Métriques système globales."""
    # CPU
    cpu_percent: float = 0.0
    cpu_count: int = 0
    
    # Mémoire
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    memory_total_gb: float = 0.0
    memory_available_gb: float = 0.0
    
    # Disque
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    disk_free_gb: float = 0.0
    
    # Réseau
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    
    # GPU (si disponible)
    gpu_percent: float = 0.0
    gpu_memory_used_gb: float = 0.0
    gpu_memory_total_gb: float = 0.0
    gpu_available: bool = False
    
    # Événements
    events_per_second: float = 0.0
    total_events: int = 0
    
    # Caméras
    total_cameras: int = 0
    active_cameras: int = 0
    total_fps: float = 0.0
    avg_fps: float = 0.0
    
    # Files d'attente
    total_queue_size: int = 0
    total_queue_dropped: int = 0
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)


class ObservabilityService(QObject):
    """
    Service d'observabilité pour le monitoring système.
    Collecte et expose les métriques en temps réel.
    """
    
    # Signaux
    metrics_updated = pyqtSignal(object)  # SystemMetrics
    camera_metrics_updated = pyqtSignal(str, object)  # camera_id, CameraMetrics
    alert_triggered = pyqtSignal(str, str)  # metric_name, message
    
    _instance = None
    
    def __init__(self):
        super().__init__()
        
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        self._logger = get_logger(__name__)
        
        # Métriques par caméra
        self._camera_metrics: Dict[str, CameraMetrics] = {}
        
        # Métriques système
        self._system_metrics = SystemMetrics()
        
        # Compteur d'événements
        self._event_count = 0
        self._event_history: deque = deque(maxlen=1000)
        
        # Timer pour la collecte périodique
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._collect_metrics)
        self._update_timer.start(1000)  # Mise à jour chaque seconde
        
        # Seuils d'alerte
        self._alert_thresholds = {
            "cpu_percent": 90.0,
            "memory_percent": 90.0,
            "disk_percent": 90.0,
            "fps_drop": 15.0,
            "inference_time_ms": 500.0,
            "queue_drop_rate": 0.1
        }

        self._logger.info("ObservabilityService initialisé")
    
    def _collect_metrics(self):
        """Collecte les métriques système."""
        # CPU
        self._system_metrics.cpu_percent = psutil.cpu_percent(interval=0.1)
        self._system_metrics.cpu_count = psutil.cpu_count()
        
        # Mémoire
        memory = psutil.virtual_memory()
        self._system_metrics.memory_percent = memory.percent
        self._system_metrics.memory_used_gb = memory.used / (1024 ** 3)
        self._system_metrics.memory_total_gb = memory.total / (1024 ** 3)
        self._system_metrics.memory_available_gb = memory.available / (1024 ** 3)
        
        # Disque
        disk = psutil.disk_usage('/')
        self._system_metrics.disk_percent = disk.percent
        self._system_metrics.disk_used_gb = disk.used / (1024 ** 3)
        self._system_metrics.disk_total_gb = disk.total / (1024 ** 3)
        self._system_metrics.disk_free_gb = disk.free / (1024 ** 3)
        
        # Réseau
        network = psutil.net_io_counters()
        self._system_metrics.network_sent_mb = network.bytes_sent / (1024 ** 2)
        self._system_metrics.network_recv_mb = network.bytes_recv / (1024 ** 2)
        
        # GPU (si disponible)
        self._collect_gpu_metrics()
        
        # Événements par seconde
        now = datetime.now()
        self._event_history.append(now)
        cutoff = now - timedelta(seconds=1)
        recent_events = [t for t in self._event_history if t >= cutoff]
        self._system_metrics.events_per_second = len(recent_events)
        
        # Caméras
        self._system_metrics.total_cameras = len(self._camera_metrics)
        active_cameras = sum(1 for m in self._camera_metrics.values() if m.state in ["streaming", "detecting", "recording"])
        self._system_metrics.active_cameras = active_cameras
        
        total_fps = sum(m.fps for m in self._camera_metrics.values())
        self._system_metrics.total_fps = total_fps
        self._system_metrics.avg_fps = total_fps / len(self._camera_metrics) if self._camera_metrics else 0.0
        
        # Files d'attente
        self._system_metrics.total_queue_size = sum(m.queue_size for m in self._camera_metrics.values())
        self._system_metrics.total_queue_dropped = sum(m.queue_dropped for m in self._camera_metrics.values())
        
        # Timestamp
        self._system_metrics.timestamp = now
        
        # Vérifier les seuils d'alerte
        self._check_alert_thresholds()
        
        # Émettre le signal
        self.metrics_updated.emit(self._system_metrics)
    
    def _collect_gpu_metrics(self):
        """Collecte les métriques GPU si disponibles."""
        try:
            import torch
            if torch.cuda.is_available():
                self._system_metrics.gpu_available = True
                self._system_metrics.gpu_percent = torch.cuda.utilization()
                self._system_metrics.gpu_memory_used_gb = torch.cuda.memory_allocated() / (1024 ** 3)
                self._system_metrics.gpu_memory_total_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            else:
                self._system_metrics.gpu_available = False
        except ImportError:
            self._system_metrics.gpu_available = False
    
    def _check_alert_thresholds(self):
        """Vérifie les seuils d'alerte et émet des alertes si nécessaire."""
        thresholds = self._alert_thresholds
        
        if self._system_metrics.cpu_percent > thresholds["cpu_percent"]:
            self.alert_triggered.emit("cpu_percent", f"CPU élevé: {self._system_metrics.cpu_percent:.1f}%")
        
        if self._system_metrics.memory_percent > thresholds["memory_percent"]:
            self.alert_triggered.emit("memory_percent", f"Mémoire élevée: {self._system_metrics.memory_percent:.1f}%")
        
        if self._system_metrics.disk_percent > thresholds["disk_percent"]:
            self.alert_triggered.emit("disk_percent", f"Disque plein: {self._system_metrics.disk_percent:.1f}%")
    
    def register_camera(self, camera_id: str):
        """
        Enregistre une caméra pour le monitoring.
        
        Args:
            camera_id: ID de la caméra
        """
        if camera_id not in self._camera_metrics:
            self._camera_metrics[camera_id] = CameraMetrics(camera_id=camera_id)
            self._logger.info(f"Caméra enregistrée pour monitoring: {camera_id}")
    
    def unregister_camera(self, camera_id: str):
        """
        Désenregistre une caméra du monitoring.
        
        Args:
            camera_id: ID de la caméra
        """
        if camera_id in self._camera_metrics:
            del self._camera_metrics[camera_id]
            self._logger.info(f"Caméra désenregistrée du monitoring: {camera_id}")
    
    def update_camera_fps(self, camera_id: str, fps: float):
        """
        Met à jour le FPS d'une caméra.
        
        Args:
            camera_id: ID de la caméra
            fps: FPS actuel
        """
        if camera_id in self._camera_metrics:
            metrics = self._camera_metrics[camera_id]
            metrics.fps = fps
            metrics.fps_history.append(fps)
            metrics.last_frame_time = datetime.now()
            metrics.frame_count += 1
            
            # Calculer l'uptime
            if metrics.uptime_seconds == 0:
                metrics.uptime_seconds = 1
            else:
                metrics.uptime_seconds += 1
            
            self.camera_metrics_updated.emit(camera_id, metrics)
    
    def update_camera_inference(self, camera_id: str, inference_time_ms: float):
        """
        Met à jour le temps d'inférence d'une caméra.
        
        Args:
            camera_id: ID de la caméra
            inference_time_ms: Temps d'inférence en ms
        """
        if camera_id in self._camera_metrics:
            metrics = self._camera_metrics[camera_id]
            metrics.inference_time_ms = inference_time_ms
            metrics.inference_count += 1
            metrics.inference_history.append(inference_time_ms)
            
            # Calculer la moyenne
            if metrics.inference_history:
                metrics.avg_inference_time_ms = sum(metrics.inference_history) / len(metrics.inference_history)
            
            self.camera_metrics_updated.emit(camera_id, metrics)
    
    def update_camera_queue(self, camera_id: str, queue_size: int, queue_dropped: int):
        """
        Met à jour les métriques de file d'attente d'une caméra.
        
        Args:
            camera_id: ID de la caméra
            queue_size: Taille actuelle de la file
            queue_dropped: Nombre de frames supprimées
        """
        if camera_id in self._camera_metrics:
            metrics = self._camera_metrics[camera_id]
            metrics.queue_size = queue_size
            metrics.queue_dropped = queue_dropped
            
            # Calculer le taux de suppression
            total = metrics.frame_count + queue_dropped
            metrics.queue_drop_rate = queue_dropped / total if total > 0 else 0.0
            
            self.camera_metrics_updated.emit(camera_id, metrics)
    
    def update_camera_state(self, camera_id: str, state: str):
        """
        Met à jour l'état d'une caméra.
        
        Args:
            camera_id: ID de la caméra
            state: État actuel
        """
        if camera_id in self._camera_metrics:
            self._camera_metrics[camera_id].state = state
            self.camera_metrics_updated.emit(camera_id, self._camera_metrics[camera_id])
    
    def record_event(self):
        """Enregistre un événement pour le compteur."""
        self._event_count += 1
        self._event_history.append(datetime.now())
    
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
    
    def get_system_metrics(self) -> SystemMetrics:
        """Retourne les métriques système actuelles."""
        return self._system_metrics
    
    def get_event_count(self) -> int:
        """Retourne le nombre total d'événements."""
        return self._event_count
    
    def set_alert_threshold(self, metric_name: str, threshold: float):
        """
        Définit un seuil d'alerte.
        
        Args:
            metric_name: Nom de la métrique
            threshold: Seuil
        """
        self._alert_thresholds[metric_name] = threshold
        self._logger.info(f"Seuil d'alerte mis à jour: {metric_name} = {threshold}")
    
    def get_alert_thresholds(self) -> Dict[str, float]:
        """Retourne les seuils d'alerte actuels."""
        return self._alert_thresholds.copy()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé des performances.
        
        Returns:
            Dictionnaire de résumé
        """
        return {
            "system": {
                "cpu_percent": self._system_metrics.cpu_percent,
                "memory_percent": self._system_metrics.memory_percent,
                "disk_percent": self._system_metrics.disk_percent,
                "events_per_second": self._system_metrics.events_per_second
            },
            "cameras": {
                "total": self._system_metrics.total_cameras,
                "active": self._system_metrics.active_cameras,
                "avg_fps": self._system_metrics.avg_fps,
                "total_queue_dropped": self._system_metrics.total_queue_dropped
            },
            "gpu": {
                "available": self._system_metrics.gpu_available,
                "percent": self._system_metrics.gpu_percent if self._system_metrics.gpu_available else 0,
                "memory_used_gb": self._system_metrics.gpu_memory_used_gb if self._system_metrics.gpu_available else 0
            }
        }


def get_observability_service() -> ObservabilityService:
    """
    Fonction utilitaire pour récupérer l'ObservabilityService.
    
    Returns:
        Instance singleton du ObservabilityService
    """
    if ObservabilityService._instance is None:
        ObservabilityService._instance = ObservabilityService()
    return ObservabilityService._instance
