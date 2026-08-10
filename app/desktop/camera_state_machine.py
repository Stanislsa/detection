"""
Machine à états pour le cycle de vie des caméras.
Formalise les transitions : Disconnected → Connecting → Connected → Streaming → Detecting → Recording → Error → Reconnecting.
"""

from typing import Optional, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from threading import Lock

from app.core.logger import get_logger
from app.core.exceptions import CameraException


class CameraState(Enum):
    """États d'une caméra."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    DETECTING = "detecting"
    RECORDING = "recording"
    ERROR = "error"
    RECONNECTING = "reconnecting"


class CameraEvent(Enum):
    """Événements qui déclenchent des transitions."""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    STREAM_START = "stream_start"
    STREAM_STOP = "stream_stop"
    DETECTION_START = "detection_start"
    DETECTION_STOP = "detection_stop"
    RECORDING_START = "recording_start"
    RECORDING_STOP = "recording_stop"
    ERROR_OCCURRED = "error_occurred"
    ERROR_RESOLVED = "error_resolved"
    RECONNECT = "reconnect"


@dataclass
class StateTransition:
    """Transition d'état."""
    from_state: CameraState
    event: CameraEvent
    to_state: CameraState
    action: Optional[Callable] = None
    guard: Optional[Callable] = None  # Condition pour autoriser la transition


