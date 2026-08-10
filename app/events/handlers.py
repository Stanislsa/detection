"""
Handlers d'événements.
Implémente les réactions aux événements du bus.
"""

from typing import Optional
from datetime import datetime

from app.events.event_types import (
    Event, EventType, CameraConnectedEvent, CameraDisconnectedEvent,
    FrameReceivedEvent, DetectionResultEvent, FallDetectedEvent,
    IntrusionDetectedEvent, AlertGeneratedEvent, AlertResolvedEvent,
    RecordingStartedEvent, RecordingStoppedEvent, ErrorEvent
)
from app.events.event_bus import EventBus
from app.core.logger import get_logger


class BaseEventHandler:
    """
    Handler de base pour les événements.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialise le handler.
        
        Args:
            event_bus: Instance du bus d'événements
        """
        self.event_bus = event_bus
        self._logger = get_logger(self.__class__.__name__)
        self._subscribed = False
    
    def subscribe(self):
        """Abonne le handler aux événements pertinents."""
        raise NotImplementedError("Subclasses must implement subscribe")
    
    def unsubscribe(self):
        """Désabonne le handler."""
        raise NotImplementedError("Subclasses must implement unsubscribe")
    
    def handle_event(self, event: Event):
        """
        Traite un événement.
        
        Args:
            event: Événement à traiter
        """
        raise NotImplementedError("Subclasses must implement handle_event")


class CameraEventHandler(BaseEventHandler):
    """
    Handler pour les événements de caméras.
    Gère les connexions, déconnexions et changements de statut.
    """
    
    def subscribe(self):
        """Abonne aux événements de caméras."""
        self.event_bus.subscribe(EventType.CAMERA_CONNECTED, self._on_camera_connected)
        self.event_bus.subscribe(EventType.CAMERA_DISCONNECTED, self._on_camera_disconnected)
        self.event_bus.subscribe(EventType.CAMERA_STATUS_CHANGED, self._on_camera_status_changed)
        self._subscribed = True
        self._logger.info("CameraEventHandler abonné")
    
    def unsubscribe(self):
        """Désabonne des événements de caméras."""
        self.event_bus.unsubscribe(EventType.CAMERA_CONNECTED, self._on_camera_connected)
        self.event_bus.unsubscribe(EventType.CAMERA_DISCONNECTED, self._on_camera_disconnected)
        self.event_bus.unsubscribe(EventType.CAMERA_STATUS_CHANGED, self._on_camera_status_changed)
        self._subscribed = False
        self._logger.info("CameraEventHandler désabonné")
    
    def _on_camera_connected(self, event: CameraConnectedEvent):
        """Traite une connexion de caméra."""
        self._logger.info(f"Caméra connectée: {event.camera_name} ({event.camera_id})")
        # Logique métier: mettre à jour l'état, notifier l'UI, etc.
    
    def _on_camera_disconnected(self, event: CameraDisconnectedEvent):
        """Traite une déconnexion de caméra."""
        self._logger.warning(f"Caméra déconnectée: {event.camera_id} - {event.reason}")
        # Logique métier: arrêter les workers, notifier l'UI, etc.
    
    def _on_camera_status_changed(self, event: Event):
        """Traite un changement de statut de caméra."""
        self._logger.info(f"Statut caméra changé: {event.data.get('camera_id')} -> {event.data.get('status')}")


