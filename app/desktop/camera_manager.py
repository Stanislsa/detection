"""
Gestionnaire de caméras multi-flux.
Gère plusieurs caméras simultanément avec leurs workers respectifs.
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading

from PyQt6.QtCore import QObject, pyqtSignal

from app.desktop.models.camera import Camera
from app.desktop.workers.camera_worker import CameraWorker
from app.desktop.workers.detection_worker import DetectionWorker
from app.desktop.workers.recording_worker import RecordingManager
from app.events.event_bus import EventBus
from app.events.event_types import (
    CameraConnectedEvent, CameraDisconnectedEvent, FrameReceivedEvent,
    DetectionResultEvent, EventType
)
from app.core.logger import get_logger
from app.core.exceptions import CameraException


class CameraState(Enum):
    """États d'une caméra."""
    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DETECTING = "detecting"
    RECORDING = "recording"
    ERROR = "error"
    DISCONNECTED = "disconnected"


@dataclass
class CameraInstance:
    """
    Instance de caméra avec tous ses composants.
    """
    camera: Camera
    state: CameraState = CameraState.IDLE
    camera_worker: Optional[CameraWorker] = None
    detection_worker: Optional[DetectionWorker] = None
    detector: Optional[object] = None  # Détecteur IA
    frame_buffer: List = field(default_factory=list)
    max_buffer_size: int = 30
    statistics: Dict = field(default_factory=dict)
    last_frame_time: Optional[datetime] = None
    frame_count: int = 0
    detection_count: int = 0
    
    def add_frame(self, frame):
        """Ajoute un frame au buffer."""
        self.frame_buffer.append(frame)
        if len(self.frame_buffer) > self.max_buffer_size:
            self.frame_buffer.pop(0)
        self.last_frame_time = datetime.now()
        self.frame_count += 1
    
    def get_latest_frame(self):
        """Retourne le frame le plus récent."""
        return self.frame_buffer[-1] if self.frame_buffer else None
    
    def update_statistics(self, key: str, value):
        """Met à jour les statistiques."""
        self.statistics[key] = value


