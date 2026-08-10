"""
Modèles de données pour les utilisateurs.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    """Rôles d'utilisateur."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


@dataclass
class Permission:
    """Permission utilisateur."""
    id: int
    name: str
    description: str


@dataclass
class User:
    """Modèle d'utilisateur."""
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    permissions: Optional[List[Permission]] = None
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour l'API."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Crée une instance depuis un dictionnaire API."""
        permissions = None
        if data.get("permissions"):
            permissions = [
                Permission(
                    id=p.get("id"),
                    name=p.get("name"),
                    description=p.get("description")
                )
                for p in data["permissions"]
            ]
        
        return cls(
            id=data.get("id"),
            username=data.get("username"),
            email=data.get("email"),
            full_name=data.get("full_name"),
            role=UserRole(data.get("role", "viewer")),
            is_active=data.get("is_active", True),
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            permissions=permissions
        )
