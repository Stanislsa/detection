"""DashboardController — KPI + historique auto-refresh."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal, pyqtProperty, pyqtSlot
from desktop.services.api_client import get_api_client

class _FetchWorker(QThread):
    finished_ok = pyqtSignal(dict, dict)
    finished_err = pyqtSignal(str)
    def __init__(self, days: int, parent=None):
        super().__init__(parent); self._days = days
    def run(self):
        c = get_api_client()
        overview, history = {}, {}
        try:
            if hasattr(c, "dashboard_history"):
                history = c.dashboard_history(self._days) or {}
            else:
                history = c.get("/dashboard/history", params={"days": self._days}) or {}
        except Exception as e:
            history = {"error": str(e)}
        try:
            overview = (getattr(c, "dashboard_kpis", None) or (lambda d: c.get("/dashboard/kpis", params={"days": d})))(self._days) or {}
        except Exception:
            try: overview = c.dashboard_stats() if hasattr(c, "dashboard_stats") else {}
            except Exception: overview = {}
        self.finished_ok.emit(overview or {}, history or {})

class DashboardController(QObject):
    dataChanged = pyqtSignal(); errorChanged = pyqtSignal(str)
    loadingChanged = pyqtSignal(); autoRefreshChanged = pyqtSignal(); historyChanged = pyqtSignal()
    DEFAULT_INTERVAL_MS = 15000
    def __init__(self, parent=None):
        super().__init__(parent)
        self._days, self._loading, self._error = 30, False, ""
        self._overview, self._history = {}, {}
        self._auto_refresh, self._interval_ms = False, self.DEFAULT_INTERVAL_MS
        self._worker, self._last_updated = None, ""
        self._timer = QTimer(self); self._timer.setInterval(self._interval_ms)
        self._timer.timeout.connect(self.refresh)
    def _det(self):
        o = self._overview; return o.get("detection") or o
    @pyqtProperty(bool, notify=loadingChanged)
    def loading(self): return self._loading
    @pyqtProperty(str, notify=errorChanged)
    def lastError(self): return self._error
    @pyqtProperty(str, notify=dataChanged)
    def lastUpdated(self): return self._last_updated
    @pyqtProperty(int, notify=dataChanged)
    def days(self): return self._days
    @pyqtProperty(bool, notify=autoRefreshChanged)
    def autoRefresh(self): return self._auto_refresh
    @pyqtProperty(int, notify=autoRefreshChanged)
    def refreshIntervalMs(self): return self._interval_ms
    @pyqtProperty(int, notify=dataChanged)
    def fallsTotal(self): return int(self._det().get("total_falls") or 0)
    @pyqtProperty(str, notify=dataChanged)
    def falseAlertRateLabel(self):
        v = self._det().get("false_positive_rate")
        if v is None: return "—"
        fv = float(v); fv = fv * 100 if fv <= 1 else fv
        return f"{fv:.1f} %"
    @pyqtProperty(str, notify=dataChanged)
    def f1Label(self):
        f1 = self._det().get("f1_score")
        return "—" if f1 is None else f"{float(f1)*100:.1f} %"
    @pyqtProperty(str, notify=dataChanged)
    def cameraAvailabilityLabel(self):
        cams = self._overview.get("cameras") or {}
        a, t = cams.get("active"), cams.get("total")
        return f"{a}/{t}" if a is not None and t is not None else "—"
    @pyqtProperty(str, notify=dataChanged)
    def avgInterventionLabel(self): return "—"
    def _series(self, name): return list((self._history.get("series") or {}).get(name) or [])
    @pyqtProperty("QVariantList", notify=historyChanged)
    def fallsHistory(self): return self._series("falls")
    @pyqtProperty("QVariantList", notify=historyChanged)
    def falseAlertRateHistory(self): return self._series("false_alert_rate_pct")
    @pyqtProperty("QVariantList", notify=historyChanged)
    def precisionHistory(self): return self._series("precision_running")
    @pyqtProperty("QVariantList", notify=historyChanged)
    def alertsHistory(self): return self._series("alerts")
    @pyqtSlot(int)
    def setDays(self, days: int): self._days = max(7, min(int(days), 365)); self.refresh()
    @pyqtSlot(int)
    def setRefreshIntervalMs(self, ms: int):
        self._interval_ms = max(5000, min(int(ms), 300000))
        self._timer.setInterval(self._interval_ms); self.autoRefreshChanged.emit()
    @pyqtSlot()
    def refresh(self):
        if self._worker and self._worker.isRunning(): return
        self._loading = True; self.loadingChanged.emit()
        self._worker = _FetchWorker(self._days, self)
        self._worker.finished_ok.connect(self._on_ok)
        self._worker.finished_err.connect(lambda m: (setattr(self, "_error", m), self.errorChanged.emit(m)))
        self._worker.finished.connect(lambda: (setattr(self, "_loading", False), self.loadingChanged.emit()))
        self._worker.start()
    def _on_ok(self, overview, history):
        self._overview, self._history = overview or {}, history or {}
        self._error = str(history.get("error") or "") if isinstance(history, dict) else ""
        self._last_updated = datetime.now().strftime("%H:%M:%S")
        self.dataChanged.emit(); self.historyChanged.emit(); self.errorChanged.emit(self._error)
    @pyqtSlot()
    def startAutoRefresh(self):
        self._auto_refresh = True; self.autoRefreshChanged.emit(); self.refresh()
        if not self._timer.isActive(): self._timer.start()
    @pyqtSlot()
    def stopAutoRefresh(self):
        self._auto_refresh = False; self._timer.stop(); self.autoRefreshChanged.emit()
    @pyqtSlot(bool)
    def setPageVisible(self, visible: bool):
        self.startAutoRefresh() if visible else self.stopAutoRefresh()
