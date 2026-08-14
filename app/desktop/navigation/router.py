"""
Router pour la navigation entre les pages de l'application.

Exposed to QML via `setContextProperty("Router", Router())`.
QML strings ("dashboard", "alerts", ...) are the page keys
registered in AppLayout.qml's getPageSource().
"""

from enum import Enum
from typing import Optional, Dict, Any

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty


class Page(Enum):
    """Pages disponibles dans l'application."""
    DASHBOARD = "dashboard"
    CAMERAS = "cameras"
    ALERTS = "alerts"
    EVENTS = "events"
    USERS = "users"
    AI_TRAINING = "ai_training"
    OBSERVABILITY = "observability"
    SYSTEM_HEALTH = "system_health"
    NOTIFICATIONS = "notifications"
    SETTINGS = "settings"

    # Detail pages (kept for sub-navigation)
    CAMERA_DETAIL = "camera_detail"
    CAMERA_SETTINGS = "camera_settings"


class Router(QObject):
    """Gestionnaire de navigation entre les pages (QObject, QML-friendly)."""

    pageChanged = pyqtSignal(str)
    breadcrumbChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._current_page: Page = Page.DASHBOARD
        self._page_params: Dict[str, Any] = {}
        self._navigation_history: list = []
        self._breadcrumbs: list = ["SentinelAI"]

    # ---- Properties ----

    @pyqtProperty(str, notify=pageChanged)
    def currentPage(self) -> str:
        return self._current_page.value

    @pyqtProperty('QVariantList', notify=breadcrumbChanged)
    def breadcrumbs(self) -> list:
        return list(self._breadcrumbs)

    # ---- Slots ----

    @pyqtSlot(str)
    def navigateTo(self, page: str) -> None:
        self.navigate_to(page)

    @pyqtSlot()
    def goBack(self) -> None:
        self.go_back()

    # ---- Pure-python API (kept for Python callers) ----

    @property
    def page_enum(self) -> Page:
        return self._current_page

    @property
    def page_params(self) -> Dict[str, Any]:
        return self._page_params

    def navigate_to(self, page: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Navigue vers une nouvelle page (string key, e.g. 'dashboard')."""
        self._navigation_history.append(self._current_page.value)
        self._current_page = Page(page)
        self._page_params = params or {}
        # Update breadcrumbs: ["SentinelAI", page title]
        title = self._title_for(self._current_page)
        self._breadcrumbs = ["SentinelAI", title]
        self.pageChanged.emit(self._current_page.value)
        self.breadcrumbChanged.emit()
        return self._current_page.value

    def go_back(self) -> Optional[str]:
        if self._navigation_history:
            previous = self._navigation_history.pop()
            self._current_page = Page(previous)
            title = self._title_for(self._current_page)
            self._breadcrumbs = ["SentinelAI", title]
            self.pageChanged.emit(self._current_page.value)
            self.breadcrumbChanged.emit()
            return previous
        return None

    def can_go_back(self) -> bool:
        return len(self._navigation_history) > 0

    def _title_for(self, page: Page) -> str:
        titles = {
            Page.DASHBOARD:      "Dashboard",
            Page.CAMERAS:        "Cameras",
            Page.ALERTS:         "Alerts",
            Page.EVENTS:         "Events",
            Page.USERS:          "Users",
            Page.AI_TRAINING:    "AI Training",
            Page.OBSERVABILITY:  "Observability",
            Page.SYSTEM_HEALTH:  "System Health",
            Page.NOTIFICATIONS:  "Notifications",
            Page.SETTINGS:       "Settings",
            Page.CAMERA_DETAIL:  "Camera Detail",
            Page.CAMERA_SETTINGS:"Camera Settings",
        }
        return titles.get(page, page.value.title())