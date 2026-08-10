"""
Service de gestion des caméras.
Abstraction entre l'UI et l'API pour les opérations sur les caméras.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

from app.desktop.services.api_client import APIClient, APIResponse


@dataclass
class Camera:
    """Modèle de caméra."""
    id: int
    name: str
    source: str
    source_type: str  # 'webcam', 'rtsp', 'file'
    resolution: str = "1920x1080"
    fps: int = 30
    is_active: bool = True
    is_online: bool = False
    room: Optional[str] = None
    resolution_width: Optional[int] = 1920
    resolution_height: Optional[int] = 1080
    status: str = "offline"


class CameraService:
    """
    Service pour la gestion des caméras.
    """
    
    def __init__(self, api_client: APIClient):
        """
        Initialise le service de caméras.
        
        Args:
            api_client: Client API
        """
        self.api_client = api_client
        self._cameras_cache: Dict[int, Camera] = {}
    
    def get_cameras(self, use_cache: bool = True) -> List[Camera]:
        """
        Récupère la liste des caméras.
        
        Args:
            use_cache: Utiliser le cache si disponible
        
        Returns:
            Liste des caméras
        """
    def _parse_camera(self, cam_data: Dict) -> Camera:
        return Camera(
            id=cam_data.get("id"),
            name=cam_data.get("name", ""),
            source=cam_data.get("source", ""),
            source_type=cam_data.get("source_type", "webcam"),
            resolution=cam_data.get("resolution", f"{cam_data.get('resolution_width', 1920)}x{cam_data.get('resolution_height', 1080)}"),
            fps=cam_data.get("fps", 30),
            is_active=cam_data.get("is_active", True),
            is_online=cam_data.get("is_online", cam_data.get("status") == "online"),
            room=cam_data.get("room"),
            resolution_width=cam_data.get("resolution_width", 1920),
            resolution_height=cam_data.get("resolution_height", 1080),
            status=cam_data.get("status", "offline")
        )

    def get_cameras(self, use_cache: bool = True) -> List[Camera]:
        """
        Récupère la liste des caméras.
        
        Args:
            use_cache: Utiliser le cache si disponible
        
        Returns:
            Liste des caméras
        """
        if use_cache and self._cameras_cache:
            return list(self._cameras_cache.values())
        
        response = self.api_client.get_cameras()
        
        if response.success and response.data:
            cameras = []
            for cam_data in response.data:
                camera = self._parse_camera(cam_data)
                cameras.append(camera)
                self._cameras_cache[camera.id] = camera
            
            return cameras
        
        return []
    
    def get_camera(self, camera_id: int) -> Optional[Camera]:
        """
        Récupère une caméra spécifique.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            Caméra ou None
        """
        if camera_id in self._cameras_cache:
            return self._cameras_cache[camera_id]
        
        response = self.api_client.get_camera(camera_id)
        
        if response and getattr(response, 'success', False) is True and response.data:
            if isinstance(response.data, dict):
                camera = self._parse_camera(response.data)
                self._cameras_cache[camera.id] = camera
                return camera
        
        return None
    
    def create_camera(self, camera_data: Dict) -> Optional[Camera]:
        """
        Crée une nouvelle caméra.
        
        Args:
            camera_data: Données de la caméra
        
        Returns:
            Caméra créée ou None
        """
        response = self.api_client.create_camera(camera_data)
        
        if response.success and response.data:
            camera = self._parse_camera(response.data)
            self._cameras_cache[camera.id] = camera
            return camera
        
        return None
    
    def update_camera(self, camera_id: int, camera_data: Dict) -> Optional[Camera]:
        """
        Met à jour une caméra.
        
        Args:
            camera_id: ID de la caméra
            camera_data: Données de la caméra
        
        Returns:
            Caméra mise à jour ou None
        """
        response = self.api_client.update_camera(camera_id, camera_data)
        
        if response.success and response.data:
            camera = self._parse_camera(response.data)
            self._cameras_cache[camera.id] = camera
            return camera
        
        return None
    
    def delete_camera(self, camera_id: int) -> bool:
        """
        Supprime une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            True si succès
        """
        response = self.api_client.delete_camera(camera_id)
        
        if response.success:
            if camera_id in self._cameras_cache:
                del self._cameras_cache[camera_id]
            return True
        
        return False
    
    def invalidate_cache(self):
        """Invalide le cache des caméras."""
        self._cameras_cache.clear()
    
    def update_camera_status(self, camera_id: int, is_online: bool):
        """
        Met à jour le statut d'une caméra (via WebSocket).
        
        Args:
            camera_id: ID de la caméra
            is_online: Nouveau statut
        """
        if camera_id in self._cameras_cache:
            self._cameras_cache[camera_id].is_online = is_online
