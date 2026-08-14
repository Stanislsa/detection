"""
Contrôleur pour la gestion des caméras (pont avec QML).
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot

from app.desktop.models.camera_model import Camera, CameraStatus, Detection, DetectionType
from app.desktop.services.camera_service import CameraService


class CameraController(QObject):
    """Contrôleur pour les caméras exposé à QML."""
    
    camerasChanged = pyqtSignal()
    cameraAdded = pyqtSignal(str)
    cameraUpdated = pyqtSignal(str)
    cameraDeleted = pyqtSignal(str)
    detectionAdded = pyqtSignal(str)
    
    def __init__(self, service: CameraService):
        super().__init__()
        self._service = service
    
    @pyqtProperty(list, notify=camerasChanged)
    def cameras(self) -> List[Dict[str, Any]]:
        """Liste des caméras."""
        return [camera.to_dict() for camera in self._service.get_all_cameras()]
    
    @pyqtProperty(int, notify=camerasChanged)
    def cameraCount(self) -> int:
        """Nombre total de caméras."""
        return len(self._service.get_all_cameras())
    
    @pyqtProperty(int, notify=camerasChanged)
    def onlineCount(self) -> int:
        """Nombre de caméras en ligne."""
        return len(self._service.get_online_cameras())
    
    @pyqtProperty(int, notify=camerasChanged)
    def alertCount(self) -> int:
        """Nombre de caméras avec alertes."""
        return len(self._service.get_cameras_with_alerts())
    
    @pyqtSlot(str, result=dict)
    def getCamera(self, camera_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une caméra par ID."""
        camera = self._service.get_camera(camera_id)
        return camera.to_dict() if camera else None
    
    @pyqtSlot(str, str, str, result=str)
    def addCamera(self, name: str, url: str, location: str) -> str:
        """Ajoute une nouvelle caméra."""
        camera = self._service.add_camera(name, url, location)
        self.camerasChanged.emit()
        self.cameraAdded.emit(camera.id)
        return camera.id
    
    @pyqtSlot(str, str, str, str, result=bool)
    def updateCamera(self, camera_id: str, name: str, url: str, location: str) -> bool:
        """Met à jour une caméra."""
        camera = self._service.update_camera(
            camera_id=camera_id,
            name=name,
            url=url,
            location=location
        )
        if camera:
            self.camerasChanged.emit()
            self.cameraUpdated.emit(camera_id)
            return True
        return False
    
    @pyqtSlot(str, result=bool)
    def deleteCamera(self, camera_id: str) -> bool:
        """Supprime une caméra."""
        success = self._service.delete_camera(camera_id)
        if success:
            self.camerasChanged.emit()
            self.cameraDeleted.emit(camera_id)
        return success
    
    @pyqtSlot(str, str, float, float, float, float, result=bool)
    def addDetection(
        self,
        camera_id: str,
        label: str,
        confidence: float,
        x: float,
        y: float,
        width: float,
        height: float
    ) -> bool:
        """Ajoute une détection à une caméra."""
        detection = Detection(
            id=str(uuid.uuid4()),
            type=DetectionType.PERSON,
            label=label,
            confidence=confidence,
            bbox={"x": x, "y": y, "width": width, "height": height},
            timestamp=datetime.now()
        )
        success = self._service.add_detection(camera_id, detection)
        if success:
            self.detectionAdded.emit(camera_id)
        return success
    
    @pyqtSlot(result=dict)
    def getCameraStats(self) -> Dict[str, int]:
        """Récupère les statistiques de caméras."""
        return self._service.get_camera_count()
    
    def refresh(self) -> None:
        """Rafraîchit les données des caméras."""
        self.camerasChanged.emit()
