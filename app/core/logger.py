"""
Configuration centralisée du logger pour l'application.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from app.core.constants import STORAGE_DIR_NAME, CACHE_DIR


class LoggerConfig:
    """
    Configuration du logger avec rotation des fichiers et niveaux personnalisés.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logger()
            self._initialized = True
    
    def _setup_logger(self):
        """Configure le logger global de l'application."""
        # Créer le dossier de logs
        log_dir = Path.home() / STORAGE_DIR_NAME / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Nom du fichier avec date
        log_file = log_dir / f"surveillance_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Configuration du logger racine
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Format des logs
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler fichier (DEBUG)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Handler console (INFO)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Récupère un logger avec le nom spécifié.
        
        Args:
            name: Nom du logger (généralement __name__)
        
        Returns:
            Logger configuré
        """
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    """
    Fonction utilitaire pour récupérer un logger.
    
    Args:
        name: Nom du logger
    
    Returns:
        Logger configuré
    """
    LoggerConfig()
    return logging.getLogger(name)
