"""
Modèle de données pour les paramètres système.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum


class SettingsCategory(Enum):
    """Catégories de paramètres."""
    GENERAL = "general"
    CAMERA = "camera"
    AI = "ai"
    NOTIFICATION = "notification"
    STORAGE = "storage"
    SECURITY = "security"


@dataclass
class GeneralSettings:
    """Paramètres généraux."""
    application_name: str = "SentinelAI"
    theme: str = "dark"
    language: str = "en"
    auto_update: bool = True
    debug_mode: bool = False
    log_level: str = "info"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "application_name": self.application_name,
            "theme": self.theme,
            "language": self.language,
            "auto_update": self.auto_update,
            "debug_mode": self.debug_mode,
            "log_level": self.log_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeneralSettings":
        return cls(
            application_name=data.get("application_name", "SentinelAI"),
            theme=data.get("theme", "dark"),
            language=data.get("language", "en"),
            auto_update=data.get("auto_update", True),
            debug_mode=data.get("debug_mode", False),
            log_level=data.get("log_level", "info")
        )


@dataclass
class CameraSettings:
    """Paramètres de caméra."""
    default_resolution: str = "1080p"
    default_fps: int = 30
    auto_reconnect: bool = True
    reconnect_interval: int = 30
    recording_enabled: bool = True
    retention_days: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "default_resolution": self.default_resolution,
            "default_fps": self.default_fps,
            "auto_reconnect": self.auto_reconnect,
            "reconnect_interval": self.reconnect_interval,
            "recording_enabled": self.recording_enabled,
            "retention_days": self.retention_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CameraSettings":
        return cls(
            default_resolution=data.get("default_resolution", "1080p"),
            default_fps=data.get("default_fps", 30),
            auto_reconnect=data.get("auto_reconnect", True),
            reconnect_interval=data.get("reconnect_interval", 30),
            recording_enabled=data.get("recording_enabled", True),
            retention_days=data.get("retention_days", 30)
        )


@dataclass
class AISettings:
    """Paramètres IA."""
    model_name: str = "yolov8"
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.45
    max_detections: int = 100
    enable_pose_estimation: bool = True
    enable_face_recognition: bool = False
    inference_device: str = "cpu"  # cpu, gpu, tpu
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "confidence_threshold": self.confidence_threshold,
            "nms_threshold": self.nms_threshold,
            "max_detections": self.max_detections,
            "enable_pose_estimation": self.enable_pose_estimation,
            "enable_face_recognition": self.enable_face_recognition,
            "inference_device": self.inference_device
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AISettings":
        return cls(
            model_name=data.get("model_name", "yolov8"),
            confidence_threshold=data.get("confidence_threshold", 0.5),
            nms_threshold=data.get("nms_threshold", 0.45),
            max_detections=data.get("max_detections", 100),
            enable_pose_estimation=data.get("enable_pose_estimation", True),
            enable_face_recognition=data.get("enable_face_recognition", False),
            inference_device=data.get("inference_device", "cpu")
        )


@dataclass
class NotificationSettings:
    """Paramètres de notification."""
    email_enabled: bool = True
    email_address: str = ""
    sms_enabled: bool = False
    sms_number: str = ""
    push_enabled: bool = True
    critical_only: bool = False
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "email_enabled": self.email_enabled,
            "email_address": self.email_address,
            "sms_enabled": self.sms_enabled,
            "sms_number": self.sms_number,
            "push_enabled": self.push_enabled,
            "critical_only": self.critical_only,
            "quiet_hours_enabled": self.quiet_hours_enabled,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotificationSettings":
        return cls(
            email_enabled=data.get("email_enabled", True),
            email_address=data.get("email_address", ""),
            sms_enabled=data.get("sms_enabled", False),
            sms_number=data.get("sms_number", ""),
            push_enabled=data.get("push_enabled", True),
            critical_only=data.get("critical_only", False),
            quiet_hours_enabled=data.get("quiet_hours_enabled", False),
            quiet_hours_start=data.get("quiet_hours_start", "22:00"),
            quiet_hours_end=data.get("quiet_hours_end", "08:00")
        )


@dataclass
class StorageSettings:
    """Paramètres de stockage."""
    storage_path: str = "/var/lib/sentinelai/storage"
    max_storage_gb: int = 1000
    auto_cleanup: bool = True
    cleanup_threshold: int = 90
    backup_enabled: bool = True
    backup_path: str = "/var/lib/sentinelai/backups"
    backup_schedule: str = "daily"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "storage_path": self.storage_path,
            "max_storage_gb": self.max_storage_gb,
            "auto_cleanup": self.auto_cleanup,
            "cleanup_threshold": self.cleanup_threshold,
            "backup_enabled": self.backup_enabled,
            "backup_path": self.backup_path,
            "backup_schedule": self.backup_schedule
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StorageSettings":
        return cls(
            storage_path=data.get("storage_path", "/var/lib/sentinelai/storage"),
            max_storage_gb=data.get("max_storage_gb", 1000),
            auto_cleanup=data.get("auto_cleanup", True),
            cleanup_threshold=data.get("cleanup_threshold", 90),
            backup_enabled=data.get("backup_enabled", True),
            backup_path=data.get("backup_path", "/var/lib/sentinelai/backups"),
            backup_schedule=data.get("backup_schedule", "daily")
        )


@dataclass
class SecuritySettings:
    """Paramètres de sécurité."""
    session_timeout: int = 30
    max_login_attempts: int = 5
    lockout_duration: int = 15
    two_factor_enabled: bool = False
    password_min_length: int = 8
    password_require_special: bool = True
    password_require_number: bool = True
    audit_logging: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_timeout": self.session_timeout,
            "max_login_attempts": self.max_login_attempts,
            "lockout_duration": self.lockout_duration,
            "two_factor_enabled": self.two_factor_enabled,
            "password_min_length": self.password_min_length,
            "password_require_special": self.password_require_special,
            "password_require_number": self.password_require_number,
            "audit_logging": self.audit_logging
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecuritySettings":
        return cls(
            session_timeout=data.get("session_timeout", 30),
            max_login_attempts=data.get("max_login_attempts", 5),
            lockout_duration=data.get("lockout_duration", 15),
            two_factor_enabled=data.get("two_factor_enabled", False),
            password_min_length=data.get("password_min_length", 8),
            password_require_special=data.get("password_require_special", True),
            password_require_number=data.get("password_require_number", True),
            audit_logging=data.get("audit_logging", True)
        )


@dataclass
class SystemSettings:
    """Paramètres système complets."""
    general: GeneralSettings = field(default_factory=GeneralSettings)
    camera: CameraSettings = field(default_factory=CameraSettings)
    ai: AISettings = field(default_factory=AISettings)
    notification: NotificationSettings = field(default_factory=NotificationSettings)
    storage: StorageSettings = field(default_factory=StorageSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "general": self.general.to_dict(),
            "camera": self.camera.to_dict(),
            "ai": self.ai.to_dict(),
            "notification": self.notification.to_dict(),
            "storage": self.storage.to_dict(),
            "security": self.security.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemSettings":
        return cls(
            general=GeneralSettings.from_dict(data.get("general", {})),
            camera=CameraSettings.from_dict(data.get("camera", {})),
            ai=AISettings.from_dict(data.get("ai", {})),
            notification=NotificationSettings.from_dict(data.get("notification", {})),
            storage=StorageSettings.from_dict(data.get("storage", {})),
            security=SecuritySettings.from_dict(data.get("security", {}))
        )
