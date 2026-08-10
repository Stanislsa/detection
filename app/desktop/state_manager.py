"""
Gestionnaire d'état centralisé pour l'application desktop.
Centralise les données partagées entre les pages et les services.
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

from app.desktop.models.camera import Camera
from app.desktop.models.alert import Alert
from app.desktop.models.user import User
from app.desktop.models.statistics import Statistics
from app.core.logger import get_logger


class ConnectionState(Enum):
    """États de connexion."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class AppState:
    """
    État global de l'application.
    """
    # Utilisateur connecté
    current_user: Optional[User] = None
    is_authenticated: bool = False
    
    # État de connexion
    connection_state: ConnectionState = ConnectionState.DISCONNECTED
    connection_error: Optional[str] = None
    
    # Données chargées
    cameras: List[Camera] = field(default_factory=list)
    alerts: List[Alert] = field(default_factory=list)
    statistics: Optional[Statistics] = None
    
    # Dernière mise à jour
    last_cameras_update: Optional[datetime] = None
    last_alerts_update: Optional[datetime] = None
    last_statistics_update: Optional[datetime] = None
    
    # État de chargement
    is_loading_cameras: bool = False
    is_loading_alerts: bool = False
    is_loading_statistics: bool = False


class StateManager(QObject):
    """
    Gestionnaire d'état avec signaux PyQt pour les mises à jour.
    Singleton pour garantir un seul état dans l'application.
    """
    
    _instance = None
    
    # Signaux de changement d'état
    user_changed = pyqtSignal(object)  # Optional[User]
    authentication_changed = pyqtSignal(bool)  # is_authenticated
    connection_state_changed = pyqtSignal(str, str)  # state, error
    
    cameras_changed = pyqtSignal(list)  # List[Camera]
    cameras_loading_changed = pyqtSignal(bool)
    
    alerts_changed = pyqtSignal(list)  # List[Alert]
    alerts_loading_changed = pyqtSignal(bool)
    
    statistics_changed = pyqtSignal(object)  # Optional[Statistics]
    statistics_loading_changed = pyqtSignal(bool)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._state = AppState()
            self._logger = get_logger(__name__)
            self._initialized = True
    
    @property
    def state(self) -> AppState:
        """Retourne l'état actuel."""
        return self._state
    
    # ===== UTILISATEUR =====
    
    def set_user(self, user: Optional[User]):
        """
        Définit l'utilisateur connecté.
        
        Args:
            user: Utilisateur connecté ou None
        """
        self._state.current_user = user
        self._state.is_authenticated = user is not None
        self.user_changed.emit(user)
        self.authentication_changed.emit(self._state.is_authenticated)
        self._logger.info(f"Utilisateur changé: {user.username if user else 'None'}")
    
    def get_user(self) -> Optional[User]:
        """Retourne l'utilisateur connecté."""
        return self._state.current_user
    
    def is_authenticated(self) -> bool:
        """Vérifie si un utilisateur est connecté."""
        return self._state.is_authenticated
    
    def logout(self):
        """Déconnecte l'utilisateur."""
        self.set_user(None)
        self._state.cameras = []
        self._state.alerts = []
        self._state.statistics = None
        self._logger.info("Déconnexion effectuée")
    
    # ===== CONNEXION =====
    
    def set_connection_state(self, state: ConnectionState, error: Optional[str] = None):
        """
        Définit l'état de connexion.
        
        Args:
            state: Nouvel état de connexion
            error: Message d'erreur si applicable
        """
        self._state.connection_state = state
        self._state.connection_error = error
        self.connection_state_changed.emit(state.value, error or "")
        self._logger.info(f"État de connexion: {state.value}")
    
    def get_connection_state(self) -> ConnectionState:
        """Retourne l'état de connexion."""
        return self._state.connection_state
    
    # ===== CAMÉRAS =====
    
    def set_cameras(self, cameras: List[Camera]):
        """
        Définit la liste des caméras.
        
        Args:
            cameras: Liste des caméras
        """
        self._state.cameras = cameras
        self._state.last_cameras_update = datetime.now()
        self._state.is_loading_cameras = False
        self.cameras_changed.emit(cameras)
        self.cameras_loading_changed.emit(False)
        self._logger.info(f"Caméras mises à jour: {len(cameras)} caméras")
    
    def get_cameras(self) -> List[Camera]:
        """Retourne la liste des caméras."""
        return self._state.cameras
    
    def get_camera(self, camera_id: int) -> Optional[Camera]:
        """
        Retourne une caméra par son ID.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            Caméra ou None
        """
        for camera in self._state.cameras:
            if camera.id == camera_id:
                return camera
        return None
    
    def set_cameras_loading(self, loading: bool):
        """
        Définit l'état de chargement des caméras.
        
        Args:
            loading: True si en cours de chargement
        """
        self._state.is_loading_cameras = loading
        self.cameras_loading_changed.emit(loading)
    
    def is_loading_cameras(self) -> bool:
        """Vérifie si les caméras sont en cours de chargement."""
        return self._state.is_loading_cameras
    
    def add_camera(self, camera: Camera):
        """
        Ajoute une caméra à la liste.
        
        Args:
            camera: Caméra à ajouter
        """
        self._state.cameras.append(camera)
        self._state.last_cameras_update = datetime.now()
        self.cameras_changed.emit(self._state.cameras)
        self._logger.info(f"Caméra ajoutée: {camera.name}")
    
    def update_camera(self, camera: Camera):
        """
        Met à jour une caméra dans la liste.
        
        Args:
            camera: Caméra mise à jour
        """
        for i, cam in enumerate(self._state.cameras):
            if cam.id == camera.id:
                self._state.cameras[i] = camera
                self._state.last_cameras_update = datetime.now()
                self.cameras_changed.emit(self._state.cameras)
                self._logger.info(f"Caméra mise à jour: {camera.name}")
                return
    
    def remove_camera(self, camera_id: int):
        """
        Supprime une caméra de la liste.
        
        Args:
            camera_id: ID de la caméra à supprimer
        """
        self._state.cameras = [c for c in self._state.cameras if c.id != camera_id]
        self._state.last_cameras_update = datetime.now()
        self.cameras_changed.emit(self._state.cameras)
        self._logger.info(f"Caméra supprimée: ID {camera_id}")
    
    # ===== ALERTES =====
    
    def set_alerts(self, alerts: List[Alert]):
        """
        Définit la liste des alertes.
        
        Args:
            alerts: Liste des alertes
        """
        self._state.alerts = alerts
        self._state.last_alerts_update = datetime.now()
        self._state.is_loading_alerts = False
        self.alerts_changed.emit(alerts)
        self.alerts_loading_changed.emit(False)
        self._logger.info(f"Alertes mises à jour: {len(alerts)} alertes")
    
    def get_alerts(self) -> List[Alert]:
        """Retourne la liste des alertes."""
        return self._state.alerts
    
    def get_alert(self, alert_id: int) -> Optional[Alert]:
        """
        Retourne une alerte par son ID.
        
        Args:
            alert_id: ID de l'alerte
        
        Returns:
            Alerte ou None
        """
        for alert in self._state.alerts:
            if alert.id == alert_id:
                return alert
        return None
    
    def set_alerts_loading(self, loading: bool):
        """
        Définit l'état de chargement des alertes.
        
        Args:
            loading: True si en cours de chargement
        """
        self._state.is_loading_alerts = loading
        self.alerts_loading_changed.emit(loading)
    
    def is_loading_alerts(self) -> bool:
        """Vérifie si les alertes sont en cours de chargement."""
        return self._state.is_loading_alerts
    
    def add_alert(self, alert: Alert):
        """
        Ajoute une alerte à la liste.
        
        Args:
            alert: Alerte à ajouter
        """
        self._state.alerts.insert(0, alert)  # Ajouter au début
        self._state.last_alerts_update = datetime.now()
        self.alerts_changed.emit(self._state.alerts)
        self._logger.info(f"Nouvelle alerte: {alert.alert_type.value}")
    
    def update_alert(self, alert: Alert):
        """
        Met à jour une alerte dans la liste.
        
        Args:
            alert: Alerte mise à jour
        """
        for i, a in enumerate(self._state.alerts):
            if a.id == alert.id:
                self._state.alerts[i] = alert
                self._state.last_alerts_update = datetime.now()
                self.alerts_changed.emit(self._state.alerts)
                self._logger.info(f"Alerte mise à jour: ID {alert.id}")
                return
    
    def remove_alert(self, alert_id: int):
        """
        Supprime une alerte de la liste.
        
        Args:
            alert_id: ID de l'alerte à supprimer
        """
        self._state.alerts = [a for a in self._state.alerts if a.id != alert_id]
        self._state.last_alerts_update = datetime.now()
        self.alerts_changed.emit(self._state.alerts)
        self._logger.info(f"Alerte supprimée: ID {alert_id}")
    
    # ===== STATISTIQUES =====
    
    def set_statistics(self, statistics: Optional[Statistics]):
        """
        Définit les statistiques.
        
        Args:
            statistics: Statistiques ou None
        """
        self._state.statistics = statistics
        self._state.last_statistics_update = datetime.now()
        self._state.is_loading_statistics = False
        self.statistics_changed.emit(statistics)
        self.statistics_loading_changed.emit(False)
        self._logger.info("Statistiques mises à jour")
    
    def get_statistics(self) -> Optional[Statistics]:
        """Retourne les statistiques."""
        return self._state.statistics
    
    def set_statistics_loading(self, loading: bool):
        """
        Définit l'état de chargement des statistiques.
        
        Args:
            loading: True si en cours de chargement
        """
        self._state.is_loading_statistics = loading
        self.statistics_loading_changed.emit(loading)
    
    def is_loading_statistics(self) -> bool:
        """Vérifie si les statistiques sont en cours de chargement."""
        return self._state.is_loading_statistics
    
    # ===== RESET =====
    
    def reset(self):
        """Réinitialise tout l'état."""
        self._state = AppState()
        self.user_changed.emit(None)
        self.authentication_changed.emit(False)
        self.connection_state_changed.emit(ConnectionState.DISCONNECTED.value, "")
        self.cameras_changed.emit([])
        self.alerts_changed.emit([])
        self.statistics_changed.emit(None)
        self._logger.info("État réinitialisé")


def get_state_manager() -> StateManager:
    """
    Fonction utilitaire pour récupérer le StateManager.
    
    Returns:
        Instance singleton du StateManager
    """
    return StateManager()