class DetectionEventHandler(BaseEventHandler):
    """
    Handler pour les événements de détection IA.
    Gère les résultats de détection et les alertes générées.
    """
    
    def __init__(self, event_bus: EventBus, alert_service=None):
        """
        Initialise le handler de détection.
        
        Args:
            event_bus: Instance du bus d'événements
            alert_service: Service de gestion des alertes (optionnel)
        """
        super().__init__(event_bus)
        self.alert_service = alert_service
    
    def subscribe(self):
        """Abonne aux événements de détection."""
        self.event_bus.subscribe(EventType.DETECTION_RESULT, self._on_detection_result)
        self.event_bus.subscribe(EventType.FALL_DETECTED, self._on_fall_detected)
        self.event_bus.subscribe(EventType.INTRUSION_DETECTED, self._on_intrusion_detected)
        self.event_bus.subscribe(EventType.MOVEMENT_DETECTED, self._on_movement_detected)
        self._subscribed = True
        self._logger.info("DetectionEventHandler abonné")
    
    def unsubscribe(self):
        """Désabonne des événements de détection."""
        self.event_bus.unsubscribe(EventType.DETECTION_RESULT, self._on_detection_result)
        self.event_bus.unsubscribe(EventType.FALL_DETECTED, self._on_fall_detected)
        self.event_bus.unsubscribe(EventType.INTRUSION_DETECTED, self._on_intrusion_detected)
        self.event_bus.unsubscribe(EventType.MOVEMENT_DETECTED, self._on_movement_detected)
        self._subscribed = False
        self._logger.info("DetectionEventHandler désabonné")
    
    def _on_detection_result(self, event: DetectionResultEvent):
        """Traite un résultat de détection."""
        self._logger.debug(
            f"Détection: {event.camera_id} - "
            f"{len(event.detections)} objets - "
            f"{event.processing_time_ms:.2f}ms"
        )
        # Logique métier: mettre à jour les statistiques, etc.
    
    def _on_fall_detected(self, event: FallDetectedEvent):
        """Traite une détection de chute."""
        self._logger.warning(
            f"Chute détectée: {event.camera_id} - "
            f"confiance: {event.confidence:.2f}"
        )
        # Logique métier: générer une alerte, notifier, enregistrer, etc.
        if self.alert_service:
            # Créer une alerte de chute
            pass
    
    def _on_intrusion_detected(self, event: IntrusionDetectedEvent):
        """Traite une détection d'intrusion."""
        self._logger.warning(
            f"Intrusion détectée: {event.camera_id} - "
            f"zone: {event.zone_id} - "
            f"confiance: {event.confidence:.2f}"
        )
        # Logique métier: générer une alerte, notifier, enregistrer, etc.
    
    def _on_movement_detected(self, event: Event):
        """Traite une détection de mouvement."""
        self._logger.debug(f"Mouvement détecté: {event.data.get('camera_id')}")


class AlertEventHandler(BaseEventHandler):
    """
    Handler pour les événements d'alertes.
    Gère la génération et la résolution des alertes.
    """
    
    def __init__(self, event_bus: EventBus, notification_service=None):
        """
        Initialise le handler d'alertes.
        
        Args:
            event_bus: Instance du bus d'événements
            notification_service: Service de notifications (optionnel)
        """
        super().__init__(event_bus)
        self.notification_service = notification_service
    
    def subscribe(self):
        """Abonne aux événements d'alertes."""
        self.event_bus.subscribe(EventType.ALERT_GENERATED, self._on_alert_generated)
        self.event_bus.subscribe(EventType.ALERT_UPDATED, self._on_alert_updated)
        self.event_bus.subscribe(EventType.ALERT_RESOLVED, self._on_alert_resolved)
        self._subscribed = True
        self._logger.info("AlertEventHandler abonné")
    
    def unsubscribe(self):
        """Désabonne des événements d'alertes."""
        self.event_bus.unsubscribe(EventType.ALERT_GENERATED, self._on_alert_generated)
        self.event_bus.unsubscribe(EventType.ALERT_UPDATED, self._on_alert_updated)
        self.event_bus.unsubscribe(EventType.ALERT_RESOLVED, self._on_alert_resolved)
        self._subscribed = False
        self._logger.info("AlertEventHandler désabonné")
    
    def _on_alert_generated(self, event: AlertGeneratedEvent):
        """Traite la génération d'une alerte."""
        if event.alert:
            self._logger.warning(
                f"Alerte générée: {event.alert.alert_type.value} - "
                f"caméra: {event.alert.camera_id} - "
                f"gravité: {event.alert.severity.value}"
            )
            # Notifier les opérateurs
            if self.notification_service:
                self.notification_service.add_notification(
                    f"Alerte {event.alert.alert_type.value}",
                    f"Caméra {event.alert.camera_name}",
                    event.alert.severity.value
                )
    
    def _on_alert_updated(self, event: Event):
        """Traite la mise à jour d'une alerte."""
        self._logger.info(f"Alerte mise à jour: {event.data.get('alert_id')}")
    
    def _on_alert_resolved(self, event: AlertResolvedEvent):
        """Traite la résolution d'une alerte."""
        self._logger.info(
            f"Alerte résolue: {event.alert_id} - "
            f"par: {event.resolved_by}"
        )


class RecordingEventHandler(BaseEventHandler):
    """
    Handler pour les événements d'enregistrement.
    Gère le démarrage et l'arrêt des enregistrements.
    """
    
    def subscribe(self):
        """Abonne aux événements d'enregistrement."""
        self.event_bus.subscribe(EventType.RECORDING_STARTED, self._on_recording_started)
        self.event_bus.subscribe(EventType.RECORDING_STOPPED, self._on_recording_stopped)
        self.event_bus.subscribe(EventType.SNAPSHOT_SAVED, self._on_snapshot_saved)
        self._subscribed = True
        self._logger.info("RecordingEventHandler abonné")
    
    def unsubscribe(self):
        """Désabonne des événements d'enregistrement."""
        self.event_bus.unsubscribe(EventType.RECORDING_STARTED, self._on_recording_started)
        self.event_bus.unsubscribe(EventType.RECORDING_STOPPED, self._on_recording_stopped)
        self.event_bus.unsubscribe(EventType.SNAPSHOT_SAVED, self._on_snapshot_saved)
        self._subscribed = False
        self._logger.info("RecordingEventHandler désabonné")
    
    def _on_recording_started(self, event: RecordingStartedEvent):
        """Traite le démarrage d'un enregistrement."""
        self._logger.info(f"Enregistrement démarré: {event.camera_id} -> {event.file_path}")
    
    def _on_recording_stopped(self, event: RecordingStoppedEvent):
        """Traite l'arrêt d'un enregistrement."""
        self._logger.info(
            f"Enregistrement arrêté: {event.camera_id} - "
            f"durée: {event.duration_seconds:.2f}s"
        )
    
    def _on_snapshot_saved(self, event: Event):
        """Traite la sauvegarde d'un snapshot."""
        self._logger.debug(f"Snapshot sauvegardé: {event.data.get('file_path')}")


