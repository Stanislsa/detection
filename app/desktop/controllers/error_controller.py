"""
Gestion centralisée des erreurs applicatives (Python → QML).
"""

from __future__ import annotations

import traceback
from collections import deque
from datetime import datetime
from typing import Any, Deque, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot


class ErrorController(QObject):
    """
    Collecte les erreurs runtime et les expose à QML.
    Niveaux: info | warning | error | critical
    """

    errorOccurred = pyqtSignal(str, str, str)  # id, level, message
    errorsChanged = pyqtSignal()
    lastErrorChanged = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None, max_history: int = 50):
        super().__init__(parent)
        self._history: Deque[Dict[str, Any]] = deque(maxlen=max_history)
        self._last: Dict[str, Any] = {}
        self._counter = 0
        self._banner_visible = False
        self._banner_message = ""
        self._banner_level = "error"

    # ---------------------------------------------------------------- properties
    @pyqtProperty("QVariantList", notify=errorsChanged)
    def errors(self) -> List[Dict[str, Any]]:
        return list(self._history)

    @pyqtProperty(int, notify=errorsChanged)
    def errorCount(self) -> int:
        return len(self._history)

    @pyqtProperty("QVariantMap", notify=lastErrorChanged)
    def lastError(self) -> Dict[str, Any]:
        return dict(self._last) if self._last else {}

    @pyqtProperty(bool, notify=lastErrorChanged)
    def bannerVisible(self) -> bool:
        return self._banner_visible

    @pyqtProperty(str, notify=lastErrorChanged)
    def bannerMessage(self) -> str:
        return self._banner_message

    @pyqtProperty(str, notify=lastErrorChanged)
    def bannerLevel(self) -> str:
        return self._banner_level

    # -------------------------------------------------------------------- API
    @pyqtSlot(str, str, str)
    def report(self, message: str, level: str = "error", source: str = "app") -> str:
        """Enregistre une erreur et déclenche le bandeau si level >= warning."""
        self._counter += 1
        eid = f"ERR-{self._counter:04d}"
        level = (level or "error").lower()
        entry = {
            "id": eid,
            "level": level,
            "message": str(message)[:500],
            "source": str(source)[:80],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "dismissed": False,
        }
        self._history.appendleft(entry)
        self._last = entry
        self.errorsChanged.emit()
        self.lastErrorChanged.emit()
        self.errorOccurred.emit(eid, level, entry["message"])

        if level in ("warning", "error", "critical"):
            self._banner_visible = True
            self._banner_message = entry["message"]
            self._banner_level = level
            self.lastErrorChanged.emit()
        return eid

    @pyqtSlot(str)
    def reportPageLoadError(self, page: str) -> str:
        return self.report(
            f"Failed to load page « {page} ». Navigation remains available.",
            "error",
            "navigation",
        )

    @pyqtSlot(str, str)
    def reportException(self, context: str, detail: str) -> str:
        msg = f"{context}: {detail}" if context else detail
        return self.report(msg, "error", "exception")

    def report_exception_obj(self, context: str, exc: BaseException) -> str:
        tb = traceback.format_exc(limit=4)
        detail = f"{type(exc).__name__}: {exc}"
        eid = self.report(f"{context} — {detail}", "critical", "exception")
        # Keep full traceback in history metadata (not shown in banner)
        if self._history:
            self._history[0]["traceback"] = tb[-800:]
        return eid

    @pyqtSlot()
    def dismissBanner(self) -> None:
        self._banner_visible = False
        self._banner_message = ""
        self.lastErrorChanged.emit()

    @pyqtSlot()
    def clearHistory(self) -> None:
        self._history.clear()
        self._last = {}
        self._banner_visible = False
        self._banner_message = ""
        self.errorsChanged.emit()
        self.lastErrorChanged.emit()

    @pyqtSlot(str)
    def dismissError(self, error_id: str) -> None:
        for e in self._history:
            if e.get("id") == error_id:
                e["dismissed"] = True
                break
        self.errorsChanged.emit()
