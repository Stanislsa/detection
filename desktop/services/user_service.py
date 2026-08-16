"""
Service pour la gestion des utilisateurs.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import random

from desktop.models.user_model import (
    User, UserRole, UserStatus, Permission, UserActivity
)


class UserService:
    """Service de gestion des utilisateurs."""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._initialize_demo_users()
    
    def _initialize_demo_users(self) -> None:
        """Initialise les utilisateurs de démonstration."""
        demo_users = [
            User(
                id=str(uuid.uuid4()),
                username="admin",
                email="admin@sentinelai.com",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                created_at=datetime.now() - timedelta(days=365),
                last_login=datetime.now() - timedelta(minutes=5),
                permissions=list(Permission),
                activities=[
                    UserActivity(timestamp=datetime.now() - timedelta(minutes=5), action="Login", details="Successful login"),
                    UserActivity(timestamp=datetime.now() - timedelta(hours=2), action="Settings Update", details="Updated system settings"),
                    UserActivity(timestamp=datetime.now() - timedelta(days=1), action="User Created", details="Created user operator1"),
                ]
            ),
            User(
                id=str(uuid.uuid4()),
                username="operator1",
                email="operator1@sentinelai.com",
                role=UserRole.OPERATOR,
                status=UserStatus.ACTIVE,
                created_at=datetime.now() - timedelta(days=180),
                last_login=datetime.now() - timedelta(hours=1),
                permissions=[
                    Permission.CAMERA_VIEW, Permission.CAMERA_MANAGE,
                    Permission.ALERTS_VIEW, Permission.ALERTS_MANAGE,
                    Permission.EVENTS_VIEW, Permission.EVENTS_MANAGE
                ],
                activities=[
                    UserActivity(timestamp=datetime.now() - timedelta(hours=1), action="Login", details="Successful login"),
                    UserActivity(timestamp=datetime.now() - timedelta(hours=3), action="Camera Added", details="Added camera cam6"),
                    UserActivity(timestamp=datetime.now() - timedelta(days=2), action="Alert Resolved", details="Resolved alert #1234"),
                ]
            ),
            User(
                id=str(uuid.uuid4()),
                username="viewer1",
                email="viewer1@sentinelai.com",
                role=UserRole.VIEWER,
                status=UserStatus.ACTIVE,
                created_at=datetime.now() - timedelta(days=90),
                last_login=datetime.now() - timedelta(hours=6),
                permissions=[
                    Permission.CAMERA_VIEW, Permission.ALERTS_VIEW, Permission.EVENTS_VIEW
                ],
                activities=[
                    UserActivity(timestamp=datetime.now() - timedelta(hours=6), action="Login", details="Successful login"),
                    UserActivity(timestamp=datetime.now() - timedelta(days=1), action="Viewed Camera", details="Viewed camera cam1"),
                ]
            ),
            User(
                id=str(uuid.uuid4()),
                username="analyst1",
                email="analyst1@sentinelai.com",
                role=UserRole.ANALYST,
                status=UserStatus.ACTIVE,
                created_at=datetime.now() - timedelta(days=60),
                last_login=datetime.now() - timedelta(minutes=30),
                permissions=[
                    Permission.EVENTS_VIEW, Permission.EVENTS_MANAGE,
                    Permission.ALERTS_VIEW, Permission.EXPORT_DATA
                ],
                activities=[
                    UserActivity(timestamp=datetime.now() - timedelta(minutes=30), action="Login", details="Successful login"),
                    UserActivity(timestamp=datetime.now() - timedelta(hours=4), action="Export", details="Exported events data"),
                    UserActivity(timestamp=datetime.now() - timedelta(days=3), action="Report Generated", details="Generated weekly report"),
                ]
            ),
            User(
                id=str(uuid.uuid4()),
                username="operator2",
                email="operator2@sentinelai.com",
                role=UserRole.OPERATOR,
                status=UserStatus.INACTIVE,
                created_at=datetime.now() - timedelta(days=120),
                last_login=datetime.now() - timedelta(days=30),
                permissions=[
                    Permission.CAMERA_VIEW, Permission.CAMERA_MANAGE,
                    Permission.ALERTS_VIEW, Permission.ALERTS_MANAGE
                ],
                activities=[
                    UserActivity(timestamp=datetime.now() - timedelta(days=30), action="Login", details="Successful login"),
                ]
            ),
            User(
                id=str(uuid.uuid4()),
                username="viewer2",
                email="viewer2@sentinelai.com",
                role=UserRole.VIEWER,
                status=UserStatus.PENDING,
                created_at=datetime.now() - timedelta(days=7),
                last_login=None,
                permissions=[
                    Permission.CAMERA_VIEW, Permission.ALERTS_VIEW
                ],
                activities=[
                    UserActivity(timestamp=datetime.now() - timedelta(days=7), action="Account Created", details="Account pending activation"),
                ]
            )
        ]
        
        for user in demo_users:
            self._users[user.id] = user
    
    def get_all_users(self) -> List[User]:
        """Récupère tous les utilisateurs."""
        return sorted(self._users.values(), key=lambda u: u.created_at, reverse=True)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Récupère un utilisateur par ID."""
        return self._users.get(user_id)
    
    def add_user(self, user: User) -> User:
        """Ajoute un nouvel utilisateur."""
        self._users[user.id] = user
        return user
    
    def create_user(
        self,
        username: str,
        email: str,
        role: UserRole,
        status: UserStatus = UserStatus.PENDING
    ) -> User:
        """Crée un nouvel utilisateur."""
        permissions = self._get_default_permissions(role)
        
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            role=role,
            status=status,
            created_at=datetime.now(),
            permissions=permissions,
            activities=[
                UserActivity(timestamp=datetime.now(), action="Account Created", details="Account created")
            ]
        )
        self._users[user.id] = user
        return user
    
    def _get_default_permissions(self, role: UserRole) -> List[Permission]:
        """Récupère les permissions par défaut pour un rôle."""
        if role == UserRole.ADMIN:
            return list(Permission)
        if role == UserRole.OPERATOR:
            return [
                Permission.CAMERA_VIEW, Permission.CAMERA_MANAGE,
                Permission.ALERTS_VIEW, Permission.ALERTS_MANAGE,
                Permission.EVENTS_VIEW, Permission.EVENTS_MANAGE
            ]
        if role == UserRole.ANALYST:
            return [
                Permission.EVENTS_VIEW, Permission.EVENTS_MANAGE,
                Permission.ALERTS_VIEW, Permission.EXPORT_DATA
            ]
        if role == UserRole.VIEWER:
            return [
                Permission.CAMERA_VIEW, Permission.ALERTS_VIEW, Permission.EVENTS_VIEW
            ]
        return []
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Met à jour un utilisateur."""
        user = self._users.get(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Supprime un utilisateur."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Récupère les utilisateurs par rôle."""
        return [u for u in self._users.values() if u.role == role]
    
    def get_users_by_status(self, status: UserStatus) -> List[User]:
        """Récupère les utilisateurs par statut."""
        return [u for u in self._users.values() if u.status == status]
    
    def search_users(self, query: str) -> List[User]:
        """Recherche des utilisateurs."""
        query = query.lower()
        return [
            u for u in self._users.values()
            if query in u.username.lower() or query in u.email.lower()
        ]
    
    def get_user_statistics(self) -> Dict[str, int]:
        """Récupère les statistiques des utilisateurs."""
        total = len(self._users)
        active = len(self.get_users_by_status(UserStatus.ACTIVE))
        inactive = len(self.get_users_by_status(UserStatus.INACTIVE))
        pending = len(self.get_users_by_status(UserStatus.PENDING))
        suspended = len(self.get_users_by_status(UserStatus.SUSPENDED))
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "pending": pending,
            "suspended": suspended
        }
