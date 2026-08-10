"""
Exceptions personnalisées de l'application.
"""


class SurveillanceException(Exception):
    """Exception de base pour l'application."""
    pass


class APIException(SurveillanceException):
    """Exception liée à l'API."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)


class AuthenticationException(SurveillanceException):
    """Exception liée à l'authentification."""
    pass


class CameraException(SurveillanceException):
    """Exception liée aux caméras."""
    pass


class DetectionException(SurveillanceException):
    """Exception liée à la détection IA."""
    pass


class WebSocketException(SurveillanceException):
    """Exception liée au WebSocket."""
    pass


class StorageException(SurveillanceException):
    """Exception liée au stockage."""
    pass


class WorkerException(SurveillanceException):
    """Exception liée aux workers."""
    pass


class ValidationException(SurveillanceException):
    """Exception liée à la validation des données."""
    pass


class ConfigurationException(SurveillanceException):
    """Exception liée à la configuration."""
    pass
