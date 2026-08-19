from desktop.controllers.dashboard_controller import DashboardController
"""
Application principale PyQt6 + QML — portable Linux / Windows.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt6.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal, pyqtProperty
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtWidgets import QApplication

from desktop.controllers.auth_controller import AuthController
from desktop.controllers.alert_controller import AlertController
from desktop.controllers.camera_controller import CameraController
from desktop.controllers.video_pipeline_controller import VideoPipelineController
from desktop.controllers.event_controller import EventController
from desktop.controllers.notification_controller import NotificationController
from desktop.controllers.health_controller import HealthController
from desktop.controllers.settings_controller import SettingsController
from desktop.controllers.service_health_controller import ServiceHealthController
from desktop.controllers.user_controller import UserController
from desktop.services.camera_service import CameraService
from desktop.services.event_service import EventService
from desktop.services.notification_service import NotificationService
from desktop.services.health_service import HealthService
from desktop.services.settings_service import SettingsService
from desktop.services.service_health_service import ServiceHealthService
from desktop.services.user_service import UserService
from desktop.navigation.router import Router
from desktop.services.push_notification_service import PushNotificationService
from desktop.services.telegram_service import TelegramService
from desktop.controllers.telegram_controller import TelegramController
from desktop.controllers.error_controller import ErrorController
from desktop.controllers.i18n_controller import I18nController
from desktop.controllers.theme_controller import ThemeController
from desktop.services.android_permissions import AndroidPermissionHelper
from desktop.models.notification_model import NotificationType, NotificationCategory

# Force Basic style before any Qt Quick Controls instantiation
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

DESKTOP_DIR = Path(__file__).resolve().parent
QML_DIR = DESKTOP_DIR / "qml"
ASSETS_DIR = DESKTOP_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"


class AppPaths(QObject):
    """Expose filesystem paths to QML (icons, assets)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._icons = ICONS_DIR.as_uri() + "/"
        self._assets = ASSETS_DIR.as_uri() + "/"
        self._qml = QML_DIR.as_uri() + "/"

    @pyqtProperty(str, constant=True)
    def icons(self) -> str:
        return self._icons

    @pyqtProperty(str, constant=True)
    def assets(self) -> str:
        return self._assets

    @pyqtProperty(str, constant=True)
    def qml(self) -> str:
        return self._qml

    @pyqtSlot(str, result=str)
    def iconUrl(self, name: str) -> str:
        """Return file:// URL for an icon name (with or without .svg)."""
        if not name:
            return ""
        if name.endswith(".svg"):
            path = ICONS_DIR / name
        else:
            # camelCase → kebab-case
            import re
            kebab = re.sub(r"([A-Z])", r"-\1", name).lower().lstrip("-")
            path = ICONS_DIR / f"{kebab}.svg"
        if path.exists():
            return path.as_uri()
        return ""


class Application(QApplication):
    """Application principale SentinelAI."""

    def __init__(self):
        super().__init__(sys.argv)
        self._engine: QQmlApplicationEngine | None = None
        self._paths = AppPaths()

        self._auth_controller = AuthController()
        self._dashboard_controller = DashboardController(self)
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
        self._push = PushNotificationService(self)
        self._telegram_service = TelegramService()
        self._telegram_controller = TelegramController(self._telegram_service)
        self._android_perms = AndroidPermissionHelper(self)
        self._error_controller = ErrorController(self)
        self._i18n = I18nController(self)
        self._theme_prefs = ThemeController(self)

        # Bridge: alertes → notifications in-app + push OS
        self._alert_controller.alertReceived.connect(self._on_alert_received)


    def _on_alert_received(self, payload: dict):
        """Nouvelle alerte → centre de notifications + push système."""
        if not isinstance(payload, dict):
            return
        priority = payload.get("priority") or "HIGH"
        title = payload.get("title") or "Security Alert"
        message = payload.get("description") or payload.get("location") or ""
        # In-app notification center
        ntype = "critical" if priority == "CRITICAL" else ("warning" if priority == "HIGH" else "info")
        try:
            self._notification_service.create_notification(
                type=NotificationType(ntype),
                category=NotificationCategory.ALERT,
                title=title,
                message=message,
                action_required=priority in ("CRITICAL", "HIGH"),
                metadata={
                    "alert_id": payload.get("id"),
                    "camera_id": payload.get("camera_id"),
                    "location": payload.get("location"),
                    "priority": priority,
                },
            )
            # Notify QML listeners
            self._notification_controller.notificationsChanged.emit()
            if hasattr(self._notification_controller, "notificationAdded"):
                # id may not be available easily; emit empty or skip
                pass
        except Exception as exc:
            self._error_controller.report_exception_obj("Notification", exc)
            print(f"[Notify] in-app failed: {exc}")

        # OS push (tray / notify-send)
        try:
            self._push.push_from_alert(payload)
        except Exception as exc:
            self._error_controller.report(f"Push notification failed: {exc}", "warning", "push")
            print(f"[Push] OS notification failed: {exc}")

        try:
            self._telegram_controller.notify_alert(payload)
        except Exception as exc:
            self._error_controller.report(f"Telegram notify failed: {exc}", "warning", "telegram")
            print(f"[Telegram] notify failed: {exc}")

    def create_main_window(self):
        """Crée le moteur QML et charge Main.qml."""
        self._engine = QQmlApplicationEngine()
        ctx = self._engine.rootContext()

        # Controllers
        ctx.setContextProperty("AuthController", self._auth_controller)
        ctx.setContextProperty("DashboardController", self._dashboard_controller)
        ctx.setContextProperty("AlertController", self._alert_controller)
        ctx.setContextProperty("CameraController", self._camera_controller)
        ctx.setContextProperty("VideoPipeline", self._video_pipeline)
        ctx.setContextProperty("EventController", self._event_controller)
        ctx.setContextProperty("NotificationController", self._notification_controller)
        ctx.setContextProperty("HealthController", self._health_controller)
        ctx.setContextProperty("SettingsController", self._settings_controller)
        ctx.setContextProperty("ServiceHealthController", self._service_health_controller)
        ctx.setContextProperty("UserController", self._user_controller)
        ctx.setContextProperty("Router", self._router)
        ctx.setContextProperty("PushService", self._push)
        ctx.setContextProperty("TelegramController", self._telegram_controller)
        ctx.setContextProperty("AndroidPermissions", self._android_perms)
        ctx.setContextProperty("ErrorController", self._error_controller)
        ctx.setContextProperty("I18n", self._i18n)
        ctx.setContextProperty("ThemePrefs", self._theme_prefs)
        ctx.setContextProperty("AppPaths", self._paths)

        # Video image provider
        self._engine.addImageProvider("video", self._video_pipeline.image_provider)

        # QML import path
        self._engine.addImportPath(str(QML_DIR))

        qml_file = QML_DIR / "Main.qml"
        if not qml_file.exists():
            raise FileNotFoundError(f"QML entry not found: {qml_file}")

        self._engine.load(QUrl.fromLocalFile(str(qml_file)))

        if not self._engine.rootObjects():
            errs = []
            try:
                for e in self._engine.rootObjects():
                    pass
                # Collect warnings from last load if available
            except Exception:
                pass
            msg = (
                f"Failed to load QML: {qml_file}. "
                "Check console for QML errors (missing imports, syntax)."
            )
            self._error_controller.report(msg, "critical", "qml")
            raise RuntimeError(msg)

    def exec(self) -> int:
        try:
            self.create_main_window()
        except Exception as exc:
            self._error_controller.report_exception_obj("Startup", exc)
            print(f"[FATAL] {exc}", file=sys.stderr)
            raise
        return super().exec()
