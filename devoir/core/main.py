"""
Point d'entrée principal du système de détection de chutes.
"""

import sys
import logging
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from database.models import init_db
from utils.logger import setup_logger

def main():
    """Fonction principale du système."""
    
    # Configuration du logging
    logger = setup_logger(__name__)
    logger.info("Démarrage du système de détection de chutes")
    
    # Initialisation de la base de données
    try:
        db_path = settings.DATA_DIR / "db" / "fall_detection.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        engine = init_db(str(db_path))
        logger.info(f"Base de données initialisée: {db_path}")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        return
    
    logger.info("Système prêt")
    logger.info(f"Mode debug: {settings.DEBUG}")
    logger.info(f"API: {settings.API_HOST}:{settings.API_PORT}")

if __name__ == "__main__":
    main()
