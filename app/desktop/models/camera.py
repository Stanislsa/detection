"""
Modèles de données pour les caméras.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class CameraStatus(Enum):
    """Statut de caméra."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class Camera:
    """Modèle de caméra."""
    id: int
    name: str
    source: str  # RTSP URL, webcam index, ou chemin fichier
    source_type: str  # 'webcam', 'rtsp', 'file'
    room: Optional[str] = None
    is_active: bool = True
    fps: int = 30
    resolution_width: int = 1920
    resolution_height: int = 1080
    status: CameraStatus = CameraStatus.OFFLINE
    last_seen: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    @property
    def resolution(self) -> str:
        """Retourne la résolution sous forme de chaîne."""
        return f"{self.resolution_width}x{self.resolution_height}"
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour l'API."""
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "source_type": self.source_type,
            "room": self.room,
            "is_active": self.is_active,
            "fps": self.fps,
            "resolution_width": self.resolution_width,
            "resolution_height": self.resolution_height
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Camera':
        """Crée une instance depuis un dictionnaire API."""
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            source=data.get("source"),
            source_type=data.get("source_type", "rtsp"),
            room=data.get("room"),
            is_active=data.get("is_active", True),
            fps=data.get("fps", 30),
            resolution_width=data.get("resolution_width", 1920),
            resolution_height=data.get("resolution_height", 1080),
            status=CameraStatus(data.get("status", "offline")),
            last_seen=datetime.fromisoformat(data["last_seen"]) if data.get("last_seen") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )
