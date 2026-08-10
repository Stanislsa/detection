"""
Worker pour la communication WebSocket.
Utilise QThread pour ne pas bloquer l'interface lors des communications réseau.
"""

from PyQt6.QtCore import pyqtSignal
from typing import Optional, Dict, Any, Callable
import json
import threading
import time

try:
    import websockets
    import asyncio
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

from app.desktop.workers.base_worker import BaseWorker, WorkerStatus
from app.core.logger import get_logger
from app.core.exceptions import WebSocketException


class WebSocketWorker(BaseWorker):
    """
    Worker pour la communication WebSocket temps réel.
    Gère la connexion, la réception des messages et la reconnexion automatique.
    """
    
    # Signaux
    connected = pyqtSignal()
    disconnected = pyqtSignal(str)  # error message
    message_received = pyqtSignal(dict)  # message data
    alert_received = pyqtSignal(dict)  # alert data
    camera_status_received = pyqtSignal(dict)  # camera status
    statistics_received = pyqtSignal(dict)  # statistics
    
    def __init__(self, url: str, access_token: str = None, parent=None):
        """
        Initialise le worker WebSocket.
        
        Args:
            url: URL du serveur WebSocket
            access_token: Token d'accès JWT
        """
        super().__init__(parent)
        self.url = url
        self.access_token = access_token
        self._websocket = None
        self._loop = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 10
        self._reconnect_delay = 5
    
    def set_access_token(self, token: str):
        """
        Définit le token d'accès.
        
        Args:
            token: Token JWT
        """
        self.access_token = token
        self._logger.info("Token d'accès mis à jour")
    
    def set_reconnect_settings(self, max_attempts: int, delay: int):
        """
        Configure les paramètres de reconnexion.
        
        Args:
            max_attempts: Nombre maximum de tentatives
            delay: Délai entre tentatives (secondes)
        """
        self._max_reconnect_attempts = max_attempts
        self._reconnect_delay = delay
    
    def _run_impl(self):
        """Implémentation de la connexion WebSocket."""
        if not WEBSOCKET_AVAILABLE:
            self._logger.error("websockets non installé. pip install websockets")
            self.error.emit("websockets non installé")
            return
        
        self._logger.info(f"Tentative de connexion WebSocket à {self.url}")
        
        # Créer l'event loop
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        # Exécuter la connexion
        try:
            self._loop.run_until_complete(self._connect_and_listen())
        except Exception as e:
            self._logger.error(f"Erreur WebSocket: {e}")
            self.error.emit(str(e))
        finally:
            self._loop.close()
    
    async def _connect_and_listen(self):
        """Connecte au serveur et écoute les messages."""
        ws_url = self.url
        if self.access_token:
            ws_url = f"{self.url}?token={self.access_token}"
        
        self._reconnect_attempts = 0
        
        while not self._should_stop and self._reconnect_attempts < self._max_reconnect_attempts:
            try:
                async with websockets.connect(ws_url) as websocket:
                    self._websocket = websocket
                    self._reconnect_attempts = 0
                    self.connected.emit()
                    self._logger.info("WebSocket connecté")
                    
                    # Écouter les messages
                    async for message in websocket:
                        if self._check_stop():
                            break
                        
                        try:
                            data = json.loads(message)
                            self._handle_message(data)
                        except json.JSONDecodeError as e:
                            self._logger.warning(f"Erreur décodage message: {e}")
            
            except Exception as e:
                self._logger.warning(f"Connexion WebSocket perdue: {e}")
                self.disconnected.emit(str(e))
                
                if self._should_stop:
                    break
                
                # Attendre avant de reconnecter
                self._reconnect_attempts += 1
                if self._reconnect_attempts < self._max_reconnect_attempts:
                    self._logger.info(f"Reconnexion dans {self._reconnect_delay}s (tentative {self._reconnect_attempts})")
                    await asyncio.sleep(self._reconnect_delay)
        
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            self._logger.error("Nombre maximum de tentatives de reconnexion atteint")
            self.error.emit("Impossible de reconnecter au serveur WebSocket")
    
    def _handle_message(self, data: Dict[str, Any]):
        """
        Traite un message reçu.
        
        Args:
            data: Données du message
        """
        message_type = data.get("type", "unknown")
        
        if message_type == "alert":
            self.alert_received.emit(data)
        elif message_type == "camera_status":
            self.camera_status_received.emit(data)
        elif message_type == "statistics":
            self.statistics_received.emit(data)
        else:
            self.message_received.emit(data)
    
    async def send_message(self, message: Dict[str, Any]):
        """
        Envoie un message au serveur.
        
        Args:
            message: Message à envoyer
        """
        if self._websocket is None:
            self._logger.warning("WebSocket non connecté")
            return
        
        try:
            await self._websocket.send(json.dumps(message))
        except Exception as e:
            self._logger.error(f"Erreur envoi message: {e}")
    
    def send_message_sync(self, message: Dict[str, Any]):
        """
        Envoie un message de manière synchrone (depuis le thread principal).
        
        Args:
            message: Message à envoyer
        """
        if self._loop is None or self._websocket is None:
            self._logger.warning("WebSocket non connecté")
            return
        
        try:
            asyncio.run_coroutine_threadsafe(
                self.send_message(message),
                self._loop
            )
        except Exception as e:
            self._logger.error(f"Erreur envoi message sync: {e}")
    
    def stop(self):
        """Arrête le worker et ferme la connexion WebSocket."""
        super().stop()
        if self._websocket is not None:
            try:
                asyncio.run_coroutine_threadsafe(
                    self._websocket.close(),
                    self._loop
                )
            except Exception as e:
                self._logger.error(f"Erreur fermeture WebSocket: {e}")
