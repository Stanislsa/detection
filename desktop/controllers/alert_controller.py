"""
Contrôleur pour la gestion des alertes et incidents — flux temps réel.
"""

from __future__ import annotations

from typing import Any, Dict, List

from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtProperty, pyqtSlot

from app.desktop.services.alert_service import AlertService
from app.desktop.models.alert_model import AlertStatus


class AlertController(QObject):
    """Contrôleur d'alertes accessible depuis QML (temps réel)."""

    alertsChanged = pyqtSignal()
    alertSelected = pyqtSignal(str)
    alertAcknowledged = pyqtSignal(str)
    alertStatusChanged = pyqtSignal(str, str)
    # Nouvelle alerte temps réel (payload dict pour toast / badge)
    alertReceived = pyqtSignal(object)
    configChanged = pyqtSignal()
    realtimeStateChanged = pyqtSignal()
    statsChanged = pyqtSignal()

    def __init__(self, service: AlertService | None = None):
        super().__init__()
        self._alert_service = service or AlertService()
        self._alerts: List[dict] = []
        self._selected_alert_id = ""
        self._filter_priority = "ALL"
        self._filter_status = "ALL"
        self._filter_camera = "ALL"
        self._search = ""

        self._realtime_running = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)

        self._alert_service.set_new_alert_callback(self._on_service_new_alert)
        self._load_alerts()
        # Démarrer le flux temps réel par défaut si config.enabled
        cfg = self._alert_service.get_config()
        if cfg.get("enabled", True):
            self.startRealtime()

    # ------------------------------------------------------------------ data
    def _load_alerts(self):
        self._alerts = self._alert_service.get_all_alerts()
        self.alertsChanged.emit()
        self.statsChanged.emit()

    def _on_service_new_alert(self, payload: dict):
        self._load_alerts()
        self.alertReceived.emit(payload)

    def _on_tick(self):
        created = self._alert_service.tick_realtime()
        # callback déjà branché si created

    # -------------------------------------------------------------- properties
    @pyqtProperty("QVariantList", notify=alertsChanged)
    def alerts(self):
        filtered = self._alerts
        if self._filter_priority != "ALL":
            filtered = [a for a in filtered if a.get("priority") == self._filter_priority]
        if self._filter_status != "ALL":
            filtered = [a for a in filtered if a.get("status") == self._filter_status]
        if self._filter_camera != "ALL":
            filtered = [a for a in filtered if a.get("camera_id") == self._filter_camera]
        if self._search:
            q = self._search.lower()
            filtered = [
                a
                for a in filtered
                if q in a.get("id", "").lower()
                or q in a.get("title", "").lower()
                or q in a.get("location", "").lower()
                or q in a.get("camera_name", "").lower()
            ]
        return filtered

    @pyqtProperty(str, notify=alertSelected)
    def selectedAlertId(self):
        return self._selected_alert_id

    @pyqtProperty("QVariantMap", notify=alertSelected)
    def selectedAlert(self):
        if self._selected_alert_id:
            return self._alert_service.get_alert_by_id(self._selected_alert_id) or {}
        return {}

    @pyqtProperty(str, notify=alertsChanged)
    def filterPriority(self):
        return self._filter_priority

    @pyqtProperty(str, notify=alertsChanged)
    def filterStatus(self):
        return self._filter_status

    @pyqtProperty(str, notify=alertsChanged)
    def filterCamera(self):
        return self._filter_camera

    @pyqtProperty("QVariantMap", notify=statsChanged)
    def statistics(self):
        return self._alert_service.get_alert_statistics()

    @pyqtProperty(int, notify=statsChanged)
    def openCount(self):
        return self._alert_service.get_open_count()

    @pyqtProperty(int, notify=statsChanged)
    def criticalOpenCount(self):
        return self._alert_service.get_critical_open_count()

    @pyqtProperty("QVariantMap", notify=configChanged)
    def config(self):
        return self._alert_service.get_config()

    @pyqtProperty(bool, notify=realtimeStateChanged)
    def realtimeRunning(self):
        return self._realtime_running

    # ------------------------------------------------------------------ slots
    @pyqtSlot(str)
    def setFilterPriority(self, priority: str):
        self._filter_priority = priority
        self.alertsChanged.emit()

    @pyqtSlot(str)
    def setFilterStatus(self, status: str):
        self._filter_status = status
        self.alertsChanged.emit()

    @pyqtSlot(str)
    def setFilterCamera(self, camera_id: str):
        self._filter_camera = camera_id
        self.alertsChanged.emit()

    @pyqtSlot(str)
    def setSearch(self, text: str):
        self._search = text or ""
        self.alertsChanged.emit()

    @pyqtSlot()
    def clearFilters(self):
        self._filter_priority = "ALL"
        self._filter_status = "ALL"
        self._filter_camera = "ALL"
        self._search = ""
        self.alertsChanged.emit()

    @pyqtSlot(str)
    def selectAlert(self, alert_id: str):
        self._selected_alert_id = alert_id
        self.alertSelected.emit(alert_id)

    @pyqtSlot(str, str)
    def acknowledgeAlert(self, alert_id: str, user: str = "admin"):
        if self._alert_service.acknowledge_alert(alert_id, user):
            self._load_alerts()
            self.alertAcknowledged.emit(alert_id)

    @pyqtSlot(str, str, str)
    def updateAlertStatus(self, alert_id: str, status: str, user: str = "admin"):
        try:
            status_enum = AlertStatus(status)
            if self._alert_service.update_alert_status(alert_id, status_enum, user):
                self._load_alerts()
                self.alertStatusChanged.emit(alert_id, status)
        except ValueError:
            pass

    @pyqtSlot()
    def refreshAlerts(self):
        self._load_alerts()

    @pyqtSlot(result="QStringList")
    def getPriorities(self):
        return ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]

    @pyqtSlot(result="QStringList")
    def getStatuses(self):
        return ["ALL", "OPEN", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED"]

    @pyqtSlot(result="QStringList")
    def getCameras(self):
        cameras = {a.get("camera_id") for a in self._alerts if a.get("camera_id")}
        return ["ALL"] + sorted(cameras)

    # -------------------------------------------------------- real-time control
    @pyqtSlot()
    def startRealtime(self):
        cfg = self._alert_service.get_config()
        interval = int(cfg.get("poll_interval_ms", 5000))
        interval = max(1000, min(interval, 60000))
        self._timer.setInterval(interval)
        if not self._timer.isActive():
            self._timer.start()
        self._realtime_running = True
        self.realtimeStateChanged.emit()

    @pyqtSlot()
    def stopRealtime(self):
        self._timer.stop()
        self._realtime_running = False
        self.realtimeStateChanged.emit()

    @pyqtSlot()
    def toggleRealtime(self):
        if self._realtime_running:
            self.stopRealtime()
        else:
            self.startRealtime()

    @pyqtSlot("QVariantMap")
    def updateConfig(self, data: dict):
        """Met à jour la config temps réel depuis QML."""
        if not isinstance(data, dict):
            return
        # Convertir types QML éventuels
        clean: Dict[str, Any] = {}
        for k, v in data.items():
            clean[str(k)] = v
        self._alert_service.update_config(clean)
        self.configChanged.emit()
        # Réappliquer l'intervalle si en cours
        if self._realtime_running:
            self.startRealtime()
        elif clean.get("enabled", self._alert_service.get_config().get("enabled")):
            self.startRealtime()
        else:
            self.stopRealtime()

    @pyqtSlot(str, result="QVariant")
    def getConfigValue(self, key: str):
        return self._alert_service.get_config().get(key)

    @pyqtSlot(str, "QVariant")
    def setConfigValue(self, key: str, value):
        self.updateConfig({key: value})


    @pyqtSlot(int, result="QVariantList")
    def simulateCriticalBurst(self, count: int = 3):
        """Génère immédiatement N alertes CRITICAL (demo + push)."""
        created = self._alert_service.simulate_critical_burst(count)
        self._load_alerts()
        for payload in created:
            self.alertReceived.emit(payload)
        return created

    @pyqtSlot(str, str, str, str, str, str, str, result="QVariantMap")
    def injectTestAlert(
        self,
        title: str = "Test Alert",
        description: str = "Manually injected test alert",
        priority: str = "HIGH",
        alert_type: str = "INTRUSION",
        camera_id: str = "CAM-TEST",
        camera_name: str = "Test Camera",
        location: str = "Lab",
    ):
        payload = self._alert_service.inject_alert(
            title=title,
            description=description,
            priority=priority,
            alert_type=alert_type,
            camera_id=camera_id,
            camera_name=camera_name,
            location=location,
        )
        self._load_alerts()
        self.alertReceived.emit(payload)
        return payload
