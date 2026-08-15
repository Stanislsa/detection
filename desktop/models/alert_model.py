"""
Modèle de données pour les alertes et incidents.
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class AlertPriority(str, Enum):
    """Niveaux de priorité des alertes."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertStatus(str, Enum):
    """Statuts des alertes."""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"


class AlertType(str, Enum):
    """Types d'alertes."""
    MOTION = "MOTION"
    PERSON = "PERSON"
    VEHICLE = "VEHICLE"
    INTRUSION = "INTRUSION"
    SYSTEM = "SYSTEM"
    OTHER = "OTHER"


@dataclass
class Alert:
    """Représente une alerte/incident."""
    id: str
    title: str
    description: str
    priority: AlertPriority
    status: AlertStatus
    alert_type: AlertType
    camera_id: str
    camera_name: str
    location: str
    timestamp: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convertit l'alerte en dictionnaire pour QML."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "alert_type": self.alert_type.value,
            "camera_id": self.camera_id,
            "camera_name": self.camera_name,
            "location": self.location,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "image_path": self.image_path,
            "video_path": self.video_path
        }
