"""
Modèle de données pour les événements.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class EventType(Enum):
    """Types d'événements."""
    PERSON_DETECTED = "person_detected"
    FALL_DETECTED = "fall_detected"
    MOTION_DETECTED = "motion_detected"
    INTRUSION = "intrusion"
    CAMERA_OFFLINE = "camera_offline"
    CAMERA_ONLINE = "camera_online"


class EventSeverity(Enum):
    """Sévérité des événements."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class EventStatus(Enum):
    """Statut des événements."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ARCHIVED = "archived"


@dataclass
class Event:
    """Modèle d'événement."""
    id: str
    type: EventType
    severity: EventSeverity
    camera_id: str
    camera_name: str
    timestamp: datetime
    status: EventStatus = EventStatus.OPEN
    description: Optional[str] = None
    preview_image: Optional[str] = None  # Path to preview image
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire."""
        return {
            "id": self.id,
            "type": self.type.value,
            "severity": self.severity.value,
            "camera_id": self.camera_id,
            "camera_name": self.camera_name,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "description": self.description,
            "preview_image": self.preview_image,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Crée un événement depuis un dictionnaire."""
        return cls(
            id=data["id"],
            type=EventType(data["type"]),
            severity=EventSeverity(data["severity"]),
            camera_id=data["camera_id"],
            camera_name=data["camera_name"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            status=EventStatus(data.get("status", "open")),
            description=data.get("description"),
            preview_image=data.get("preview_image"),
            metadata=data.get("metadata", {})
        )
    
    def get_display_name(self) -> str:
        """Retourne le nom d'affichage du type d'événement."""
        names = {
            EventType.PERSON_DETECTED: "Person Detected",
            EventType.FALL_DETECTED: "Fall Detected",
            EventType.MOTION_DETECTED: "Motion Detected",
            EventType.INTRUSION: "Intrusion",
            EventType.CAMERA_OFFLINE: "Camera Offline",
            EventType.CAMERA_ONLINE: "Camera Online"
        }
        return names.get(self.type, self.type.value)
