"""
Exceptions personnalisées pour le backend unifié.
"""


class SentinelException(Exception):
    """Exception de base pour Sentinel AI."""
    pass


class DatabaseException(SentinelException):
    """Exception liée à la base de données."""
    pass


class AuthenticationException(SentinelException):
    """Exception liée à l'authentification."""
    pass


class AuthorizationException(SentinelException):
    """Exception liée à l'autorisation."""
    pass


class DetectionException(SentinelException):
    """Exception liée à la détection IA."""
    pass


class NotificationException(SentinelException):
    """Exception liée aux notifications."""
    pass


class ValidationException(SentinelException):
    """Exception liée à la validation des données."""
    pass


class ConfigurationException(SentinelException):
    """Exception liée à la configuration."""
    pass


class RateLimitException(SentinelException):
    """Exception liée au rate limiting."""
    pass
