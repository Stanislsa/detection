"""
Configuration centralisée de l'application.
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any

from app.core.constants import (
    DEFAULT_API_BASE_URL,
    DEFAULT_WS_URL,
    CONFIG_DIR_NAME,
    CONFIG_FILE_NAME,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    DETECTION_CONFIDENCE_THRESHOLD,
    FALL_CONFIDENCE_THRESHOLD,
    DEFAULT_FPS,
    DEFAULT_RESOLUTION,
    WS_RECONNECT_DELAY,
    WS_MAX_RECONNECT_ATTEMPTS,
    MAX_WORKER_THREADS,
)


@dataclass
class APISettings:
    """Configuration de l'API."""
    base_url: str = DEFAULT_API_BASE_URL
    timeout: int = 30
    verify_ssl: bool = True


@dataclass
class WebSocketSettings:
    """Configuration du WebSocket."""
    url: str = DEFAULT_WS_URL
    reconnect_delay: int = WS_RECONNECT_DELAY
    max_reconnect_attempts: int = WS_MAX_RECONNECT_ATTEMPTS


@dataclass
class DetectionSettings:
    """Configuration de la détection IA."""
    confidence_threshold: float = DETECTION_CONFIDENCE_THRESHOLD
    fall_confidence_threshold: float = FALL_CONFIDENCE_THRESHOLD
    enable_fall_detection: bool = True
    enable_intrusion_detection: bool = True
    enable_movement_detection: bool = True


@dataclass
class VideoSettings:
    """Configuration vidéo."""
    default_fps: int = DEFAULT_FPS
    default_resolution: str = DEFAULT_RESOLUTION
    enable_recording: bool = True
    recording_format: str = "mp4"
    recording_quality: str = "high"  # low, medium, high


@dataclass
class NotificationSettings:
    """Configuration des notifications."""
    enable_toast: bool = True
    enable_sound: bool = True
    enable_desktop: bool = True
    sound_file: Optional[str] = None


@dataclass
class StorageSettings:
    """Configuration du stockage."""
    snapshots_dir: str = "snapshots"
    recordings_dir: str = "recordings"
    reports_dir: str = "reports"
    exports_dir: str = "exports"
    cache_dir: str = "cache"
    max_storage_gb: int = 100
    auto_cleanup_days: int = 30


@dataclass
class UISettings:
    """Configuration de l'interface."""
    theme: str = "dark"  # dark, light
    language: str = "fr"  # fr, en
    auto_refresh_interval: int = 5  # secondes
    show_camera_previews: bool = True


@dataclass
class Settings:
    """Configuration principale de l'application."""
    api: APISettings = field(default_factory=APISettings)
    websocket: WebSocketSettings = field(default_factory=WebSocketSettings)
    detection: DetectionSettings = field(default_factory=DetectionSettings)
    video: VideoSettings = field(default_factory=VideoSettings)
    notification: NotificationSettings = field(default_factory=NotificationSettings)
    storage: StorageSettings = field(default_factory=StorageSettings)
    ui: UISettings = field(default_factory=UISettings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit les settings en dictionnaire."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """Crée les settings depuis un dictionnaire."""
        return cls(
            api=APISettings(**data.get('api', {})),
            websocket=WebSocketSettings(**data.get('websocket', {})),
            detection=DetectionSettings(**data.get('detection', {})),
            video=VideoSettings(**data.get('video', {})),
            notification=NotificationSettings(**data.get('notification', {})),
            storage=StorageSettings(**data.get('storage', {})),
            ui=UISettings(**data.get('ui', {})),
        )


class SettingsManager:
    """
    Gestionnaire de configuration avec persistance.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._settings: Optional[Settings] = None
        self._config_path: Path = Path.home() / CONFIG_DIR_NAME / CONFIG_FILE_NAME
    
    def load(self) -> Settings:
        """
        Charge la configuration depuis le fichier.
        
        Returns:
            Settings chargés ou défaut
        """
        if self._config_path.exists():
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._settings = Settings.from_dict(data)
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                from app.core.logger import get_logger
                logger = get_logger(__name__)
                logger.warning(f"Erreur lors du chargement de la config: {e}. Utilisation des valeurs par défaut.")
                self._settings = Settings()
        else:
            self._settings = Settings()
        
        return self._settings
    
    def save(self, settings: Settings = None) -> bool:
        """
        Sauvegarde la configuration dans le fichier.
        
        Args:
            settings: Settings à sauvegarder (sinon utilise les actuels)
        
        Returns:
            True si succès
        """
        if settings:
            self._settings = settings
        
        if self._settings is None:
            return False
        
        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings.to_dict(), f, indent=4, ensure_ascii=False)
            return True
        except (IOError, TypeError) as e:
            from app.core.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Erreur lors de la sauvegarde de la config: {e}")
            return False
    
    @property
    def settings(self) -> Settings:
        """Retourne les settings actuels (charge si nécessaire)."""
        if self._settings is None:
            return self.load()
        return self._settings
    
    def reset(self) -> Settings:
        """Réinitialise aux valeurs par défaut."""
        self._settings = Settings()
        self.save()
        return self._settings


def get_settings() -> Settings:
    """
    Fonction utilitaire pour récupérer les settings.
    
    Returns:
        Settings actuels
    """
    manager = SettingsManager()
    return manager.settings
