"""
Types d'événements pour le bus d'événements.
Définit tous les événements qui peuvent circuler dans l'application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Dict, List
from enum import Enum
import numpy as np

from app.desktop.models.camera import Camera
from app.desktop.models.alert import Alert
from app.desktop.models.user import User


class EventType(Enum):
    """Types d'événements disponibles."""
    # Caméras
    CAMERA_CONNECTED = "camera_connected"
    CAMERA_DISCONNECTED = "camera_disconnected"
    CAMERA_STATUS_CHANGED = "camera_status_changed"
    FRAME_RECEIVED = "frame_received"
    
    # Détection IA
    DETECTION_STARTED = "detection_started"
    DETECTION_STOPPED = "detection_stopped"
    DETECTION_RESULT = "detection_result"
    FALL_DETECTED = "fall_detected"
    INTRUSION_DETECTED = "intrusion_detected"
    MOVEMENT_DETECTED = "movement_detected"
    
    # Alertes
    ALERT_GENERATED = "alert_generated"
    ALERT_UPDATED = "alert_updated"
    ALERT_RESOLVED = "alert_resolved"
    
    # Utilisateurs
    USER_LOGGED_IN = "user_logged_in"
    USER_LOGGED_OUT = "user_logged_out"
    USER_PERMISSION_CHANGED = "user_permission_changed"
    
    # Système
    SYSTEM_STARTED = "system_started"
    SYSTEM_STOPPED = "system_stopped"
    ERROR_OCCURRED = "error_occurred"
    WARNING_OCCURRED = "warning_occurred"
    
    # Enregistrement
    RECORDING_STARTED = "recording_started"
    RECORDING_STOPPED = "recording_stopped"
    SNAPSHOT_SAVED = "snapshot_saved"
    
    # WebSocket
    WS_CONNECTED = "ws_connected"
    WS_DISCONNECTED = "ws_disconnected"
    WS_MESSAGE_RECEIVED = "ws_message_received"


@dataclass
class Event:
    """
    Événement de base.
    Tous les événements héritent de cette classe.
    """
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "system"  # Source de l'événement
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'événement en dictionnaire."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data
        }


@dataclass
class CameraConnectedEvent(Event):
    """Événement émis quand une caméra se connecte."""
    camera_id: str = ""
    camera_name: str = ""
    source: str = ""
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.CAMERA_CONNECTED
        self.data = {
            "camera_id": self.camera_id,
            "camera_name": self.camera_name,
            "source": self.source
        }


@dataclass
class CameraDisconnectedEvent(Event):
    """Événement émis quand une caméra se déconnecte."""
    camera_id: str = ""
    reason: str = ""
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.CAMERA_DISCONNECTED
        self.data = {
            "camera_id": self.camera_id,
            "reason": self.reason
        }


@dataclass
class FrameReceivedEvent(Event):
    """Événement émis quand un frame est reçu d'une caméra."""
    camera_id: str = ""
    frame: Optional[np.ndarray] = None
    frame_number: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.FRAME_RECEIVED
        self.data = {
            "camera_id": self.camera_id,
            "frame_number": self.frame_number
        }


@dataclass
class DetectionResultEvent(Event):
    """Événement émis quand une détection IA est effectuée."""
    camera_id: str = ""
    detections: List[Dict[str, Any]] = field(default_factory=list)
    processing_time_ms: float = 0.0
    model_name: str = ""
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.DETECTION_RESULT
        self.data = {
            "camera_id": self.camera_id,
            "detection_count": len(self.detections),
            "processing_time_ms": self.processing_time_ms,
            "model_name": self.model_name
        }


@dataclass
class FallDetectedEvent(Event):
    """Événement émis quand une chute est détectée."""
    camera_id: str = ""
    confidence: float = 0.0
    bbox: tuple = (0, 0, 0, 0)
    frame: Optional[np.ndarray] = None
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.FALL_DETECTED
        self.data = {
            "camera_id": self.camera_id,
            "confidence": self.confidence,
            "bbox": self.bbox
        }


@dataclass
class IntrusionDetectedEvent(Event):
    """Événement émis quand une intrusion est détectée."""
    camera_id: str = ""
    confidence: float = 0.0
    zone_id: str = ""
    bbox: tuple = (0, 0, 0, 0)
    frame: Optional[np.ndarray] = None
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.INTRUSION_DETECTED
        self.data = {
            "camera_id": self.camera_id,
            "confidence": self.confidence,
            "zone_id": self.zone_id,
            "bbox": self.bbox
        }


@dataclass
class AlertGeneratedEvent(Event):
    """Événement émis quand une alerte est générée."""
    alert: Optional[Alert] = None
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.ALERT_GENERATED
        if self.alert:
            self.data = {
                "alert_id": self.alert.id,
                "camera_id": self.alert.camera_id,
                "alert_type": self.alert.alert_type.value,
                "severity": self.alert.severity.value,
                "confidence": self.alert.confidence
            }


@dataclass
class AlertResolvedEvent(Event):
    """Événement émis quand une alerte est résolue."""
    alert_id: int = 0
    resolved_by: str = ""
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.ALERT_RESOLVED
        self.data = {
            "alert_id": self.alert_id,
            "resolved_by": self.resolved_by
        }


@dataclass
class UserLoggedInEvent(Event):
    """Événement émis quand un utilisateur se connecte."""
    user: Optional[User] = None
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.USER_LOGGED_IN
        if self.user:
            self.data = {
                "user_id": self.user.id,
                "username": self.user.username,
                "role": self.user.role.value
            }


@dataclass
class UserLoggedOutEvent(Event):
    """Événement émis quand un utilisateur se déconnecte."""
    user_id: int = 0
    username: str = ""
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.USER_LOGGED_OUT
        self.data = {
            "user_id": self.user_id,
            "username": self.username
        }


@dataclass
class RecordingStartedEvent(Event):
    """Événement émis quand un enregistrement démarre."""
    camera_id: str = ""
    file_path: str = ""
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.RECORDING_STARTED
        self.data = {
            "camera_id": self.camera_id,
            "file_path": self.file_path
        }


@dataclass
class RecordingStoppedEvent(Event):
    """Événement émis quand un enregistrement s'arrête."""
    camera_id: str = ""
    file_path: str = ""
    duration_seconds: float = 0.0
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.RECORDING_STOPPED
        self.data = {
            "camera_id": self.camera_id,
            "file_path": self.file_path,
            "duration_seconds": self.duration_seconds
        }


@dataclass
class ErrorEvent(Event):
    """Événement émis quand une erreur survient."""
    error_message: str = ""
    error_type: str = ""
    stack_trace: str = ""
    
    def __post_init__(self):
        if not self.event_type:
            self.event_type = EventType.ERROR_OCCURRED
        self.data = {
            "error_message": self.error_message,
            "error_type": self.error_type,
            "stack_trace": self.stack_trace
        }
