"""
Contrôleur pour la gestion de la santé système (pont avec QML).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot

from desktop.models.system_model import (
    SystemMetric, ComponentHealth, SystemOverview,
    HealthStatus, ComponentType
)
from desktop.services.health_service import HealthService
from desktop.workers.monitoring_worker import MonitoringWorker


class HealthController(QObject):
    """Contrôleur pour la santé système exposé à QML."""
    
    metricsChanged = pyqtSignal()
    healthStatusChanged = pyqtSignal()
    
    def __init__(self, service: HealthService):
        super().__init__()
        self._service = service
        self._monitoring_worker = MonitoringWorker(service, update_interval=1000)
        self._monitoring_worker.metricsUpdated.connect(self._on_metrics_updated)
        self._monitoring_worker.start()
    
    def _on_metrics_updated(self):
        """Appelé quand les métriques sont mises à jour."""
        self.metricsChanged.emit()
        self.healthStatusChanged.emit()
    
    @pyqtProperty('QVariantMap', notify=healthStatusChanged)
    def systemOverview(self) -> Dict[str, Any]:
        """Vue d'ensemble du système."""
        return self._service.get_system_overview().to_dict()
    
    @pyqtProperty(list, notify=metricsChanged)
    def components(self) -> List[Dict[str, Any]]:
        """Liste des composants."""
        return [c.to_dict() for c in self._service.get_all_components()]
    
    @pyqtProperty('QVariantMap', notify=healthStatusChanged)
    def healthStatistics(self) -> Dict[str, Any]:
        """Statistiques de santé."""
        return self._service.get_health_statistics()
    
    @pyqtProperty(str, notify=healthStatusChanged)
    def overallStatus(self) -> str:
        """Statut global du système."""
        return self._service.get_system_overview().overall_status.value
    
    @pyqtSlot(str, result='QVariantMap')
    def getComponent(self, component_type: str) -> Optional[Dict[str, Any]]:
        """Récupère un composant par type."""
        component = self._service.get_component_health(ComponentType(component_type))
        return component.to_dict() if component else None
    
    @pyqtSlot(str, int, result=list)
    def getMetricHistory(self, component_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère l'historique des métriques d'un composant."""
        metrics = self._service.get_metric_history(ComponentType(component_type), limit)
        return [m.to_dict() for m in metrics]
    
    @pyqtSlot()
    def refreshMetrics(self):
        """Rafraîchit les métriques."""
        self._service.update_all_metrics()
        self.metricsChanged.emit()
    
    def cleanup(self):
        """Nettoie les ressources."""
        self._monitoring_worker.stop()
