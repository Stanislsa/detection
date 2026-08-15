"""
Service pour la gestion des caméras.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.desktop.models.camera_model import Camera, CameraStatus, Detection, DetectionType


class CameraService:
    """Service de gestion des caméras."""
    
    def __init__(self):
        self._cameras: Dict[str, Camera] = {}
        self._initialize_demo_cameras()
    
    def _initialize_demo_cameras(self) -> None:
        """Initialise des caméras de démonstration."""
        demo_cameras = [
            Camera(
                id="cam1",
                name="Camera 1",
                url="rtsp://demo1.example.com/stream",
                location="Zone A - Entrance",
                status=CameraStatus.ONLINE,
                last_activity=datetime.now()
            ),
            Camera(
                id="cam2",
                name="Camera 2",
                url="rtsp://demo2.example.com/stream",
                location="Zone B - Parking",
                status=CameraStatus.ONLINE,
                last_activity=datetime.now()
            ),
            Camera(
                id="cam3",
                name="Camera 3",
                url="rtsp://demo3.example.com/stream",
                location="Zone C - Warehouse",
                status=CameraStatus.ONLINE,
                last_activity=datetime.now()
            ),
            Camera(
                id="cam4",
                name="Camera 4",
                url="rtsp://demo4.example.com/stream",
                location="Zone D - Office",
                status=CameraStatus.OFFLINE
            ),
            Camera(
                id="cam5",
                name="Camera 5",
                url="rtsp://demo5.example.com/stream",
                location="Zone E - Loading Dock",
                status=CameraStatus.ONLINE,
                last_activity=datetime.now()
            ),
            Camera(
                id="cam6",
                name="Camera 6",
                url="rtsp://demo6.example.com/stream",
                location="Zone F - Storage",
                status=CameraStatus.ONLINE,
                last_activity=datetime.now()
            )
        ]
        
        for camera in demo_cameras:
            self._cameras[camera.id] = camera
    
    def get_all_cameras(self) -> List[Camera]:
        """Récupère toutes les caméras."""
        return list(self._cameras.values())
    
    def get_camera(self, camera_id: str) -> Optional[Camera]:
        """Récupère une caméra par ID."""
        return self._cameras.get(camera_id)
    
    def add_camera(self, name: str, url: str, location: str) -> Camera:
        """Ajoute une nouvelle caméra."""
        camera_id = f"cam{len(self._cameras) + 1}"
        camera = Camera(
            id=camera_id,
            name=name,
            url=url,
            location=location,
            status=CameraStatus.OFFLINE
        )
        self._cameras[camera_id] = camera
        return camera
    
    def update_camera(
        self,
        camera_id: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[CameraStatus] = None,
        detection_enabled: Optional[bool] = None,
        confidence_threshold: Optional[float] = None
    ) -> Optional[Camera]:
        """Met à jour une caméra."""
        camera = self._cameras.get(camera_id)
        if not camera:
            return None
        
        if name is not None:
            camera.name = name
        if url is not None:
            camera.url = url
        if location is not None:
            camera.location = location
        if status is not None:
            camera.status = status
        if detection_enabled is not None:
            camera.detection_enabled = detection_enabled
        if confidence_threshold is not None:
            camera.confidence_threshold = confidence_threshold
        
        return camera
    
    def delete_camera(self, camera_id: str) -> bool:
        """Supprime une caméra."""
        if camera_id in self._cameras:
            del self._cameras[camera_id]
            return True
        return False
    
    def add_detection(self, camera_id: str, detection: Detection) -> bool:
        """Ajoute une détection à une caméra."""
        camera = self._cameras.get(camera_id)
        if not camera:
            return False
        
        camera.add_detection(detection)
        return True
    
    def get_online_cameras(self) -> List[Camera]:
        """Récupère les caméras en ligne."""
        return [c for c in self._cameras.values() if c.status == CameraStatus.ONLINE]
    
    def get_cameras_with_alerts(self) -> List[Camera]:
        """Récupère les caméras avec des alertes récentes."""
        return [c for c in self._cameras.values() if c.has_recent_alert()]
    
    def get_camera_count(self) -> Dict[str, int]:
        """Récupère les statistiques de caméras."""
        total = len(self._cameras)
        online = len(self.get_online_cameras())
        offline = total - online
        with_alerts = len(self.get_cameras_with_alerts())
        
        return {
            "total": total,
            "online": online,
            "offline": offline,
            "with_alerts": with_alerts
        }
