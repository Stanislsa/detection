"""
Contrôleur pour la gestion des événements (pont avec QML).
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot

from app.desktop.models.event_model import Event, EventType, EventSeverity, EventStatus
from app.desktop.services.event_service import EventService


class EventController(QObject):
    """Contrôleur pour les événements exposé à QML."""
    
    eventsChanged = pyqtSignal()
    eventAdded = pyqtSignal(str)
    eventUpdated = pyqtSignal(str)
    eventDeleted = pyqtSignal(str)
    
    def __init__(self, service: EventService):
        super().__init__()
        self._service = service
    
    @pyqtProperty(list, notify=eventsChanged)
    def events(self) -> List[Dict[str, Any]]:
        """Liste des événements."""
        return [event.to_dict() for event in self._service.get_all_events()]
    
    @pyqtProperty(int, notify=eventsChanged)
    def eventCount(self) -> int:
        """Nombre total d'événements."""
        return len(self._service.get_all_events())
    
    @pyqtProperty(int, notify=eventsChanged)
    def openCount(self) -> int:
        """Nombre d'événements ouverts."""
        return len(self._service.get_events_by_status(EventStatus.OPEN))
    
    @pyqtProperty(int, notify=eventsChanged)
    def criticalCount(self) -> int:
        """Nombre d'événements critiques."""
        return len(self._service.get_events_by_severity(EventSeverity.CRITICAL))
    
    @pyqtSlot(str, result='QVariantMap')
    def getEvent(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un événement par ID."""
        event = self._service.get_event(event_id)
        return event.to_dict() if event else None
    
    @pyqtSlot(str, str, str, str, str, str, result=str)
    def createEvent(
        self,
        type: str,
        severity: str,
        camera_id: str,
        camera_name: str,
        description: str = "",
        metadata: str = ""
    ) -> str:
        """Crée un nouvel événement."""
        event = self._service.create_event(
            type=EventType(type),
            severity=EventSeverity(severity),
            camera_id=camera_id,
            camera_name=camera_name,
            description=description if description else None,
            metadata={"raw": metadata} if metadata else None
        )
        self.eventsChanged.emit()
        self.eventAdded.emit(event.id)
        return event.id
    
    @pyqtSlot(str, str, result=bool)
    def updateEventStatus(self, event_id: str, status: str) -> bool:
        """Met à jour le statut d'un événement."""
        event = self._service.update_event_status(event_id, EventStatus(status))
        if event:
            self.eventsChanged.emit()
            self.eventUpdated.emit(event_id)
            return True
        return False
    
    @pyqtSlot(str, result=bool)
    def acknowledgeEvent(self, event_id: str) -> bool:
        """Acknowledge un événement."""
        event = self._service.acknowledge_event(event_id)
        if event:
            self.eventsChanged.emit()
            self.eventUpdated.emit(event_id)
            return True
        return False
    
    @pyqtSlot(str, result=bool)
    def resolveEvent(self, event_id: str) -> bool:
        """Résout un événement."""
        event = self._service.resolve_event(event_id)
        if event:
            self.eventsChanged.emit()
            self.eventUpdated.emit(event_id)
            return True
        return False
    
    @pyqtSlot(str, result=bool)
    def deleteEvent(self, event_id: str) -> bool:
        """Supprime un événement."""
        success = self._service.delete_event(event_id)
        if success:
            self.eventsChanged.emit()
            self.eventDeleted.emit(event_id)
        return success
    
    @pyqtSlot(str, result=list)
    def getEventsByCamera(self, camera_id: str) -> List[Dict[str, Any]]:
        """Récupère les événements d'une caméra."""
        return [event.to_dict() for event in self._service.get_events_by_camera(camera_id)]
    
    @pyqtSlot(str, result=list)
    def getEventsByType(self, event_type: str) -> List[Dict[str, Any]]:
        """Récupère les événements par type."""
        return [event.to_dict() for event in self._service.get_events_by_type(EventType(event_type))]
    
    @pyqtSlot(str, result=list)
    def getEventsBySeverity(self, severity: str) -> List[Dict[str, Any]]:
        """Récupère les événements par sévérité."""
        return [event.to_dict() for event in self._service.get_events_by_severity(EventSeverity(severity))]
    
    @pyqtSlot(str, result=list)
    def getEventsByStatus(self, status: str) -> List[Dict[str, Any]]:
        """Récupère les événements par statut."""
        return [event.to_dict() for event in self._service.get_events_by_status(EventStatus(status))]
    
    @pyqtSlot(int, result=list)
    def getRecentEvents(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Récupère les événements récents."""
        return [event.to_dict() for event in self._service.get_recent_events(hours)]
    
    @pyqtSlot(result='QVariantMap')
    def getEventStatistics(self) -> Dict[str, int]:
        """Récupère les statistiques des événements."""
        return self._service.get_event_statistics()
    
    def refresh(self) -> None:
        """Rafraîchit les données des événements."""
        self.eventsChanged.emit()
