"""
Point d'entrée principal de l'application desktop SentinelAI.
"""

import os
import sys
from pathlib import Path

# Fix pour conflit DLL Intel OpenMP / PyTorch sous Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

try:
    import torch
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.desktop.main_window import MainWindow
from app.desktop.camera_manager import get_camera_manager
from app.desktop.observability import get_observability_service
from app.desktop.health_service import get_health_service
from app.events.event_bus import get_event_bus
from app.core.config_loader import get_config_loader
from app.version import get_version


def main():
    """Point d'entrée principal de l'application."""
    
    # Créer l'application
    app = QApplication(sys.argv)
    app.setApplicationName("SentinelAI")
    app.setOrganizationName("Axyris")
    
    # Configuration du style
    app.setStyle("Fusion")
    
    # Configuration de la police
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Charger la configuration
    config_loader = get_config_loader()
    config_loader.load_all()
    
    # Initialiser les services
    event_bus = get_event_bus()
    observability = get_observability_service()
    health_service = get_health_service()
    camera_manager = get_camera_manager()
    
    # Afficher les informations de version
    version = get_version()
    print(f"SentinelAI {version.app_version} (Build {version.build_number})")
    print(f"Version Python: {version.python_version}")
    print(f"Système: {version.os_name} {version.os_version}")
    
    # Créer et afficher la fenêtre principale
    window = MainWindow()
    window.show()
    
    # Exécuter l'application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
