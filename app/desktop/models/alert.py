"""
Modèles de données pour les alertes.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class AlertSeverity(Enum):
    """Gravité d'alerte."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Statut d'alerte."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class AlertType(Enum):
    """Type d'alerte."""
    FALL = "fall"
    INTRUSION = "intrusion"
    MOVEMENT = "movement"
    ABNORMAL_ACTIVITY = "abnormal_activity"
    SYSTEM = "system"


@dataclass
class Alert:
    """Modèle d'alerte."""
    id: int
    camera_id: int
    camera_name: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    detected_at: datetime
    confidence: Optional[float] = None
    bbox: Optional[tuple] = None
    confirmed_at: Optional[datetime] = None
    gravity_score: Optional[float] = None
    impact_velocity: Optional[float] = None
    trunk_angle_at_impact: Optional[float] = None
    time_on_ground: Optional[float] = None
    max_acceleration: Optional[float] = None
    skeleton_video_path: Optional[str] = None
    encrypted_video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    is_false_positive: bool = False
    confirmed_by: Optional[str] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour l'API."""
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "is_false_positive": self.is_false_positive,
            "confirmed_by": self.confirmed_by,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Alert':
        """Crée une instance depuis un dictionnaire API."""
        return cls(
            id=data.get("id"),
            camera_id=data.get("camera_id"),
            camera_name=data.get("camera_name", ""),
            alert_type=AlertType(data.get("alert_type", "fall")),
            severity=AlertSeverity(data.get("severity", "medium")),
            status=AlertStatus(data.get("status", "new")),
            detected_at=datetime.fromisoformat(data["detected_at"]),
            confirmed_at=datetime.fromisoformat(data["confirmed_at"]) if data.get("confirmed_at") else None,
            gravity_score=data.get("gravity_score"),
            impact_velocity=data.get("impact_velocity"),
            trunk_angle_at_impact=data.get("trunk_angle_at_impact"),
            time_on_ground=data.get("time_on_ground"),
            max_acceleration=data.get("max_acceleration"),
            skeleton_video_path=data.get("skeleton_video_path"),
            encrypted_video_path=data.get("encrypted_video_path"),
            thumbnail_path=data.get("thumbnail_path"),
            is_false_positive=data.get("is_false_positive", False),
            confirmed_by=data.get("confirmed_by"),
            notes=data.get("notes")
        )
