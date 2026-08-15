"""
Role-Based Access Control (RBAC) system.
"""

from typing import List, Set, Dict, Optional
from enum import Enum
from functools import lru_cache

from backend.core.logger import get_logger

logger = get_logger(__name__)


class Permission(Enum):
    """Available permissions in the system."""
    # User management
    READ_USER = "read_user"
    WRITE_USER = "write_user"
    DELETE_USER = "delete_user"
    
    # Person management
    READ_PERSON = "read_person"
    WRITE_PERSON = "write_person"
    DELETE_PERSON = "delete_person"
    
    # Camera management
    READ_CAMERA = "read_camera"
    WRITE_CAMERA = "write_camera"
    DELETE_CAMERA = "delete_camera"
    
    # Fall event management
    READ_FALL = "read_fall"
    WRITE_FALL = "write_fall"
    DELETE_FALL = "delete_fall"
    
    # Alert management
    READ_ALERT = "read_alert"
    WRITE_ALERT = "write_alert"
    
    # Dashboard access
    READ_DASHBOARD = "read_dashboard"
    
    # System management
    MANAGE_USERS = "manage_users"
    MANAGE_CONFIG = "manage_config"
    MANAGE_SECURITY = "manage_security"


class Role(Enum):
    """User roles."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    FAMILY = "family"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Full access
        Permission.READ_USER, Permission.WRITE_USER, Permission.DELETE_USER,
        Permission.READ_PERSON, Permission.WRITE_PERSON, Permission.DELETE_PERSON,
        Permission.READ_CAMERA, Permission.WRITE_CAMERA, Permission.DELETE_CAMERA,
        Permission.READ_FALL, Permission.WRITE_FALL, Permission.DELETE_FALL,
        Permission.READ_ALERT, Permission.WRITE_ALERT,
        Permission.READ_DASHBOARD,
        Permission.MANAGE_USERS, Permission.MANAGE_CONFIG, Permission.MANAGE_SECURITY
    },
    Role.OPERATOR: {
        # Operational access (no user management)
        Permission.READ_USER,
        Permission.READ_PERSON, Permission.WRITE_PERSON,
        Permission.READ_CAMERA, Permission.WRITE_CAMERA,
        Permission.READ_FALL, Permission.WRITE_FALL,
        Permission.READ_ALERT, Permission.WRITE_ALERT,
        Permission.READ_DASHBOARD,
        Permission.MANAGE_CONFIG
    },
    Role.VIEWER: {
        # Read-only access
        Permission.READ_USER,
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
    """
    Role-Based Access Control manager.
    
    In production, store role assignments in database.
    """
    
    def __init__(self):
        """Initialize RBAC manager."""
        self.user_roles: Dict[str, Role] = {}
        self.user_permissions: Dict[str, Set[Permission]] = {}
        logger.info("RBAC manager initialized")
    
    def assign_role(self, user_id: str, role: Role):
        """
        Assign a role to a user.
        
        Args:
            user_id: User ID
            role: Role to assign
        """
        self.user_roles[user_id] = role
        self.user_permissions[user_id] = ROLE_PERMISSIONS[role]
        logger.info(f"Role {role.value} assigned to user {user_id}")
    
    def get_user_role(self, user_id: str) -> Optional[Role]:
        """
        Get user's role.
        
        Args:
            user_id: User ID
        
        Returns:
            Role or None
        """
        return self.user_roles.get(user_id)
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user_id: User ID
            permission: Permission to check
        
        Returns:
            True if user has permission
        """
        user_permissions = self.user_permissions.get(user_id, set())
        return permission in user_permissions
    
    def has_any_permission(self, user_id: str, permissions: List[Permission]) -> bool:
        """
        Check if user has at least one of the permissions.
        
        Args:
            user_id: User ID
            permissions: List of permissions
        
        Returns:
            True if user has at least one permission
        """
        user_permissions = self.user_permissions.get(user_id, set())
        return any(perm in user_permissions for perm in permissions)
    
    def has_all_permissions(self, user_id: str, permissions: List[Permission]) -> bool:
        """
        Check if user has all the permissions.
        
        Args:
            user_id: User ID
            permissions: List of permissions
        
        Returns:
            True if user has all permissions
        """
        user_permissions = self.user_permissions.get(user_id, set())
        return all(perm in user_permissions for perm in permissions)
    
    def remove_role(self, user_id: str):
        """
        Remove user's role.
        
        Args:
            user_id: User ID
        """
        if user_id in self.user_roles:
            del self.user_roles[user_id]
        if user_id in self.user_permissions:
            del self.user_permissions[user_id]
        logger.info(f"Role removed from user {user_id}")
    
    def get_all_permissions(self, user_id: str) -> Set[Permission]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Set of permissions
        """
        return self.user_permissions.get(user_id, set())
    
    def get_role_permissions(self, role: Role) -> Set[Permission]:
        """
        Get all permissions for a role.
        
        Args:
            role: Role
        
        Returns:
            Set of permissions
        """
        return ROLE_PERMISSIONS.get(role, set())


# Permission decorators for FastAPI
def require_permission(permission: Permission):
    """
    Decorator to require a specific permission.
    
    Args:
        permission: Required permission
    
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # In FastAPI, user_id would come from token
            user_id = kwargs.get('user_id')
            
            if not user_id:
                from backend.core.exceptions import AuthorizationException
                raise AuthorizationException("User ID required")
            
            if not rbac_manager.has_permission(str(user_id), permission):
                from backend.core.exceptions import AuthorizationException
                raise AuthorizationException(f"Permission {permission.value} required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: Role):
    """
    Decorator to require a specific role.
    
    Args:
        role: Required role
    
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            
            if not user_id:
                from backend.core.exceptions import AuthorizationException
                raise AuthorizationException("User ID required")
            
            if rbac_manager.get_user_role(str(user_id)) != role:
                from backend.core.exceptions import AuthorizationException
                raise AuthorizationException(f"Role {role.value} required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Global RBAC manager instance
rbac_manager = RBACManager()
