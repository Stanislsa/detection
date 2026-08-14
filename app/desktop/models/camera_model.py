"""
Modèle de données pour les caméras.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class CameraStatus(Enum):
    """Statut de la caméra."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class DetectionType(Enum):
    """Types de détection."""
    PERSON = "person"
    VEHICLE = "vehicle"
    MOTION = "motion"
    OBJECT = "object"


@dataclass
class Detection:
    """Détection IA."""
    id: str
    type: DetectionType
    label: str
    confidence: float
    bbox: Dict[str, float]  # {x, y, width, height} normalized 0-1
    timestamp: datetime
    keypoints: Optional[List[Dict[str, float]]] = None  # For pose estimation


@dataclass
class Camera:
    """Modèle de caméra."""
    id: str
    name: str
    url: str
    location: str
    status: CameraStatus = CameraStatus.OFFLINE
    resolution: str = "1920x1080"
    fps: int = 30
    is_recording: bool = False
    detection_enabled: bool = True
    confidence_threshold: float = 0.7
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    recent_detections: List[Detection] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "location": self.location,
            "status": self.status.value,
            "resolution": self.resolution,
            "fps": self.fps,
            "is_recording": self.is_recording,
            "detection_enabled": self.detection_enabled,
            "confidence_threshold": self.confidence_threshold,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "recent_detections": [self._detection_to_dict(d) for d in self.recent_detections]
        }
    
    def _detection_to_dict(self, detection: Detection) -> Dict[str, Any]:
        """Convertit une détection en dictionnaire."""
        return {
            "id": detection.id,
            "type": detection.type.value,
            "label": detection.label,
            "confidence": detection.confidence,
            "bbox": detection.bbox,
            "timestamp": detection.timestamp.isoformat(),
            "keypoints": detection.keypoints
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Camera":
        """Crée une caméra depuis un dictionnaire."""
        return cls(
            id=data["id"],
            name=data["name"],
            url=data["url"],
            location=data["location"],
            status=CameraStatus(data.get("status", "offline")),
            resolution=data.get("resolution", "1920x1080"),
            fps=data.get("fps", 30),
            is_recording=data.get("is_recording", False),
            detection_enabled=data.get("detection_enabled", True),
            confidence_threshold=data.get("confidence_threshold", 0.7),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            last_activity=datetime.fromisoformat(data["last_activity"]) if data.get("last_activity") else None
        )
    
    def add_detection(self, detection: Detection) -> None:
        """Ajoute une détection à la caméra."""
        self.recent_detections.insert(0, detection)
        self.last_activity = detection.timestamp
        
        # Garder seulement les 100 dernières détections
        if len(self.recent_detections) > 100:
            self.recent_detections = self.recent_detections[:100]
    
    def has_recent_alert(self, minutes: int = 5) -> bool:
        """Vérifie s'il y a une alerte récente."""
        if not self.last_activity:
            return False
        
        threshold = datetime.now() - timedelta(minutes=minutes)
        return self.last_activity > threshold
    
    def get_alert_level(self) -> float:
        """Calcule le niveau d'alerte (0-1)."""
        if not self.recent_detections:
            return 0.0
        
        # Compte les détections des 5 dernières minutes
        threshold = datetime.now() - timedelta(minutes=5)
        recent_count = sum(1 for d in self.recent_detections if d.timestamp > threshold)
        
        # Normalise entre 0 et 1 (10+ détections = niveau max)
        return min(recent_count / 10.0, 1.0)


from datetime import timedelta
