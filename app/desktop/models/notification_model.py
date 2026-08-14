"""
Modèle de données pour les notifications.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class NotificationType(Enum):
    """Types de notifications."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class NotificationCategory(Enum):
    """Catégories de notifications."""
    SYSTEM = "system"
    CAMERA = "camera"
    ALERT = "alert"
    AI_MODEL = "ai_model"
    MAINTENANCE = "maintenance"


@dataclass
class Notification:
    """Modèle de notification."""
    id: str
    type: NotificationType
    category: NotificationCategory
    title: str
    message: str
    timestamp: datetime
    read: bool = False
    action_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le modèle en dictionnaire."""
        return {
            "id": self.id,
            "type": self.type.value,
            "category": self.category.value,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "read": self.read,
            "action_required": self.action_required,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        """Crée une notification depuis un dictionnaire."""
        return cls(
            id=data["id"],
            type=NotificationType(data["type"]),
            category=NotificationCategory(data["category"]),
            title=data["title"],
            message=data["message"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            read=data.get("read", False),
            action_required=data.get("action_required", False),
            metadata=data.get("metadata", {})
        )
    
    def mark_as_read(self) -> None:
        """Marque la notification comme lue."""
        self.read = True
