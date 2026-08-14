"""
Fenêtre principale de l'application.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QUrl
from PyQt6.QtQml import QQmlApplicationEngine

# Force le style Basic pour éviter les problèmes de DLL Windows
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"


class MainWindow(QMainWindow):
    """Fenêtre principale SentinelAI."""

    MIN_WIDTH = 1024
    MIN_HEIGHT = 768

    def __init__(self):
        super().__init__()
        self._engine = None
        self._setup_window()
        self._setup_qml_engine()

    def _setup_window(self):
        """Configure les propriétés de la fenêtre."""
        self.setWindowTitle("SentinelAI")
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.resize(1280, 800)

    def _setup_qml_engine(self):
        """Configure le moteur QML et charge le fichier principal."""
        self._engine = QQmlApplicationEngine()
        
        # Ajoute le chemin QML pour les imports
        qml_path = Path(__file__).parent / "qml"
        self._engine.addImportPath(str(qml_path))
        
        # Chemin vers le fichier QML principal
        qml_file = Path(__file__).parent / "qml" / "Main.qml"
        self._engine.load(QUrl.fromLocalFile(str(qml_file)))

        if not self._engine.rootObjects():
            raise RuntimeError("Failed to load QML file")

    def closeEvent(self, event):
        """Gère proprement la fermeture de la fenêtre."""
        if self._engine:
            self._engine.deleteLater()
        event.accept()
