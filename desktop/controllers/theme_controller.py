"""
Persistance du thème dark / light.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QObject, QSettings, pyqtSignal, pyqtProperty, pyqtSlot


class ThemeController(QObject):
    """Préférence de thème persistée (QSettings)."""

    isDarkChanged = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._settings = QSettings("SentinelAI", "Desktop")
        val = self._settings.value("theme/isDark", True)
        if isinstance(val, str):
            self._is_dark = val.lower() in ("1", "true", "yes")
        else:
            self._is_dark = bool(val)

    @pyqtProperty(bool, notify=isDarkChanged)
    def isDark(self) -> bool:
        return self._is_dark

    @pyqtSlot(bool)
    def setDark(self, value: bool) -> None:
        value = bool(value)
        if value == self._is_dark:
            return
        self._is_dark = value
        self._settings.setValue("theme/isDark", value)
        self._settings.sync()
        self.isDarkChanged.emit()

    @pyqtSlot()
    def toggle(self) -> None:
        self.setDark(not self._is_dark)

    @pyqtSlot(result=bool)
    def loadIsDark(self) -> bool:
        return self._is_dark
