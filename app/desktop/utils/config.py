"""
Utilitaires de configuration.
Gestion des paramètres de l'application desktop.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class DesktopConfig:
    """Configuration de l'application desktop."""
    api_base_url: str = "http://localhost:8000/api/v1"
    websocket_url: str = "ws://localhost:8000/ws"
    auto_reconnect: bool = True
    reconnect_interval: int = 5  # secondes
    theme: str = "dark"
    language: str = "fr"
    remember_credentials: bool = False
    auto_start_detection: bool = False
    default_camera_resolution: str = "640x480"
    default_fps: int = 30
    enable_notifications: bool = True
    notification_sound: bool = True
    log_level: str = "INFO"
    
    def save(self, path: Optional[Path] = None):
        """
        Sauvegarde la configuration dans un fichier JSON.
        
        Args:
            path: Chemin du fichier de configuration
        """
        if path is None:
            path = Path.home() / ".surveillance_ia" / "config.json"
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=4, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: Optional[Path] = None) -> 'DesktopConfig':
        """
        Charge la configuration depuis un fichier JSON.
        
        Args:
            path: Chemin du fichier de configuration
        
        Returns:
            Configuration chargée ou configuration par défaut
        """
        if path is None:
            path = Path.home() / ".surveillance_ia" / "config.json"
        
        if not path.exists():
            return cls()
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        except (json.JSONDecodeError, TypeError):
            return cls()


class ConfigManager:
    """
    Gestionnaire de configuration.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de configuration."""
        self.config = DesktopConfig.load()
        self.config_path = Path.home() / ".surveillance_ia" / "config.json"
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.
        
        Args:
            key: Clé de configuration
            default: Valeur par défaut
        
        Returns:
            Valeur de configuration
        """
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """
        Définit une valeur de configuration.
        
        Args:
            key: Clé de configuration
            value: Nouvelle valeur
        """
        setattr(self.config, key, value)
        self.save()
    
    def save(self):
        """Sauvegarde la configuration."""
        self.config.save(self.config_path)
    
    def reload(self):
        """Recharge la configuration depuis le fichier."""
        self.config = DesktopConfig.load(self.config_path)