class CameraManager(QObject):
    """
    Gestionnaire de caméras avec support multi-flux.
    Chaque caméra a son propre worker vidéo, worker IA et buffer.
    """
    
    # Signaux PyQt
    camera_added = pyqtSignal(str)  # camera_id
    camera_removed = pyqtSignal(str)  # camera_id
    camera_state_changed = pyqtSignal(str, str)  # camera_id, state
    frame_received = pyqtSignal(str, object)  # camera_id, frame
    detection_result = pyqtSignal(str, object)  # camera_id, result
    error_occurred = pyqtSignal(str, str)  # camera_id, error_message
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        super().__init__()
        
        if not hasattr(self, '_initialized'):
            self._cameras: Dict[str, CameraInstance] = {}
            self._event_bus = EventBus()
            self._recording_manager = RecordingManager()
            self._logger = get_logger(__name__)
            self._lock = threading.Lock()
            self._initialized = True
    
    def add_camera(self, camera: Camera, detector: Optional[object] = None) -> bool:
        """
        Ajoute une caméra au gestionnaire.
        
        Args:
            camera: Configuration de la caméra
            detector: Détecteur IA à utiliser (optionnel)
        
        Returns:
            True si succès
        """
        with self._lock:
            camera_id = str(camera.id)
            
            if camera_id in self._cameras:
                self._logger.warning(f"Caméra {camera_id} déjà existante")
                return False
            
            # Créer l'instance de caméra
            instance = CameraInstance(
                camera=camera,
                detector=detector,
                statistics={
                    "total_frames": 0,
                    "total_detections": 0,
                    "fps": 0.0,
                    "uptime_seconds": 0.0,
                    "errors": 0
                }
            )
            
            self._cameras[camera_id] = instance
            self.camera_added.emit(camera_id)
            
            self._logger.info(f"Caméra ajoutée: {camera.name} ({camera_id})")
            return True
    
    def remove_camera(self, camera_id: str) -> bool:
        """
        Supprime une caméra du gestionnaire.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            True si succès
        """
        with self._lock:
            if camera_id not in self._cameras:
                self._logger.warning(f"Caméra {camera_id} inexistante")
                return False
            
            instance = self._cameras[camera_id]
            
            # Arrêter les workers
            self.stop_camera(camera_id)
            
            # Supprimer de la liste
            del self._cameras[camera_id]
            self.camera_removed.emit(camera_id)
            
            self._logger.info(f"Caméra supprimée: {camera_id}")
            return True
    
    def start_camera(self, camera_id: str) -> bool:
        """
        Démarre une caméra (capture vidéo).
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            True si succès
        """
        with self._lock:
            if camera_id not in self._cameras:
                self._logger.error(f"Caméra {camera_id} inexistante")
                return False
            
            instance = self._cameras[camera_id]
            
            if instance.state in [CameraState.CONNECTING, CameraState.CONNECTED]:
                self._logger.warning(f"Caméra {camera_id} déjà démarrée")
                return False
            
            # Créer et démarrer le worker vidéo
            instance.camera_worker = CameraWorker(
                camera_id=camera_id,
                source=instance.camera.source,
                source_type=instance.camera.source_type
            )
            
            # Connecter les signaux
            instance.camera_worker.frame_ready.connect(
                lambda frame: self._on_frame_received(camera_id, frame)
            )
            instance.camera_worker.camera_connected.connect(
                lambda: self._on_camera_connected(camera_id)
            )
            instance.camera_worker.camera_disconnected.connect(
                lambda reason: self._on_camera_disconnected(camera_id, reason)
            )
            instance.camera_worker.error.connect(
                lambda error: self._on_camera_error(camera_id, error)
            )
            
            # Démarrer le worker
            instance.camera_worker.start()
            instance.state = CameraState.CONNECTING
            self.camera_state_changed.emit(camera_id, CameraState.CONNECTING.value)
            
            self._logger.info(f"Caméra démarrée: {camera_id}")
            return True
    
    def stop_camera(self, camera_id: str) -> bool:
        """
        Arrête une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            True si succès
        """
        with self._lock:
            if camera_id not in self._cameras:
                return False
            
            instance = self._cameras[camera_id]
            
            # Arrêter le worker vidéo
            if instance.camera_worker:
                instance.camera_worker.stop()
                instance.camera_worker.wait()
                instance.camera_worker = None
            
            # Arrêter le worker IA
            if instance.detection_worker:
                instance.detection_worker.stop()
                instance.detection_worker.wait()
                instance.detection_worker = None
            
            # Arrêter l'enregistrement
            self._recording_manager.stop_recording(camera_id)
            
            instance.state = CameraState.IDLE
            self.camera_state_changed.emit(camera_id, CameraState.IDLE.value)
            
            self._logger.info(f"Caméra arrêtée: {camera_id}")
            return True
    
    def start_detection(self, camera_id: str, detector: Optional[object] = None) -> bool:
        """
        Démarre la détection IA pour une caméra.
        
        Args:
            camera_id: ID de la caméra
            detector: Détecteur IA à utiliser (optionnel, utilise celui de la caméra si None)
        
        Returns:
            True si succès
        """
        with self._lock:
            if camera_id not in self._cameras:
                self._logger.error(f"Caméra {camera_id} inexistante")
                return False
            
            instance = self._cameras[camera_id]
            
            if instance.state != CameraState.CONNECTED:
                self._logger.error(f"Caméra {camera_id} non connectée")
                return False
            
            # Utiliser le détecteur fourni ou celui de la caméra
            active_detector = detector or instance.detector
            
            if active_detector is None:
                self._logger.error(f"Aucun détecteur pour la caméra {camera_id}")
                return False
            
            # Créer et démarrer le worker IA
            instance.detection_worker = DetectionWorker(detector=active_detector)
            
            # Connecter les signaux
            instance.detection_worker.detection_ready.connect(
                lambda frame, results: self._on_detection_result(camera_id, frame, results)
            )
            
            instance.detection_worker.start()
            instance.state = CameraState.DETECTING
            self.camera_state_changed.emit(camera_id, CameraState.DETECTING.value)
            
            self._logger.info(f"Détection démarrée pour caméra {camera_id}")
            return True
    
    def stop_detection(self, camera_id: str) -> bool:
        """
        Arrête la détection IA pour une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            True si succès
        """
        with self._lock:
            if camera_id not in self._cameras:
                return False
            
            instance = self._cameras[camera_id]
            
            if instance.detection_worker:
                instance.detection_worker.stop()
                instance.detection_worker.wait()
                instance.detection_worker = None
            
            if instance.state == CameraState.DETECTING:
                instance.state = CameraState.CONNECTED
                self.camera_state_changed.emit(camera_id, CameraState.CONNECTED.value)
            
            self._logger.info(f"Détection arrêtée pour caméra {camera_id}")
            return True
    
    def start_recording(self, camera_id: str, output_path: str) -> bool:
        """
        Démarre l'enregistrement pour une caméra.
        
        Args:
            camera_id: ID de la caméra
            output_path: Chemin du fichier de sortie
        
        Returns:
            True si succès
        """
        with self._lock:
            if camera_id not in self._cameras:
                return False
            
            instance = self._cameras[camera_id]
            
            success = self._recording_manager.start_recording(
                camera_id=camera_id,
                output_path=output_path,
                fps=instance.camera.fps,
                resolution=(instance.camera.resolution_width, instance.camera.resolution_height)
            )
            
            if success:
                instance.state = CameraState.RECORDING
                self.camera_state_changed.emit(camera_id, CameraState.RECORDING.value)
                self._logger.info(f"Enregistrement démarré pour caméra {camera_id}")
            
            return success
    
    def stop_recording(self, camera_id: str) -> bool:
        """
        Arrête l'enregistrement pour une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            True si succès
        """
        with self._lock:
            success = self._recording_manager.stop_recording(camera_id)
            
            if success and camera_id in self._cameras:
                instance = self._cameras[camera_id]
                if instance.state == CameraState.RECORDING:
                    instance.state = CameraState.CONNECTED
                    self.camera_state_changed.emit(camera_id, CameraState.CONNECTED.value)
                self._logger.info(f"Enregistrement arrêté pour caméra {camera_id}")
            
            return success
    
    def get_camera(self, camera_id: str) -> Optional[CameraInstance]:
        """
        Retourne une instance de caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            Instance de caméra ou None
        """
        return self._cameras.get(camera_id)
    
    def get_all_cameras(self) -> Dict[str, CameraInstance]:
        """Retourne toutes les instances de caméras."""
        return self._cameras.copy()
    
    def get_camera_state(self, camera_id: str) -> Optional[CameraState]:
        """
        Retourne l'état d'une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            État de la caméra ou None
        """
        instance = self._cameras.get(camera_id)
        return instance.state if instance else None
    
    def get_camera_statistics(self, camera_id: str) -> Optional[Dict]:
        """
        Retourne les statistiques d'une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            Statistiques ou None
        """
        instance = self._cameras.get(camera_id)
        return instance.statistics if instance else None
    
    def get_all_statistics(self) -> Dict[str, Dict]:
        """Retourne les statistiques de toutes les caméras."""
        return {camera_id: instance.statistics for camera_id, instance in self._cameras.items()}
    
    def start_all(self) -> int:
        """
        Démarre toutes les caméras.
        
        Returns:
            Nombre de caméras démarrées
        """
        count = 0
        for camera_id in self._cameras:
            if self.start_camera(camera_id):
                count += 1
        return count
    
    def stop_all(self) -> int:
        """
        Arrête toutes les caméras.
        
        Returns:
            Nombre de caméras arrêtées
        """
        count = 0
        for camera_id in list(self._cameras.keys()):
            if self.stop_camera(camera_id):
                count += 1
        return count
    
    # ===== Callbacks =====
    
    def _on_frame_received(self, camera_id: str, frame):
        """Callback quand un frame est reçu."""
        with self._lock:
            if camera_id in self._cameras:
                instance = self._cameras[camera_id]
                instance.add_frame(frame)
                
                # Publier l'événement
                event = FrameReceivedEvent(camera_id=camera_id, frame=frame)
                self._event_bus.publish(event)
                
                # Émettre le signal PyQt
                self.frame_received.emit(camera_id, frame)
                
                # Envoyer au worker d'enregistrement si actif
                if self._recording_manager.is_recording(camera_id):
                    self._recording_manager.add_frame(camera_id, frame)
                
                # Envoyer au worker IA si actif
                if instance.detection_worker:
                    instance.detection_worker.process_frame(frame)
    
    def _on_camera_connected(self, camera_id: str):
        """Callback quand une caméra se connecte."""
        with self._lock:
            if camera_id in self._cameras:
                instance = self._cameras[camera_id]
                instance.state = CameraState.CONNECTED
                self.camera_state_changed.emit(camera_id, CameraState.CONNECTED.value)
                
                # Publier l'événement
                event = CameraConnectedEvent(
                    camera_id=camera_id,
                    camera_name=instance.camera.name,
                    source=instance.camera.source
                )
                self._event_bus.publish(event)
    
    def _on_camera_disconnected(self, camera_id: str, reason: str):
        """Callback quand une caméra se déconnecte."""
        with self._lock:
            if camera_id in self._cameras:
                instance = self._cameras[camera_id]
                instance.state = CameraState.DISCONNECTED
                self.camera_state_changed.emit(camera_id, CameraState.DISCONNECTED.value)
                
                # Publier l'événement
                event = CameraDisconnectedEvent(camera_id=camera_id, reason=reason)
                self._event_bus.publish(event)
    
    def _on_camera_error(self, camera_id: str, error: str):
        """Callback quand une erreur survient sur une caméra."""
        with self._lock:
            if camera_id in self._cameras:
                instance = self._cameras[camera_id]
                instance.state = CameraState.ERROR
                instance.statistics["errors"] += 1
                self.camera_state_changed.emit(camera_id, self.camera_state_changed.emit(camera_id, CameraState.ERROR.value))
                self.error_occurred.emit(camera_id, error)
    
    def _on_detection_result(self, camera_id: str, frame, results):
        """Callback quand un résultat de détection est reçu."""
        with self._lock:
            if camera_id in self._cameras:
                instance = self._cameras[camera_id]
                instance.detection_count += 1
                instance.statistics["total_detections"] = instance.detection_count
                
                # Publier l'événement
                detections_data = [
                    {
                        "class_id": r.class_id,
                        "class_name": r.class_name,
                        "confidence": r.confidence,
                        "bbox": r.bbox
                    }
                    for r in results
                ]
                event = DetectionResultEvent(
                    camera_id=camera_id,
                    detections=detections_data,
                    model_name=instance.detector.__class__.__name__ if instance.detector else "unknown"
                )
                self._event_bus.publish(event)
                
                # Émettre le signal PyQt
                self.detection_result.emit(camera_id, results)


def get_camera_manager() -> CameraManager:
    """
    Fonction utilitaire pour récupérer le CameraManager.
    
    Returns:
        Instance singleton du CameraManager
    """
    return CameraManager()
