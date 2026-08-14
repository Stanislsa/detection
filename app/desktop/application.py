"""
Application principale PyQt6 avec support QML.
"""

import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl

from app.desktop.controllers.auth_controller import AuthController
from app.desktop.controllers.alert_controller import AlertController
from app.desktop.controllers.camera_controller import CameraController
from app.desktop.controllers.video_pipeline_controller import VideoPipelineController
from app.desktop.controllers.event_controller import EventController
from app.desktop.controllers.notification_controller import NotificationController
from app.desktop.controllers.health_controller import HealthController
from app.desktop.controllers.settings_controller import SettingsController
from app.desktop.controllers.service_health_controller import ServiceHealthController
from app.desktop.controllers.user_controller import UserController
from app.desktop.services.camera_service import CameraService
from app.desktop.services.event_service import EventService
from app.desktop.services.notification_service import NotificationService
from app.desktop.services.health_service import HealthService
from app.desktop.services.settings_service import SettingsService
from app.desktop.services.service_health_service import ServiceHealthService
from app.desktop.services.user_service import UserService
from app.desktop.navigation.router import Router

# Force le style Basic pour éviter les problèmes de DLL Windows
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"


class Application(QApplication):
    """Application principale SentinelAI."""

    def __init__(self):
        super().__init__(sys.argv)
        self._engine = None
        self._auth_controller = AuthController()
        self._alert_controller = AlertController()
        self._camera_service = CameraService()
        self._camera_controller = CameraController(self._camera_service)
        self._video_pipeline = VideoPipelineController(self._camera_service)
        self._event_service = EventService()
        self._event_controller = EventController(self._event_service)
        self._notification_service = NotificationService()
        self._notification_controller = NotificationController(self._notification_service)
        self._health_service = HealthService()
        self._health_controller = HealthController(self._health_service)
        self._settings_service = SettingsService()
        self._settings_controller = SettingsController(self._settings_service)
        self._service_health_service = ServiceHealthService()
        self._service_health_controller = ServiceHealthController(self._service_health_service)
        self._user_service = UserService()
        self._user_controller = UserController(self._user_service)
        self._router = Router()

    def create_main_window(self):
        """Crée et affiche la fenêtre principale via QML."""
        self._engine = QQmlApplicationEngine()
        
        # Enregistre le contrôleur d'authentification
        self._engine.rootContext().setContextProperty("AuthController", self._auth_controller)
        
        # Enregistre le contrôleur d'alertes
        self._engine.rootContext().setContextProperty("AlertController", self._alert_controller)
        
        # Enregistre le contrôleur de caméras
        self._engine.rootContext().setContextProperty("CameraController", self._camera_controller)
        
        # Enregistre le pipeline vidéo
        self._engine.rootContext().setContextProperty("VideoPipeline", self._video_pipeline)
        
        # Enregistre le contrôleur d'événements
        self._engine.rootContext().setContextProperty("EventController", self._event_controller)
        
        # Enregistre le contrôleur de notifications
        self._engine.rootContext().setContextProperty("NotificationController", self._notification_controller)
        
        # Enregistre le contrôleur de santé système
        self._engine.rootContext().setContextProperty("HealthController", self._health_controller)
        
        # Enregistre le contrôleur de paramètres
        self._engine.rootContext().setContextProperty("SettingsController", self._settings_controller)
        
        # Enregistre le contrôleur de santé des services
        self._engine.rootContext().setContextProperty("ServiceHealthController", self._service_health_controller)
        
        # Enregistre le contrôleur d'utilisateurs
        self._engine.rootContext().setContextProperty("UserController", self._user_controller)

        # Enregistre le routeur (navigation)
        self._engine.rootContext().setContextProperty("Router", self._router)
        
        # Ajoute le provider d'images vidéo
        self._engine.addImageProvider("video", self._video_pipeline.image_provider)
        
        # Ajoute le chemin QML pour les imports
        qml_path = Path(__file__).parent / "qml"
        self._engine.addImportPath(str(qml_path))
        
        # Chemin vers le fichier QML principal
        qml_file = Path(__file__).parent / "qml" / "Main.qml"
        self._engine.load(QUrl.fromLocalFile(str(qml_file)))

        if not self._engine.rootObjects():
            raise RuntimeError("Failed to load QML file")

    def exec(self):
        """Démarre la boucle d'événements."""
        self.create_main_window()
        return super().exec()
