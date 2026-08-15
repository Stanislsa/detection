"""
API module - FastAPI routers and endpoints.
"""

from .router import api_router
from .dependencies import (
    get_db,
    get_current_user,
    require_admin,
    require_permission
)

__all__ = [
    "api_router",
    "get_db",
    "get_current_user", 
    "require_admin",
    "require_permission"
]
