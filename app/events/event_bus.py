"""
Bus d'événements centralisé.
Permet le découplage des composants via un pattern publish/subscribe.
"""

from typing import Callable, Dict, List, Optional, Any
from collections import defaultdict
from threading import Lock
from datetime import datetime

from app.events.event_types import Event, EventType
from app.core.logger import get_logger


class EventBus:
    """
    Bus d'événements avec pattern publish/subscribe.
    Singleton pour garantir un seul bus dans l'application.
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
            self._event_history: List[Event] = []
            self._max_history_size = 1000
            self._lock = Lock()
            self._logger = get_logger(__name__)
            self._initialized = True
    
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> bool:
        """
        Abonne un handler à un type d'événement.
        
        Args:
            event_type: Type d'événement à écouter
            handler: Fonction appelée quand l'événement survient
        
        Returns:
            True si succès
        """
        with self._lock:
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)
                self._logger.debug(f"Handler abonné à {event_type.value}")
                return True
            return False
    
    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> bool:
        """
        Désabonne un handler d'un type d'événement.
        
        Args:
            event_type: Type d'événement
            handler: Handler à désabonner
        
        Returns:
            True si succès
        """
        with self._lock:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                self._logger.debug(f"Handler désabonné de {event_type.value}")
                return True
            return False
    
    def publish(self, event: Event) -> bool:
        """
        Publie un événement vers tous les abonnés.
        
        Args:
            event: Événement à publier
        
        Returns:
            True si succès
        """
        try:
            # Ajouter à l'historique
            with self._lock:
                self._event_history.append(event)
                if len(self._event_history) > self._max_history_size:
                    self._event_history.pop(0)
            
            # Notifier les abonnés
            subscribers = self._subscribers.get(event.event_type, [])
            
            self._logger.debug(f"Publication de {event.event_type.value} vers {len(subscribers)} abonnés")
            
            for handler in subscribers:
                try:
                    handler(event)
                except Exception as e:
                    self._logger.error(f"Erreur dans le handler pour {event.event_type.value}: {e}")
            
            return True
            
        except Exception as e:
            self._logger.error(f"Erreur lors de la publication de l'événement: {e}")
            return False
    
    def publish_async(self, event: Event):
        """
        Publie un événement de manière asynchrone.
        À utiliser pour les événements qui ne doivent pas bloquer.
        
        Args:
            event: Événement à publier
        """
        import threading
        thread = threading.Thread(target=self.publish, args=(event,))
        thread.daemon = True
        thread.start()
    
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """
        Récupère l'historique des événements.
        
        Args:
            event_type: Filtrer par type (optionnel)
            limit: Nombre maximum d'événements
        
        Returns:
            Liste des événements
        """
        with self._lock:
            if event_type:
                events = [e for e in self._event_history if e.event_type == event_type]
            else:
                events = self._event_history.copy()
            
            return events[-limit:]
    
    def clear_history(self):
        """Efface l'historique des événements."""
        with self._lock:
            self._event_history.clear()
            self._logger.info("Historique des événements effacé")
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """
        Retourne le nombre d'abonnés pour un type d'événement.
        
        Args:
            event_type: Type d'événement
        
        Returns:
            Nombre d'abonnés
        """
        with self._lock:
            return len(self._subscribers.get(event_type, []))
    
    def get_all_subscriber_counts(self) -> Dict[EventType, int]:
        """
        Retourne le nombre d'abonnés pour tous les types d'événements.
        
        Returns:
            Dictionnaire {event_type: count}
        """
        with self._lock:
            return {event_type: len(handlers) for event_type, handlers in self._subscribers.items()}


class EventFilter:
    """
    Filtre d'événements pour créer des abonnements conditionnels.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialise le filtre.
        
        Args:
            event_bus: Instance du bus d'événements
        """
        self.event_bus = event_bus
        self._filters: Dict[Callable, Callable] = {}
    
    def subscribe_with_filter(
        self,
        event_type: EventType,
        handler: Callable[[Event], None],
        filter_func: Callable[[Event], bool]
    ) -> bool:
        """
        Abonne un handler avec un filtre conditionnel.
        
        Args:
            event_type: Type d'événement
            handler: Handler à appeler
            filter_func: Fonction de filtre (retourne True si handler doit être appelé)
        
        Returns:
            True si succès
        """
        def filtered_handler(event: Event):
            if filter_func(event):
                handler(event)
        
        self._filters[handler] = filtered_handler
        return self.event_bus.subscribe(event_type, filtered_handler)
    
    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> bool:
        """
        Désabonne un handler avec filtre.
        
        Args:
            event_type: Type d'événement
            handler: Handler à désabonner
        
        Returns:
            True si succès
        """
        filtered_handler = self._filters.get(handler)
        if filtered_handler:
            return self.event_bus.unsubscribe(event_type, filtered_handler)
        return False


def get_event_bus() -> EventBus:
    """
    Fonction utilitaire pour récupérer l'instance du bus d'événements.
    
    Returns:
        Instance singleton du EventBus
    """
    return EventBus()
