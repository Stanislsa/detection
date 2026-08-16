"""Exceptions personnalisées + schéma d'erreur unifié."""
from __future__ import annotations
from typing import Any, Dict, Optional

class SentinelException(Exception):
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"
    def __init__(self, message: Optional[str] = None, *, error_code: Optional[str] = None,
                 status_code: Optional[int] = None, details: Any = None):
        self.message = message or self.__class__.message
        self.error_code = error_code or self.__class__.error_code
        self.status_code = status_code or self.__class__.status_code
        self.details = details
        super().__init__(self.message)
    def to_dict(self) -> Dict[str, Any]:
        body: Dict[str, Any] = {"error": {"code": self.error_code, "message": self.message}}
        if self.details is not None: body["error"]["details"] = self.details
        return body

class DatabaseException(SentinelException):
    status_code=500; error_code="DATABASE_ERROR"; message="Database operation failed"
class AuthenticationException(SentinelException):
    status_code=401; error_code="AUTHENTICATION_FAILED"; message="Authentication failed"
class AuthorizationException(SentinelException):
    status_code=403; error_code="FORBIDDEN"; message="Insufficient permissions"
class DetectionException(SentinelException):
    status_code=500; error_code="DETECTION_ERROR"; message="AI detection failed"
class NotificationException(SentinelException):
    status_code=502; error_code="NOTIFICATION_ERROR"; message="Notification delivery failed"
class ValidationException(SentinelException):
    status_code=422; error_code="VALIDATION_ERROR"; message="Validation failed"
class ConfigurationException(SentinelException):
    status_code=500; error_code="CONFIGURATION_ERROR"; message="Invalid configuration"
class RateLimitException(SentinelException):
    status_code=429; error_code="RATE_LIMITED"; message="Too many requests"
class NotFoundException(SentinelException):
    status_code=404; error_code="NOT_FOUND"; message="Resource not found"
class ConflictException(SentinelException):
    status_code=409; error_code="CONFLICT"; message="Resource conflict"
class ServiceUnavailableException(SentinelException):
    status_code=503; error_code="SERVICE_UNAVAILABLE"; message="Service temporarily unavailable"
class TelegramException(NotificationException):
    error_code="TELEGRAM_ERROR"; message="Telegram operation failed"
class ModelNotLoadedException(DetectionException):
    status_code=503; error_code="MODEL_NOT_LOADED"; message="AI model is not loaded"
class CameraException(SentinelException):
    status_code=400; error_code="CAMERA_ERROR"; message="Camera operation failed"
