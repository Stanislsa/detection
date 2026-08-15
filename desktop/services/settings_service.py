"""
Service pour la gestion des paramètres système.
"""

from typing import Optional, Dict, Any
import json
import os

from app.desktop.models.settings_model import (
    SystemSettings, GeneralSettings, CameraSettings, AISettings,
    NotificationSettings, StorageSettings, SecuritySettings
)


class SettingsService:
    """Service de gestion des paramètres système."""
    
    def __init__(self, config_path: Optional[str] = None):
        self._config_path = config_path or os.path.join(
            os.path.expanduser("~"),
            ".sentinelai",
            "settings.json"
        )
        self._settings = self._load_settings()
    
    def _load_settings(self) -> SystemSettings:
        """Charge les paramètres depuis le fichier."""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    data = json.load(f)
                    return SystemSettings.from_dict(data)
            except Exception as e:
                print(f"Error loading settings: {e}")
        return SystemSettings()
    
    def _save_settings(self) -> bool:
        """Sauvegarde les paramètres vers le fichier."""
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, 'w') as f:
                json.dump(self._settings.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_all_settings(self) -> SystemSettings:
        """Récupère tous les paramètres."""
        return self._settings
    
    def get_general_settings(self) -> GeneralSettings:
        """Récupère les paramètres généraux."""
        return self._settings.general
    
    def get_camera_settings(self) -> CameraSettings:
        """Récupère les paramètres de caméra."""
        return self._settings.camera
    
    def get_ai_settings(self) -> AISettings:
        """Récupère les paramètres IA."""
        return self._settings.ai
    
    def get_notification_settings(self) -> NotificationSettings:
        """Récupère les paramètres de notification."""
        return self._settings.notification
    
    def get_storage_settings(self) -> StorageSettings:
        """Récupère les paramètres de stockage."""
        return self._settings.storage
    
    def get_security_settings(self) -> SecuritySettings:
        """Récupère les paramètres de sécurité."""
        return self._settings.security
    
    def update_general_settings(self, settings: GeneralSettings) -> bool:
        """Met à jour les paramètres généraux."""
        self._settings.general = settings
        return self._save_settings()
    
    def update_camera_settings(self, settings: CameraSettings) -> bool:
        """Met à jour les paramètres de caméra."""
        self._settings.camera = settings
        return self._save_settings()
    
    def update_ai_settings(self, settings: AISettings) -> bool:
        """Met à jour les paramètres IA."""
        self._settings.ai = settings
        return self._save_settings()
    
    def update_notification_settings(self, settings: NotificationSettings) -> bool:
        """Met à jour les paramètres de notification."""
        self._settings.notification = settings
        return self._save_settings()
    
    def update_storage_settings(self, settings: StorageSettings) -> bool:
        """Met à jour les paramètres de stockage."""
        self._settings.storage = settings
        return self._save_settings()
    
    def update_security_settings(self, settings: SecuritySettings) -> bool:
        """Met à jour les paramètres de sécurité."""
        self._settings.security = settings
        return self._save_settings()
    
    def reset_to_defaults(self) -> bool:
        """Réinitialise tous les paramètres aux valeurs par défaut."""
        self._settings = SystemSettings()
        return self._save_settings()
