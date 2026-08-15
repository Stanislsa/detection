"""
Logger centralisé avec configuration structurée.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from .config import settings


def setup_logging():
    """Configure le logging global de l'application."""
    
    # Créer le répertoire de logs si nécessaire
    log_dir = Path(settings.LOGS_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configuration du root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (si activé)
    if settings.LOG_FILE:
        file_handler = RotatingFileHandler(
            log_dir / "sentinel_ai.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Réduire le bruit des loggers externes
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Retourne un logger avec le nom spécifié.
    
    Args:
        name: Nom du logger (généralement __name__)
    
    Returns:
        Instance de Logger configurée
    """
    return logging.getLogger(name)


# Initialiser le logging au chargement du module
setup_logging()
