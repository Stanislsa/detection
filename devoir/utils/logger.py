"""
Logging centralisé pour le système de détection de chutes.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config import settings

def setup_logger(name: str) -> logging.Logger:
    """
    Configure et retourne un logger avec handlers console et fichier.
    
    Args:
        name: Nom du logger (généralement __name__)
    
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Format du log
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler fichier avec rotation
    logs_dir = settings.LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        logs_dir / "fall_detection.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger existant ou en crée un nouveau.
    
    Args:
        name: Nom du logger
    
    Returns:
        Logger
    """
    return logging.getLogger(name)
