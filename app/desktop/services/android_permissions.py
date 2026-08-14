"""
Gestion des permissions Android (runtime).

Cible principale: POST_NOTIFICATIONS (API 33+).
Fonctionne uniquement quand l'app tourne sous Android via Qt for Android / PySide6/PyQt6.
Sur desktop, toutes les méthodes sont des no-op sûrs.
"""

from __future__ import annotations

import sys
from typing import Callable, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty


# Constantes Android
PERMISSION_POST_NOTIFICATIONS = "android.permission.POST_NOTIFICATIONS"
PERMISSION_CAMERA = "android.permission.CAMERA"
PERMISSION_RECORD_AUDIO = "android.permission.RECORD_AUDIO"
PERMISSION_ACCESS_FINE_LOCATION = "android.permission.ACCESS_FINE_LOCATION"
PERMISSION_READ_EXTERNAL_STORAGE = "android.permission.READ_EXTERNAL_STORAGE"
PERMISSION_WRITE_EXTERNAL_STORAGE = "android.permission.WRITE_EXTERNAL_STORAGE"
PERMISSION_INTERNET = "android.permission.INTERNET"
PERMISSION_VIBRATE = "android.permission.VIBRATE"
PERMISSION_FOREGROUND_SERVICE = "android.permission.FOREGROUND_SERVICE"
PERMISSION_WAKE_LOCK = "android.permission.WAKE_LOCK"

# Permissions liées aux alertes push / surveillance
PUSH_RELATED_PERMISSIONS = [
    PERMISSION_POST_NOTIFICATIONS,
    PERMISSION_VIBRATE,
]

CAMERA_RELATED_PERMISSIONS = [
    PERMISSION_CAMERA,
    PERMISSION_RECORD_AUDIO,
]


def is_android() -> bool:
    """True si l'interpréteur tourne sous Android."""
    if sys.platform == "android":
        return True
    # Qt for Android / some embeds
    try:
        from PyQt6.QtCore import QSysInfo

        product = (QSysInfo.productType() or "").lower()
        if product in ("android", "androidx"):
            return True
    except Exception:
        pass
    return False