@dataclass
class StateInfo:
    """Informations sur l'état actuel."""
    state: CameraState
    entered_at: datetime
    last_transition: Optional[CameraEvent] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CameraStateMachine:
    """
    Machine à états pour le cycle de vie des caméras.
    Gère les transitions entre états avec gardes et actions.
    """
    
    def __init__(self, camera_id: str):
        """
        Initialise la machine à états.
        
        Args:
            camera_id: ID de la caméra
        """
        self.camera_id = camera_id
        self._logger = get_logger(f"CameraStateMachine.{camera_id}")
        self._lock = Lock()
        
        # État actuel
        self._current_state = CameraState.DISCONNECTED
        self._state_info = StateInfo(
            state=CameraState.DISCONNECTED,
            entered_at=datetime.now()
        )
        
        # Transitions définies
        self._transitions: Dict[tuple, StateTransition] = {}
        self._setup_transitions()
        
        # Callbacks
        self._state_callbacks: Dict[CameraState, list] = {}
    
    def _setup_transitions(self):
        """Configure les transitions de la machine à états."""
        # Disconnected → Connecting
        self._add_transition(
            from_state=CameraState.DISCONNECTED,
            event=CameraEvent.CONNECT,
            to_state=CameraState.CONNECTING,
            action=self._on_connecting
        )
        
        # Connecting → Connected
        self._add_transition(
            from_state=CameraState.CONNECTING,
            event=CameraEvent.STREAM_START,
            to_state=CameraState.CONNECTED,
            action=self._on_connected
        )
        
        # Connecting → Error
        self._add_transition(
            from_state=CameraState.CONNECTING,
            event=CameraEvent.ERROR_OCCURRED,
            to_state=CameraState.ERROR,
            action=self._on_error
        )
        
        # Connected → Streaming
        self._add_transition(
            from_state=CameraState.CONNECTED,
            event=CameraEvent.STREAM_START,
            to_state=CameraState.STREAMING,
            action=self._on_streaming_start
        )
        
        # Connected → Disconnected
        self._add_transition(
            from_state=CameraState.CONNECTED,
            event=CameraEvent.DISCONNECT,
            to_state=CameraState.DISCONNECTED,
            action=self._on_disconnected
        )
        
        # Streaming → Detecting
        self._add_transition(
            from_state=CameraState.STREAMING,
            event=CameraEvent.DETECTION_START,
            to_state=CameraState.DETECTING,
            action=self._on_detection_start
        )
        
        # Streaming → Recording
        self._add_transition(
            from_state=CameraState.STREAMING,
            event=CameraEvent.RECORDING_START,
            to_state=CameraState.RECORDING,
            action=self._on_recording_start
        )
        
        # Streaming → Disconnected
        self._add_transition(
            from_state=CameraState.STREAMING,
            event=CameraEvent.DISCONNECT,
            to_state=CameraState.DISCONNECTED,
            action=self._on_disconnected
        )
        
        # Streaming → Error
        self._add_transition(
            from_state=CameraState.STREAMING,
            event=CameraEvent.ERROR_OCCURRED,
            to_state=CameraState.ERROR,
            action=self._on_error
        )
        
        # Detecting → Streaming
        self._add_transition(
            from_state=CameraState.DETECTING,
            event=CameraEvent.DETECTION_STOP,
            to_state=CameraState.STREAMING,
            action=self._on_detection_stop
        )
        
        # Detecting → Recording
        self._add_transition(
            from_state=CameraState.DETECTING,
            event=CameraEvent.RECORDING_START,
            to_state=CameraState.RECORDING,
            action=self._on_recording_start
        )
        
        # Detecting → Error
        self._add_transition(
            from_state=CameraState.DETECTING,
            event=CameraEvent.ERROR_OCCURRED,
            to_state=CameraState.ERROR,
            action=self._on_error
        )
        
        # Recording → Streaming
        self._add_transition(
            from_state=CameraState.RECORDING,
            event=CameraEvent.RECORDING_STOP,
            to_state=CameraState.STREAMING,
            action=self._on_recording_stop
        )
        
        # Recording → Detecting
        self._add_transition(
            from_state=CameraState.RECORDING,
            event=CameraEvent.DETECTION_START,
            to_state=CameraState.DETECTING,
            action=self._on_detection_start
        )
        
        # Recording → Error
        self._add_transition(
            from_state=CameraState.RECORDING,
            event=CameraEvent.ERROR_OCCURRED,
            to_state=CameraState.ERROR,
            action=self._on_error
        )
        
        # Error → Reconnecting
        self._add_transition(
            from_state=CameraState.ERROR,
            event=CameraEvent.RECONNECT,
            to_state=CameraState.RECONNECTING,
            action=self._on_reconnecting
        )
        
        # Error → Disconnected
        self._add_transition(
            from_state=CameraState.ERROR,
            event=CameraEvent.DISCONNECT,
            to_state=CameraState.DISCONNECTED,
            action=self._on_disconnected
        )
        
        # Reconnecting → Connecting
        self._add_transition(
            from_state=CameraState.RECONNECTING,
            event=CameraEvent.CONNECT,
            to_state=CameraState.CONNECTING,
            action=self._on_connecting
        )
        
        # Reconnecting → Error
        self._add_transition(
            from_state=CameraState.RECONNECTING,
            event=CameraEvent.ERROR_OCCURRED,
            to_state=CameraState.ERROR,
            action=self._on_error
        )
    
    def _add_transition(self, from_state: CameraState, event: CameraEvent, to_state: CameraState, action: Optional[Callable] = None, guard: Optional[Callable] = None):
        """
        Ajoute une transition à la machine à états.
        
        Args:
            from_state: État de départ
            event: Événement déclencheur
            to_state: État d'arrivée
            action: Action à exécuter lors de la transition
            guard: Condition pour autoriser la transition
        """
        self._transitions[(from_state, event)] = StateTransition(
            from_state=from_state,
            event=event,
            to_state=to_state,
            action=action,
            guard=guard
        )
    
    def trigger(self, event: CameraEvent, **kwargs) -> bool:
        """
        Déclenche un événement pour effectuer une transition.
        
        Args:
            event: Événement à déclencher
            **kwargs: Arguments pour l'action
        
        Returns:
            True si la transition a réussi
        """
        with self._lock:
            key = (self._current_state, event)
            
            if key not in self._transitions:
                self._logger.warning(f"Transition non définie: {self._current_state.value} + {event.value}")
                return False
            
            transition = self._transitions[key]
            
            # Vérifier la garde
            if transition.guard and not transition.guard(**kwargs):
                self._logger.debug(f"Transition bloquée par la garde: {event.value}")
                return False
            
            # Effectuer la transition
            old_state = self._current_state
            new_state = transition.to_state
            
            self._logger.info(f"Transition: {old_state.value} → {new_state.value} (event: {event.value})")
            
            self._current_state = new_state
            self._state_info = StateInfo(
                state=new_state,
                entered_at=datetime.now(),
                last_transition=event,
                metadata=kwargs
            )
            
            # Exécuter l'action
            if transition.action:
                try:
                    transition.action(**kwargs)
                except Exception as e:
                    self._logger.error(f"Erreur lors de l'action de transition: {e}")
            
            # Notifier les callbacks
            self._notify_state_callbacks(new_state)
            
            return True
    
    def get_current_state(self) -> CameraState:
        """Retourne l'état actuel."""
        with self._lock:
            return self._current_state
    
    def get_state_info(self) -> StateInfo:
        """Retourne les informations sur l'état actuel."""
        with self._lock:
            return self._state_info
    
    def get_state_duration(self) -> float:
        """
        Retourne la durée dans l'état actuel en secondes.
        
        Returns:
            Durée en secondes
        """
        with self._lock:
            return (datetime.now() - self._state_info.entered_at).total_seconds()
    
    def register_state_callback(self, state: CameraState, callback: Callable):
        """
        Enregistre un callback pour un état.
        
        Args:
            state: État à écouter
            callback: Fonction à appeler
        """
        if state not in self._state_callbacks:
            self._state_callbacks[state] = []
        self._state_callbacks[state].append(callback)
    
    def _notify_state_callbacks(self, state: CameraState):
        """Notifie les callbacks enregistrés pour un état."""
        if state in self._state_callbacks:
            for callback in self._state_callbacks[state]:
                try:
                    callback(self.camera_id, state)
                except Exception as e:
                    self._logger.error(f"Erreur dans le callback d'état: {e}")
    
    # ===== Actions de transition =====
    
    def _on_connecting(self, **kwargs):
        """Action lors de la transition vers CONNECTING."""
        self._logger.info(f"Connexion en cours pour la caméra {self.camera_id}")
    
    def _on_connected(self, **kwargs):
        """Action lors de la transition vers CONNECTED."""
        self._logger.info(f"Caméra {self.camera_id} connectée")
    
    def _on_streaming_start(self, **kwargs):
        """Action lors de la transition vers STREAMING."""
        self._logger.info(f"Streaming démarré pour la caméra {self.camera_id}")
    
    def _on_detection_start(self, **kwargs):
        """Action lors de la transition vers DETECTING."""
        self._logger.info(f"Détection IA démarrée pour la caméra {self.camera_id}")
    
    def _on_detection_stop(self, **kwargs):
        """Action lors de la transition depuis DETECTING."""
        self._logger.info(f"Détection IA arrêtée pour la caméra {self.camera_id}")
    
    def _on_recording_start(self, **kwargs):
        """Action lors de la transition vers RECORDING."""
        self._logger.info(f"Enregistrement démarré pour la caméra {self.camera_id}")
    
    def _on_recording_stop(self, **kwargs):
        """Action lors de la transition depuis RECORDING."""
        self._logger.info(f"Enregistrement arrêté pour la caméra {self.camera_id}")
    
    def _on_disconnected(self, **kwargs):
        """Action lors de la transition vers DISCONNECTED."""
        self._logger.info(f"Caméra {self.camera_id} déconnectée")
    
    def _on_error(self, error_message: str = "", **kwargs):
        """Action lors de la transition vers ERROR."""
        self._logger.error(f"Erreur pour la caméra {self.camera_id}: {error_message}")
        self._state_info.error_message = error_message
    
    def _on_reconnecting(self, **kwargs):
        """Action lors de la transition vers RECONNECTING."""
        self._logger.info(f"Reconnexion en cours pour la caméra {self.camera_id}")
    
    def reset(self):
        """Réinitialise la machine à états à l'état DISCONNECTED."""
        with self._lock:
            self._current_state = CameraState.DISCONNECTED
            self._state_info = StateInfo(
                state=CameraState.DISCONNECTED,
                entered_at=datetime.now()
            )
            self._logger.info(f"Machine à états réinitialisée pour la caméra {self.camera_id}")
    
    def is_operational(self) -> bool:
        """
        Vérifie si la caméra est opérationnelle.
        
        Returns:
            True si la caméra peut recevoir des frames
        """
        with self._lock:
            return self._current_state in [
                CameraState.CONNECTED,
                CameraState.STREAMING,
                CameraState.DETECTING,
                CameraState.RECORDING
            ]
    
    def can_detect(self) -> bool:
        """
        Vérifie si la détection peut être activée.
        
        Returns:
            True si la détection peut être activée
        """
        with self._lock:
            return self._current_state in [
                CameraState.CONNECTED,
                CameraState.STREAMING,
                CameraState.RECORDING
            ]
    
    def can_record(self) -> bool:
        """
        Vérifie si l'enregistrement peut être activé.
        
        Returns:
            True si l'enregistrement peut être activé
        """
        with self._lock:
            return self._current_state in [
                CameraState.CONNECTED,
                CameraState.STREAMING,
                CameraState.DETECTING
            ]
