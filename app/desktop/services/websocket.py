"""
Client WebSocket pour les communications temps réel.
Alertes instantanées, état des caméras, informations IA.
"""

import json
import threading
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

try:
    import websockets
    import asyncio
except ImportError:
    websockets = None
    asyncio = None


@dataclass
class WSMessage:
    """Message WebSocket."""
    type: str
    data: Dict[str, Any]
    timestamp: float


class WebSocketClient:
    """
    Client WebSocket pour les communications temps réel.
    """
    
    def __init__(self, url: str = "ws://localhost:8000/ws"):
        """
        Initialise le client WebSocket.
        
        Args:
            url: URL du serveur WebSocket
        """
        self.url = url
        self.websocket: Optional[Any] = None
        self.is_connected = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        
        # Callbacks pour les événements
        self.on_alert: Optional[Callable] = None
        self.on_camera_status: Optional[Callable] = None
        self.on_detection: Optional[Callable] = None
        self.on_statistics: Optional[Callable] = None
        self.on_connect: Optional[Callable] = None
        self.on_disconnect: Optional[Callable] = None
    
    def connect(self, access_token: str) -> bool:
        """
        Connecte au serveur WebSocket.
        
        Args:
            access_token: Token d'accès JWT
        
        Returns:
            True si connexion réussie
        """
        if websockets is None:
            print("websockets non installé. pip install websockets")
            return False
        
        self.url = f"{self.url}?token={access_token}"
        
        # Créer un event loop dans un thread séparé
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        return True
    
    def _run_loop(self):
        """Exécute l'event loop asyncio."""
        if self.loop:
            self.loop.run_until_complete(self._connect_and_listen())
    
    async def _connect_and_listen(self):
        """Connecte et écoute les messages."""
        try:
            async with websockets.connect(self.url) as websocket:
                self.websocket = websocket
                self.is_connected = True
                
                if self.on_connect:
                    self.on_connect()
                
                # Écouter les messages
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        self._handle_message(data)
                    except json.JSONDecodeError:
                        pass
        
        except Exception as e:
            self.is_connected = False
            if self.on_disconnect:
                self.on_disconnect(str(e))
    
    def _handle_message(self, data: Dict[str, Any]):
        """
        Gère un message reçu.
        
        Args:
            data: Données du message
        """
        message_type = data.get("type", "")
        message_data = data.get("data", {})
        
        if message_type == "alert" and self.on_alert:
            self.on_alert(message_data)
        elif message_type == "camera_status" and self.on_camera_status:
            self.on_camera_status(message_data)
        elif message_type == "detection" and self.on_detection:
            self.on_detection(message_data)
        elif message_type == "statistics" and self.on_statistics:
            self.on_statistics(message_data)
    
    def disconnect(self):
        """Déconnecte du serveur WebSocket."""
        self.is_connected = False
        
        if self.websocket:
            asyncio.run_coroutine_threadsafe(
                self.websocket.close(),
                self.loop
            )
        
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.thread:
            self.thread.join(timeout=1)
    
    def send(self, data: Dict[str, Any]):
        """
        Envoie un message au serveur.
        
        Args:
            data: Données à envoyer
        """
        if self.websocket and self.is_connected:
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(data)),
                self.loop
            )
