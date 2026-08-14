"""
Contrôleur pour la gestion des alertes et incidents.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot
from typing import List

from app.desktop.services.alert_service import AlertService
from app.desktop.models.alert_model import AlertPriority, AlertStatus


class AlertController(QObject):
    """Contrôleur d'alertes accessible depuis QML."""

    alertsChanged = pyqtSignal()
    alertSelected = pyqtSignal(str)
    alertAcknowledged = pyqtSignal(str)
    alertStatusChanged = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self._alert_service = AlertService()
        self._alerts = []
        self._selected_alert_id = ""
        self._filter_priority = "ALL"
        self._filter_status = "ALL"
        self._filter_camera = "ALL"
        self._load_alerts()

    def _load_alerts(self):
        """Charge les alertes depuis le service."""
        self._alerts = self._alert_service.get_all_alerts()
        self.alertsChanged.emit()

    @pyqtProperty('QVariantList', notify=alertsChanged)
    def alerts(self):
        """Retourne la liste des alertes filtrées."""
        filtered = self._alerts
        
        if self._filter_priority != "ALL":
            filtered = [a for a in filtered if a["priority"] == self._filter_priority]
        
        if self._filter_status != "ALL":
            filtered = [a for a in filtered if a["status"] == self._filter_status]
        
        if self._filter_camera != "ALL":
            filtered = [a for a in filtered if a["camera_id"] == self._filter_camera]
        
        return filtered

    @pyqtProperty(str, notify=alertSelected)
    def selectedAlertId(self):
        """Retourne l'ID de l'alerte sélectionnée."""
        return self._selected_alert_id

    @pyqtProperty('QVariantMap', notify=alertSelected)
    def selectedAlert(self):
        """Retourne l'alerte sélectionnée."""
        if self._selected_alert_id:
            return self._alert_service.get_alert_by_id(self._selected_alert_id)
        return {}

    @pyqtProperty(str, notify=alertsChanged)
    def filterPriority(self):
        """Filtre de priorité."""
        return self._filter_priority

    @pyqtProperty(str, notify=alertsChanged)
    def filterStatus(self):
        """Filtre de statut."""
        return self._filter_status

    @pyqtProperty(str, notify=alertsChanged)
    def filterCamera(self):
        """Filtre de caméra."""
        return self._filter_camera

    @pyqtProperty('QVariantMap', notify=alertsChanged)
    def statistics(self):
        """Retourne les statistiques des alertes."""
        return self._alert_service.get_alert_statistics()

    @pyqtSlot(str)
    def setFilterPriority(self, priority: str):
        """Définit le filtre de priorité."""
        self._filter_priority = priority
        self.alertsChanged.emit()

    @pyqtSlot(str)
    def setFilterStatus(self, status: str):
        """Définit le filtre de statut."""
        self._filter_status = status
        self.alertsChanged.emit()

    @pyqtSlot(str)
    def setFilterCamera(self, camera_id: str):
        """Définit le filtre de caméra."""
        self._filter_camera = camera_id
        self.alertsChanged.emit()

    @pyqtSlot()
    def clearFilters(self):
        """Efface tous les filtres."""
        self._filter_priority = "ALL"
        self._filter_status = "ALL"
        self._filter_camera = "ALL"
        self.alertsChanged.emit()

    @pyqtSlot(str)
    def selectAlert(self, alert_id: str):
        """Sélectionne une alerte."""
        self._selected_alert_id = alert_id
        self.alertSelected.emit(alert_id)

    @pyqtSlot(str, str)
    def acknowledgeAlert(self, alert_id: str, user: str = "admin"):
        """Acknowledge une alerte."""
        if self._alert_service.acknowledge_alert(alert_id, user):
            self._load_alerts()
            self.alertAcknowledged.emit(alert_id)

    @pyqtSlot(str, str, str)
    def updateAlertStatus(self, alert_id: str, status: str, user: str = "admin"):
        """Met à jour le statut d'une alerte."""
        try:
            status_enum = AlertStatus(status)
            if self._alert_service.update_alert_status(alert_id, status_enum, user):
                self._load_alerts()
                self.alertStatusChanged.emit(alert_id, status)
        except ValueError:
            pass

    @pyqtSlot()
    def refreshAlerts(self):
        """Rafraîchit la liste des alertes."""
        self._load_alerts()

    @pyqtSlot(result='QStringList')
    def getPriorities(self):
        """Retourne la liste des priorités disponibles."""
        return ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]

    @pyqtSlot(result='QStringList')
    def getStatuses(self):
        """Retourne la liste des statuts disponibles."""
        return ["ALL", "OPEN", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED"]

    @pyqtSlot(result='QStringList')
    def getCameras(self):
        """Retourne la liste des caméras disponibles."""
        cameras = set()
        for alert in self._alerts:
            if alert["camera_id"]:
                cameras.add(alert["camera_id"])
        return ["ALL"] + sorted(list(cameras))
