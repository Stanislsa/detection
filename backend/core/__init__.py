"""
Core module - Configuration, exceptions, logging, constants.
"""

from .config import settings
from .exceptions import (
    SentinelException,
    DatabaseException,
    AuthenticationException,
    AuthorizationException,
    DetectionException,
    NotificationException
)
from .logger import get_logger

__all__ = [
    "settings",
    "SentinelException",
    "DatabaseException", 
    "AuthenticationException",
    "AuthorizationException",
    "DetectionException",
    "NotificationException",
    "get_logger"
]
