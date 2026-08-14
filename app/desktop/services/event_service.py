"""
Service pour la gestion des événements.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import random

from app.desktop.models.event_model import Event, EventType, EventSeverity, EventStatus


class EventService:
    """Service de gestion des événements."""
    
    def __init__(self):
        self._events: Dict[str, Event] = {}
        self._initialize_demo_events()
    
    def _initialize_demo_events(self) -> None:
        """Initialise des événements de démonstration."""
        demo_events = [
            Event(
                id=str(uuid.uuid4()),
                type=EventType.PERSON_DETECTED,
                severity=EventSeverity.HIGH,
                camera_id="cam1",
                camera_name="Camera 1",
                timestamp=datetime.now() - timedelta(minutes=5),
                description="Person detected in Zone A",
                metadata={"confidence": 0.92, "bbox": [100, 150, 80, 200]}
            ),
            Event(
                id=str(uuid.uuid4()),
                type=EventType.MOTION_DETECTED,
                severity=EventSeverity.MEDIUM,
                camera_id="cam2",
                camera_name="Camera 2",
                timestamp=datetime.now() - timedelta(minutes=15),
                description="Motion detected in parking area",
                metadata={"confidence": 0.75}
            ),
            Event(
                id=str(uuid.uuid4()),
                type=EventType.FALL_DETECTED,
                severity=EventSeverity.CRITICAL,
                camera_id="cam3",
                camera_name="Camera 3",
                timestamp=datetime.now() - timedelta(minutes=30),
                description="Fall detected in warehouse",
                metadata={"confidence": 0.88, "bbox": [200, 300, 100, 150]}
            ),
            Event(
                id=str(uuid.uuid4()),
                type=EventType.INTRUSION,
                severity=EventSeverity.HIGH,
                camera_id="cam4",
                camera_name="Camera 4",
                timestamp=datetime.now() - timedelta(hours=1),
                description="Unauthorized access detected",
                metadata={"confidence": 0.95}
            ),
            Event(
                id=str(uuid.uuid4()),
                type=EventType.CAMERA_OFFLINE,
                severity=EventSeverity.LOW,
                camera_id="cam5",
                camera_name="Camera 5",
                timestamp=datetime.now() - timedelta(hours=2),
                description="Camera went offline",
                status=EventStatus.RESOLVED
            ),
            Event(
                id=str(uuid.uuid4()),
                type=EventType.CAMERA_ONLINE,
                severity=EventSeverity.INFO,
                camera_id="cam5",
                camera_name="Camera 5",
                timestamp=datetime.now() - timedelta(hours=1, minutes=45),
                description="Camera came back online",
                status=EventStatus.RESOLVED
            ),
            Event(
                id=str(uuid.uuid4()),
                type=EventType.PERSON_DETECTED,
                severity=EventSeverity.MEDIUM,
                camera_id="cam1",
                camera_name="Camera 1",
                timestamp=datetime.now() - timedelta(hours=3),
                description="Person detected at entrance",
                metadata={"confidence": 0.85},
                status=EventStatus.ACKNOWLEDGED
            ),
            Event(
                id=str(uuid.uuid4()),
                type=EventType.MOTION_DETECTED,
                severity=EventSeverity.LOW,
                camera_id="cam6",
                camera_name="Camera 6",
                timestamp=datetime.now() - timedelta(hours=5),
                description="Motion detected in storage",
                metadata={"confidence": 0.60},
                status=EventStatus.RESOLVED
            )
        ]
        
        for event in demo_events:
            self._events[event.id] = event
    
    def get_all_events(self) -> List[Event]:
        """Récupère tous les événements."""
        return sorted(self._events.values(), key=lambda e: e.timestamp, reverse=True)
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """Récupère un événement par ID."""
        return self._events.get(event_id)
    
    def add_event(self, event: Event) -> Event:
        """Ajoute un nouvel événement."""
        self._events[event.id] = event
        return event
    
    def create_event(
        self,
        type: EventType,
        severity: EventSeverity,
        camera_id: str,
        camera_name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """Crée un nouvel événement."""
        event = Event(
            id=str(uuid.uuid4()),
            type=type,
            severity=severity,
            camera_id=camera_id,
            camera_name=camera_name,
            timestamp=datetime.now(),
            description=description,
            metadata=metadata or {}
        )
        self._events[event.id] = event
        return event
    
    def update_event_status(self, event_id: str, status: EventStatus) -> Optional[Event]:
        """Met à jour le statut d'un événement."""
        event = self._events.get(event_id)
        if event:
            event.status = status
            return event
        return None
    
    def acknowledge_event(self, event_id: str) -> Optional[Event]:
        """Acknowledge un événement."""
        return self.update_event_status(event_id, EventStatus.ACKNOWLEDGED)
    
    def resolve_event(self, event_id: str) -> Optional[Event]:
        """Résout un événement."""
        return self.update_event_status(event_id, EventStatus.RESOLVED)
    
    def delete_event(self, event_id: str) -> bool:
        """Supprime un événement."""
        if event_id in self._events:
            del self._events[event_id]
            return True
        return False
    
    def get_events_by_camera(self, camera_id: str) -> List[Event]:
        """Récupère les événements d'une caméra."""
        return [e for e in self._events.values() if e.camera_id == camera_id]
    
    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """Récupère les événements par type."""
        return [e for e in self._events.values() if e.type == event_type]
    
    def get_events_by_severity(self, severity: EventSeverity) -> List[Event]:
        """Récupère les événements par sévérité."""
        return [e for e in self._events.values() if e.severity == severity]
    
    def get_events_by_status(self, status: EventStatus) -> List[Event]:
        """Récupère les événements par statut."""
        return [e for e in self._events.values() if e.status == status]
    
    def get_events_in_range(self, start: datetime, end: datetime) -> List[Event]:
        """Récupère les événements dans une plage de temps."""
        return [e for e in self._events.values() if start <= e.timestamp <= end]
    
    def get_recent_events(self, hours: int = 24) -> List[Event]:
        """Récupère les événements récents."""
        threshold = datetime.now() - timedelta(hours=hours)
        return [e for e in self._events.values() if e.timestamp >= threshold]
    
    def get_event_statistics(self) -> Dict[str, int]:
        """Récupère les statistiques des événements."""
        total = len(self._events)
        open_count = len(self.get_events_by_status(EventStatus.OPEN))
        acknowledged_count = len(self.get_events_by_status(EventStatus.ACKNOWLEDGED))
        resolved_count = len(self.get_events_by_status(EventStatus.RESOLVED))
        
        critical_count = len(self.get_events_by_severity(EventSeverity.CRITICAL))
        high_count = len(self.get_events_by_severity(EventSeverity.HIGH))
        
        return {
            "total": total,
            "open": open_count,
            "acknowledged": acknowledged_count,
            "resolved": resolved_count,
            "critical": critical_count,
            "high": high_count
        }
