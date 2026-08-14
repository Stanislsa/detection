"""
Modèle de données pour les utilisateurs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


class UserRole(Enum):
    """Rôles d'utilisateur."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    ANALYST = "analyst"


class UserStatus(Enum):
    """Statuts d'utilisateur."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Permission(Enum):
    """Permissions."""
    CAMERA_VIEW = "camera_view"
    CAMERA_MANAGE = "camera_manage"
    ALERTS_VIEW = "alerts_view"
    ALERTS_MANAGE = "alerts_manage"
    EVENTS_VIEW = "events_view"
    EVENTS_MANAGE = "events_manage"
    USERS_VIEW = "users_view"
    USERS_MANAGE = "users_manage"
    SETTINGS_VIEW = "settings_view"
    SETTINGS_MANAGE = "settings_manage"
    EXPORT_DATA = "export_data"


@dataclass
class UserActivity:
    """Activité d'un utilisateur."""
    timestamp: datetime
    action: str
    details: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "timestamp_formatted": self._format_timestamp(),
            "action": self.action,
            "details": self.details
        }
    
    def _format_timestamp(self) -> str:
        now = datetime.now()
        diff = now - self.timestamp
        if diff.total_seconds() < 60:
            return "Just now"
        if diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() // 60)} min ago"
        if diff.total_seconds() < 86400:
            return f"{int(diff.total_seconds() // 3600)} hours ago"
        return self.timestamp.strftime("%Y-%m-%d %H:%M")


@dataclass
class User:
    """Modèle d'utilisateur."""
    id: str
    username: str
    email: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime] = None
    permissions: List[Permission] = field(default_factory=list)
    activities: List[UserActivity] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "created_at_formatted": self.created_at.strftime("%Y-%m-%d"),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_login_formatted": self._format_last_login(),
            "permissions": [p.value for p in self.permissions],
            "activities": [a.to_dict() for a in self.activities],
            "metadata": self.metadata
        }
    
    def _format_last_login(self) -> str:
        if not self.last_login:
            return "Never"
        now = datetime.now()
        diff = now - self.last_login
        if diff.total_seconds() < 60:
            return "Just now"
        if diff.total_seconds() < 3600:
            return f"{int(diff.total_seconds() // 60)} min ago"
        if diff.total_seconds() < 86400:
            return f"{int(diff.total_seconds() // 3600)} hours ago"
        return self.last_login.strftime("%Y-%m-%d %H:%M")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            role=UserRole(data["role"]),
            status=UserStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None,
            permissions=[Permission(p) for p in data.get("permissions", [])],
            activities=[UserActivity(
                timestamp=datetime.fromisoformat(a["timestamp"]),
                action=a["action"],
                details=a["details"]
            ) for a in data.get("activities", [])],
            metadata=data.get("metadata", {})
        )
    
    def add_activity(self, action: str, details: str) -> None:
        """Ajoute une activité à l'utilisateur."""
        activity = UserActivity(
            timestamp=datetime.now(),
            action=action,
            details=details
        )
        self.activities.insert(0, activity)
        if len(self.activities) > 50:
            self.activities.pop()
    
    def has_permission(self, permission: Permission) -> bool:
        """Vérifie si l'utilisateur a une permission."""
        return permission in self.permissions