class AndroidPermissionHelper(QObject):
    """
    Pont runtime permissions Android.

    Signaux:
      permissionResult(permission: str, granted: bool)
      allResults(results: dict-like via QVariantMap in practice)
    """

    permissionResult = pyqtSignal(str, bool)
    batchResult = pyqtSignal("QVariantMap")
    errorOccurred = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._android = is_android()
        self._qt_android = None
        self._pending: List[str] = []

        if self._android:
            self._qt_android = self._load_qt_android()

    def _load_qt_android(self):
        """Charge le module Qt Android disponible."""
        # PyQt6.QtCore.QNativeInterface / QtAndroid (selon version)
        candidates = [
            ("PyQt6.QtCore", "QNativeInterface"),
            ("PyQt6.QtAndroid", None),  # older bindings
        ]
        for mod_name, attr in candidates:
            try:
                mod = __import__(mod_name, fromlist=["*"])
                if attr is None:
                    return mod
                if hasattr(mod, attr):
                    return getattr(mod, attr)
            except Exception:
                continue

        # Fallback: pyjnius
        try:
            from jnius import autoclass  # type: ignore

            return {"jnius": True, "autoclass": autoclass}
        except Exception:
            pass

        return None

    @pyqtProperty(bool, constant=True)
    def isAndroid(self) -> bool:
        return self._android

    @pyqtProperty(bool, constant=True)
    def available(self) -> bool:
        return self._android and self._qt_android is not None

    # ------------------------------------------------------------------ check
    @pyqtSlot(str, result=bool)
    def checkPermission(self, permission: str) -> bool:
        """Retourne True si la permission est déjà accordée (ou non-Android)."""
        if not self._android:
            return True  # desktop: pas de runtime permission OS de ce type

        # Qt 6 Android: QtAndroidPrivate / QNativeInterface.QAndroidApplication
        try:
            result = self._check_via_qt(permission)
            if result is not None:
                return result
        except Exception as exc:
            self.errorOccurred.emit(f"checkPermission Qt: {exc}")

        try:
            return self._check_via_jnius(permission)
        except Exception as exc:
            self.errorOccurred.emit(f"checkPermission jnius: {exc}")
            return False

    def _check_via_qt(self, permission: str) -> Optional[bool]:
        """Tentative via API Qt 6."""
        try:
            from PyQt6.QtCore import QtAndroid  # type: ignore

            # Some builds expose QtAndroid.checkPermission
            if hasattr(QtAndroid, "checkPermission"):
                # 0 = Granted in many Qt Android bindings
                return int(QtAndroid.checkPermission(permission)) == 0
        except Exception:
            pass

        try:
            # Qt 6.5+ style (pseudo)
            from PyQt6.QtCore import QNativeInterface  # type: ignore

            app = QNativeInterface.QAndroidApplication
            if hasattr(app, "checkPermission"):
                return bool(app.checkPermission(permission))
        except Exception:
            pass
        return None

    def _check_via_jnius(self, permission: str) -> bool:
        from jnius import autoclass  # type: ignore

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        # Also try Qt activity
        try:
            Activity = autoclass("org.qtproject.qt.android.bindings.QtActivity")
            activity = Activity.m_activity
        except Exception:
            activity = PythonActivity.mActivity

        ContextCompat = autoclass("androidx.core.content.ContextCompat")
        PackageManager = autoclass("android.content.pm.PackageManager")
        result = ContextCompat.checkSelfPermission(activity, permission)
        return result == PackageManager.PERMISSION_GRANTED

    # ----------------------------------------------------------------- request
    @pyqtSlot(str)
    def requestPermission(self, permission: str) -> None:
        self.requestPermissions([permission])

    @pyqtSlot("QStringList")
    def requestPermissions(self, permissions: list) -> None:
        """Demande une ou plusieurs permissions runtime."""
        if not self._android:
            # Desktop: considérer comme accordé
            results = {p: True for p in permissions}
            for p, g in results.items():
                self.permissionResult.emit(p, g)
            self.batchResult.emit(results)
            return

        self._pending = list(permissions)
        try:
            if self._request_via_qt(permissions):
                return
        except Exception as exc:
            self.errorOccurred.emit(f"requestPermissions Qt: {exc}")

        try:
            self._request_via_jnius(permissions)
        except Exception as exc:
            self.errorOccurred.emit(f"requestPermissions jnius: {exc}")
            results = {p: False for p in permissions}
            for p, g in results.items():
                self.permissionResult.emit(p, g)
            self.batchResult.emit(results)

    def _request_via_qt(self, permissions: list) -> bool:
        try:
            from PyQt6.QtCore import QtAndroid  # type: ignore

            if hasattr(QtAndroid, "requestPermissions"):
                # Callback-style varies by binding version
                def _cb(results):
                    mapped = {}
                    if isinstance(results, dict):
                        mapped = {k: bool(v) for k, v in results.items()}
                    else:
                        # list of (perm, granted) or similar
                        for item in results:
                            if isinstance(item, (list, tuple)) and len(item) >= 2:
                                mapped[str(item[0])] = bool(item[1])
                    for p, g in mapped.items():
                        self.permissionResult.emit(p, g)
                    self.batchResult.emit(mapped)

                QtAndroid.requestPermissions(list(permissions), _cb)
                return True
        except Exception:
            pass
        return False

    def _request_via_jnius(self, permissions: list) -> None:
        from jnius import autoclass, PythonJavaClass, java_method  # type: ignore

        try:
            Activity = autoclass("org.qtproject.qt.android.bindings.QtActivity")
            activity = Activity.m_activity
        except Exception:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            activity = PythonActivity.mActivity

        helper = self

        class Listener(PythonJavaClass):
            __javainterfaces__ = ["androidx/core/app/ActivityCompat$OnRequestPermissionsResultCallback"]
            # Note: real integration often uses Activity.onRequestPermissionsResult hook

            @java_method("([Ljava/lang/String;[I)V")
            def onRequestPermissionsResult(self, perms, grantResults):
                PackageManager = autoclass("android.content.pm.PackageManager")
                mapped = {}
                for i, perm in enumerate(perms):
                    granted = (
                        grantResults[i] == PackageManager.PERMISSION_GRANTED
                        if i < len(grantResults)
                        else False
                    )
                    mapped[str(perm)] = granted
                    helper.permissionResult.emit(str(perm), granted)
                helper.batchResult.emit(mapped)

        # Store listener ref
        self._listener = Listener()
        ActivityCompat = autoclass("androidx.core.app.ActivityCompat")
        ActivityCompat.requestPermissions(activity, permissions, 4242)

    # --------------------------------------------------------------- high-level
    @pyqtSlot()
    def requestPushPermissions(self) -> None:
        """Demande POST_NOTIFICATIONS (+ VIBRATE si pertinent)."""
        to_request = []
        for p in PUSH_RELATED_PERMISSIONS:
            if not self.checkPermission(p):
                to_request.append(p)
        if not to_request:
            # Already all granted
            self.batchResult.emit({p: True for p in PUSH_RELATED_PERMISSIONS})
            return
        self.requestPermissions(to_request)

    @pyqtSlot(result=bool)
    def hasPushPermission(self) -> bool:
        """POST_NOTIFICATIONS accordée (ou non-Android)."""
        if not self._android:
            return True
        # Sur API < 33, POST_NOTIFICATIONS n'existe pas → considéré granted
        return self.checkPermission(PERMISSION_POST_NOTIFICATIONS)

    @pyqtSlot()
    def requestCameraPermissions(self) -> None:
        missing = [p for p in CAMERA_RELATED_PERMISSIONS if not self.checkPermission(p)]
        if missing:
            self.requestPermissions(missing)
        else:
            self.batchResult.emit({p: True for p in CAMERA_RELATED_PERMISSIONS})

    @pyqtSlot(result="QVariantMap")
    def statusSnapshot(self) -> dict:
        """État lisible pour QML."""
        return {
            "isAndroid": self._android,
            "available": self.available,
            "postNotifications": self.checkPermission(PERMISSION_POST_NOTIFICATIONS)
            if self._android
            else True,
            "camera": self.checkPermission(PERMISSION_CAMERA) if self._android else True,
            "vibrate": self.checkPermission(PERMISSION_VIBRATE) if self._android else True,
        }
