"""
Contrôle d'accès basé sur les rôles (RBAC).

Gestion des permissions et des rôles utilisateurs.
"""

from typing import List, Set, Dict, Optional
from enum import Enum


class Permission(Enum):
    """Permissions disponibles dans le système."""
    READ_PERSON = "read_person"
    WRITE_PERSON = "write_person"
    DELETE_PERSON = "delete_person"
    
    READ_CAMERA = "read_camera"
    WRITE_CAMERA = "write_camera"
    DELETE_CAMERA = "delete_camera"
    
    READ_FALL = "read_fall"
    WRITE_FALL = "write_fall"
    DELETE_FALL = "delete_fall"
    
    READ_ALERT = "read_alert"
    WRITE_ALERT = "write_alert"
    
    READ_DASHBOARD = "read_dashboard"
    
    MANAGE_USERS = "manage_users"
    MANAGE_CONFIG = "manage_config"


class Role(Enum):
    """Rôles utilisateurs."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    FAMILY = "family"


# Mapping des rôles vers les permissions
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Full access
        Permission.READ_PERSON, Permission.WRITE_PERSON, Permission.DELETE_PERSON,
        Permission.READ_CAMERA, Permission.WRITE_CAMERA, Permission.DELETE_CAMERA,
        Permission.READ_FALL, Permission.WRITE_FALL, Permission.DELETE_FALL,
        Permission.READ_ALERT, Permission.WRITE_ALERT,
        Permission.READ_DASHBOARD,
        Permission.MANAGE_USERS, Permission.MANAGE_CONFIG
    },
    Role.OPERATOR: {
        # Operational access (no user management)
        Permission.READ_PERSON, Permission.WRITE_PERSON,
        Permission.READ_CAMERA, Permission.WRITE_CAMERA,
        Permission.READ_FALL, Permission.WRITE_FALL,
        Permission.READ_ALERT, Permission.WRITE_ALERT,
        Permission.READ_DASHBOARD,
        Permission.MANAGE_CONFIG
    },
    Role.VIEWER: {
        # Read-only access
        Permission.READ_PERSON,
        Permission.READ_CAMERA,
        Permission.READ_FALL,
        Permission.READ_ALERT,
        Permission.READ_DASHBOARD
    },
    Role.FAMILY: {
        # Limited access for family members
        Permission.READ_PERSON,
        Permission.READ_FALL,
        Permission.READ_ALERT,
        Permission.READ_DASHBOARD
    }
}


class RBACManager:
    """Gestionnaire RBAC."""
    
    def __init__(self):
        """Initialise le gestionnaire RBAC."""
        self.user_roles: Dict[str, Role] = {}
        self.user_permissions: Dict[str, Set[Permission]] = {}
    
    def assign_role(self, user_id: str, role: Role):
        """
        Assigne un rôle à un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            role: Rôle à assigner
        """
        self.user_roles[user_id] = role
        self.user_permissions[user_id] = ROLE_PERMISSIONS[role]
    
    def get_user_role(self, user_id: str) -> Optional[Role]:
        """
        Récupère le rôle d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Rôle ou None
        """
        return self.user_roles.get(user_id)
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Vérifie si un utilisateur a une permission.
        
        Args:
            user_id: ID de l'utilisateur
            permission: Permission à vérifier
        
        Returns:
            True si l'utilisateur a la permission
        """
        user_permissions = self.user_permissions.get(user_id, set())
        return permission in user_permissions
    
    def has_any_permission(self, user_id: str, permissions: List[Permission]) -> bool:
        """
        Vérifie si un utilisateur a au moins une des permissions.
        
        Args:
            user_id: ID de l'utilisateur
            permissions: Liste des permissions
        
        Returns:
            True si l'utilisateur a au moins une permission
        """
        user_permissions = self.user_permissions.get(user_id, set())
        return any(perm in user_permissions for perm in permissions)
    
    def has_all_permissions(self, user_id: str, permissions: List[Permission]) -> bool:
        """
        Vérifie si un utilisateur a toutes les permissions.
        
        Args:
            user_id: ID de l'utilisateur
            permissions: Liste des permissions
        
        Returns:
            True si l'utilisateur a toutes les permissions
        """
        user_permissions = self.user_permissions.get(user_id, set())
        return all(perm in user_permissions for perm in permissions)
    
    def remove_role(self, user_id: str):
        """
        Retire le rôle d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
        """
        if user_id in self.user_roles:
            del self.user_roles[user_id]
        if user_id in self.user_permissions:
            del self.user_permissions[user_id]
    
    def get_all_permissions(self, user_id: str) -> Set[Permission]:
        """
        Récupère toutes les permissions d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Ensemble des permissions
        """
        return self.user_permissions.get(user_id, set())


# Décorateur pour vérifier les permissions
def require_permission(permission: Permission):
    """
    Décorateur pour exiger une permission.
    
    Args:
        permission: Permission requise
    
    Returns:
        Décorateur
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Dans une implémentation FastAPI, on récupérerait l'user_id depuis le token
            user_id = kwargs.get('user_id')
            
            if not user_id:
                raise PermissionError("User ID required")
            
            rbac = kwargs.get('rbac_manager')
            
            if not rbac or not rbac.has_permission(user_id, permission):
                raise PermissionError(f"Permission {permission.value} required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role):
    """
    Décorateur pour exiger un rôle.
    
    Args:
        role: Rôle requis
    
    Returns:
        Décorateur
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            
            if not user_id:
                raise PermissionError("User ID required")
            
            rbac = kwargs.get('rbac_manager')
            
            if not rbac or rbac.get_user_role(user_id) != role:
                raise PermissionError(f"Role {role.value} required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