class SystemEventHandler(BaseEventHandler):
    """
    Handler pour les événements système.
    Gère les erreurs, avertissements et changements d'état système.
    """
    
    def subscribe(self):
        """Abonne aux événements système."""
        self.event_bus.subscribe(EventType.ERROR_OCCURRED, self._on_error)
        self.event_bus.subscribe(EventType.WARNING_OCCURRED, self._on_warning)
        self.event_bus.subscribe(EventType.SYSTEM_STARTED, self._on_system_started)
        self.event_bus.subscribe(EventType.SYSTEM_STOPPED, self._on_system_stopped)
        self._subscribed = True
        self._logger.info("SystemEventHandler abonné")
    
    def unsubscribe(self):
        """Désabonne des événements système."""
        self.event_bus.unsubscribe(EventType.ERROR_OCCURRED, self._on_error)
        self.event_bus.unsubscribe(EventType.WARNING_OCCURRED, self._on_warning)
        self.event_bus.unsubscribe(EventType.SYSTEM_STARTED, self._on_system_started)
        self.event_bus.unsubscribe(EventType.SYSTEM_STOPPED, self._on_system_stopped)
        self._subscribed = False
        self._logger.info("SystemEventHandler désabonné")
    
    def _on_error(self, event: ErrorEvent):
        """Traite une erreur système."""
        self._logger.error(
            f"Erreur système: {event.error_type} - {event.error_message}"
        )
        # Logique métier: notifier l'admin, logger dans la DB, etc.
    
    def _on_warning(self, event: Event):
        """Traite un avertissement système."""
        self._logger.warning(f"Avertissement système: {event.data.get('message')}")
    
    def _on_system_started(self, event: Event):
        """Traite le démarrage du système."""
        self._logger.info("Système démarré")
    
    def _on_system_stopped(self, event: Event):
        """Traite l'arrêt du système."""
        self._logger.info("Système arrêté")


class EventHandlerManager:
    """
    Gestionnaire de handlers.
    Centralise l'abonnement/désabonnement de tous les handlers.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialise le gestionnaire.
        
        Args:
            event_bus: Instance du bus d'événements
        """
        self.event_bus = event_bus
        self._handlers: list = []
        self._logger = get_logger(__name__)
    
    def register_handler(self, handler: BaseEventHandler):
        """
        Enregistre un handler.
        
        Args:
            handler: Handler à enregistrer
        """
        self._handlers.append(handler)
        handler.subscribe()
        self._logger.info(f"Handler enregistré: {handler.__class__.__name__}")
    
    def unregister_handler(self, handler: BaseEventHandler):
        """
        Désenregistre un handler.
        
        Args:
            handler: Handler à désenregistrer
        """
        if handler in self._handlers:
            handler.unsubscribe()
            self._handlers.remove(handler)
            self._logger.info(f"Handler désenregistré: {handler.__class__.__name__}")
    
    def register_all(self, alert_service=None, notification_service=None):
        """
        Enregistre tous les handlers par défaut.
        
        Args:
            alert_service: Service d'alertes (optionnel)
            notification_service: Service de notifications (optionnel)
        """
        # Handler caméras
        self.register_handler(CameraEventHandler(self.event_bus))
        
        # Handler détections
        self.register_handler(DetectionEventHandler(self.event_bus, alert_service))
        
        # Handler alertes
        self.register_handler(AlertEventHandler(self.event_bus, notification_service))
        
        # Handler enregistrements
        self.register_handler(RecordingEventHandler(self.event_bus))
        
        # Handler système
        self.register_handler(SystemEventHandler(self.event_bus))
        
        self._logger.info("Tous les handlers enregistrés")
    
    def unregister_all(self):
        """Désenregistre tous les handlers."""
        for handler in self._handlers.copy():
            self.unregister_handler(handler)
        self._logger.info("Tous les handlers désenregistrés")
