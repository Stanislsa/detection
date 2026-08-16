"""
Notifications push desktop avec gestion des permissions.

États: unknown | granted | denied
Persistance via QSettings (clé SentinelAI/push).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, QSettings, pyqtSignal, pyqtProperty, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from desktop.services.android_permissions import (
    AndroidPermissionHelper,
    is_android,
    PERMISSION_POST_NOTIFICATIONS,
)


class PushPermission:
    UNKNOWN = "unknown"
    GRANTED = "granted"
    DENIED = "denied"


class PushNotificationService(QObject):
    """Push OS + consentement utilisateur."""

    notificationShown = pyqtSignal(str, str)
    trayActivated = pyqtSignal()
    permissionChanged = pyqtSignal(str)
    enabledChanged = pyqtSignal()
    permissionRequestNeeded = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._settings = QSettings("SentinelAI", "Desktop")
        self._permission = self._settings.value("push/permission", PushPermission.UNKNOWN)
        if self._permission not in (
            PushPermission.UNKNOWN,
            PushPermission.GRANTED,
            PushPermission.DENIED,
        ):
            self._permission = PushPermission.UNKNOWN

        self._enabled = bool(self._settings.value("push/enabled", True, type=bool))
        self._critical_only = bool(
            self._settings.value("push/critical_only", True, type=bool)
        )
        self._tray: Optional[QSystemTrayIcon] = None
        self._app_name = "SentinelAI"
        self._tray_available = QSystemTrayIcon.isSystemTrayAvailable()
        self._android = is_android()
        self._android_perms = AndroidPermissionHelper(self)
        self._android_perms.permissionResult.connect(self._on_android_permission_result)
        self._android_perms.batchResult.connect(self._on_android_batch_result)
        self._init_tray()

    @pyqtProperty(str, notify=permissionChanged)
    def permission(self) -> str:
        return self._permission

    @pyqtProperty(bool, notify=permissionChanged)
    def isGranted(self) -> bool:
        return self._permission == PushPermission.GRANTED

    @pyqtProperty(bool, notify=permissionChanged)
    def isDenied(self) -> bool:
        return self._permission == PushPermission.DENIED

    @pyqtProperty(bool, notify=permissionChanged)
    def isUnknown(self) -> bool:
        return self._permission == PushPermission.UNKNOWN

    @pyqtProperty(bool, notify=enabledChanged)
    def enabled(self) -> bool:
        return self._enabled and self._permission == PushPermission.GRANTED

    @pyqtProperty(bool, notify=enabledChanged)
    def userEnabled(self) -> bool:
        return self._enabled

    @pyqtProperty(bool, constant=True)
    def trayAvailable(self) -> bool:
        return self._tray_available

    @pyqtProperty(bool, constant=True)
    def notifySendAvailable(self) -> bool:
        return bool(shutil.which("notify-send")) if sys.platform.startswith("linux") else False

    @pyqtProperty(str, constant=True)
    def platformHint(self) -> str:
        if getattr(self, "_android", False):
            snap = self._android_perms.statusSnapshot()
            post = "granted" if snap.get("postNotifications") else "not granted"
            return f"Android: POST_NOTIFICATIONS {post}"
        if sys.platform.startswith("linux"):
            if self._tray_available and self.notifySendAvailable:
                return "Linux: system tray + notify-send"
            if self._tray_available:
                return "Linux: system tray only"
            if self.notifySendAvailable:
                return "Linux: notify-send only"
            return "Linux: no desktop notification backend detected"
        if sys.platform == "win32":
            return "Windows: system tray notifications"
        if sys.platform == "darwin":
            return "macOS: system tray (limited)"
        return f"Platform: {sys.platform}"

    @pyqtProperty(bool, constant=True)
    def isAndroid(self) -> bool:
        return getattr(self, "_android", False)

    @pyqtProperty("QVariantMap", constant=False)
    def androidStatus(self):
        if hasattr(self, "_android_perms"):
            return self._android_perms.statusSnapshot()
        return {"isAndroid": False}

    def _set_permission(self, value: str) -> None:
        if value == self._permission:
            return
        self._permission = value
        self._settings.setValue("push/permission", value)
        self._settings.sync()
        self.permissionChanged.emit(value)
        self.enabledChanged.emit()

    @pyqtSlot()
    def requestPermission(self) -> None:
        """In-app consent dialog + on Android also request OS POST_NOTIFICATIONS."""
        self.permissionRequestNeeded.emit()
        if getattr(self, "_android", False):
            self._android_perms.requestPushPermissions()

    @pyqtSlot()
    def grantPermission(self) -> None:
        """User accepted in-app dialog. On Android, still need OS grant."""
        if getattr(self, "_android", False):
            # If OS already granted → mark granted; else request and wait for callback
            if self._android_perms.hasPushPermission():
                self._set_permission(PushPermission.GRANTED)
            else:
                self._android_perms.requestPushPermissions()
                # provisional: stay unknown until OS callback
        else:
            self._set_permission(PushPermission.GRANTED)
        if not self._enabled and self._permission == PushPermission.GRANTED:
            self._enabled = True
            self._settings.setValue("push/enabled", True)
            self.enabledChanged.emit()

    def _on_android_permission_result(self, permission: str, granted: bool) -> None:
        if permission != PERMISSION_POST_NOTIFICATIONS and not permission.endswith(
            "POST_NOTIFICATIONS"
        ):
            return
        if granted:
            self._set_permission(PushPermission.GRANTED)
            if not self._enabled:
                self._enabled = True
                self._settings.setValue("push/enabled", True)
                self.enabledChanged.emit()
        else:
            # User denied at OS level
            self._set_permission(PushPermission.DENIED)

    def _on_android_batch_result(self, results: dict) -> None:
        # Prefer POST_NOTIFICATIONS key
        granted = None
        for k, v in (results or {}).items():
            if "POST_NOTIFICATIONS" in str(k):
                granted = bool(v)
                break
        if granted is None and results:
            granted = all(bool(v) for v in results.values())
        if granted is True:
            self._set_permission(PushPermission.GRANTED)
        elif granted is False:
            self._set_permission(PushPermission.DENIED)

    @pyqtSlot()
    def denyPermission(self) -> None:
        self._set_permission(PushPermission.DENIED)
        self._enabled = False
        self._settings.setValue("push/enabled", False)
        self.enabledChanged.emit()

    @pyqtSlot()
    def resetPermission(self) -> None:
        self._set_permission(PushPermission.UNKNOWN)

    @pyqtSlot(result=bool)
    def ensurePermission(self) -> bool:
        if self._permission == PushPermission.UNKNOWN:
            self.permissionRequestNeeded.emit()
            if getattr(self, "_android", False):
                self._android_perms.requestPushPermissions()
            return False
        if self._permission != PushPermission.GRANTED:
            return False
        # Re-check Android OS permission (may have been revoked in Settings)
        if getattr(self, "_android", False) and not self._android_perms.hasPushPermission():
            self._set_permission(PushPermission.DENIED)
            return False
        return self._enabled

    @pyqtSlot(bool)
    def set_enabled(self, value: bool) -> None:
        value = bool(value)
        if value and self._permission != PushPermission.GRANTED:
            self.requestPermission()
            return
        self._enabled = value
        self._settings.setValue("push/enabled", value)
        self.enabledChanged.emit()

    @pyqtSlot(bool)
    def set_critical_only(self, value: bool) -> None:
        self._critical_only = bool(value)
        self._settings.setValue("push/critical_only", self._critical_only)

    @pyqtSlot(result=bool)
    def isEnabled(self) -> bool:
        return self.enabled

    @pyqtSlot(result=bool)
    def isCriticalOnly(self) -> bool:
        return self._critical_only

    def _init_tray(self) -> None:
        if getattr(self, "_android", False):
            # Android uses NotificationManager, not QSystemTrayIcon
            print("[Push] Android mode: system tray skipped")
            return
        if not self._tray_available:
            print("[Push] System tray not available on this platform")
            return

        icon_path = (
            Path(__file__).resolve().parent.parent / "assets" / "icons" / "shield.svg"
        )
        icon = QIcon(str(icon_path)) if icon_path.exists() else QApplication.windowIcon()

        self._tray = QSystemTrayIcon(icon)
        self._tray.setToolTip("SentinelAI — Secure Operations")
        self._tray.activated.connect(self._on_tray_activated)

        menu = QMenu()
        menu.addAction("Open SentinelAI").triggered.connect(self._bring_to_front)
        menu.addSeparator()
        menu.addAction("Quit").triggered.connect(QApplication.instance().quit)
        self._tray.setContextMenu(menu)
        self._tray.show()

    def _on_tray_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.trayActivated.emit()
            self._bring_to_front()

    def _bring_to_front(self) -> None:
        app = QApplication.instance()
        if not app:
            return
        for w in app.topLevelWidgets():
            if w.isWindow() and w.isVisible():
                w.raise_()
                w.activateWindow()
                break

    @pyqtSlot(str, str, str, result=bool)
    def push(self, title: str, message: str, priority: str = "CRITICAL") -> bool:
        if not self.ensurePermission():
            return False
        if self._critical_only and priority not in ("CRITICAL", "HIGH"):
            return False

        shown = False
        if self._tray and self._tray.isVisible():
            icon = (
                QSystemTrayIcon.MessageIcon.Critical
                if priority == "CRITICAL"
                else QSystemTrayIcon.MessageIcon.Warning
                if priority == "HIGH"
                else QSystemTrayIcon.MessageIcon.Information
            )
            self._tray.showMessage(
                f"{self._app_name} — {title}",
                message[:250],
                icon,
                8000 if priority == "CRITICAL" else 5000,
            )
            shown = True

        if sys.platform.startswith("linux"):
            if self._notify_send(title, message, priority):
                shown = True

        if shown:
            self.notificationShown.emit(title, message)
        return shown

    def _notify_send(self, title: str, message: str, priority: str) -> bool:
        bin_path = shutil.which("notify-send")
        if not bin_path:
            return False
        urgency = "critical" if priority == "CRITICAL" else "normal"
        try:
            subprocess.Popen(
                [
                    bin_path,
                    f"[{self._app_name}] {title}",
                    message[:200],
                    "--urgency",
                    urgency,
                    "--app-name",
                    self._app_name,
                    "--expire-time",
                    "8000" if priority == "CRITICAL" else "5000",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except OSError:
            return False

    def push_from_alert(self, alert: dict) -> bool:
        title = alert.get("title") or "Security Alert"
        loc = alert.get("location") or alert.get("camera_name") or ""
        msg = alert.get("description") or loc
        if loc and loc not in msg:
            msg = f"{msg} @ {loc}"
        priority = alert.get("priority") or "HIGH"
        return self.push(title, msg, priority)
