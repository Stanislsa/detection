"""
Contrôleur pour la gestion de la santé des services (pont avec QML).
"""

from typing import List, Optional, Dict, Any

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot

from app.desktop.models.service_health_model import (
    ServiceHealth, SystemHealthOverview,
    ServiceStatus, ServiceType
)
from app.desktop.services.service_health_service import ServiceHealthService


class ServiceHealthController(QObject):
    """Contrôleur pour la santé des services exposé à QML."""
    
    healthChanged = pyqtSignal()
    
    def __init__(self, service: ServiceHealthService):
        super().__init__()
        self._service = service
    
    @pyqtProperty('QVariantMap', notify=healthChanged)
    def systemOverview(self) -> Dict[str, Any]:
        """Vue d'ensemble du système."""
        return self._service.get_system_overview().to_dict()
    
    @pyqtProperty(list, notify=healthChanged)
    def services(self) -> List[Dict[str, Any]]:
        """Liste des services."""
        return [s.to_dict() for s in self._service.get_all_services()]
    
    @pyqtProperty('QVariantMap', notify=healthChanged)
    def healthStatistics(self) -> Dict[str, Any]:
        """Statistiques de santé."""
        return self._service.get_health_statistics()
    
    @pyqtProperty(str, notify=healthChanged)
    def overallStatus(self) -> str:
        """Statut global du système."""
        return self._service.get_system_overview().overall_status.value
    
    @pyqtSlot(str, result='QVariantMap')
    def getService(self, service_type: str) -> Optional[Dict[str, Any]]:
        """Récupère un service par type."""
        service = self._service.get_service_health(ServiceType(service_type))
        return service.to_dict() if service else None
    
    @pyqtSlot()
    def refreshHealth(self):
        """Rafraîchit la santé des services."""
        self._service.simulate_health_changes()
        self.healthChanged.emit()
    
    def refresh(self) -> None:
        """Rafraîchit les données de santé."""
        self.healthChanged.emit()
