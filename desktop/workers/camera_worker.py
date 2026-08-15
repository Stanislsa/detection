"""
Worker pour la gestion des caméras.
Exécute les opérations de caméra dans un thread séparé pour ne pas bloquer l'UI.
"""

from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QMutex, QMutexLocker, QWaitCondition
from PyQt6.QtGui import QImage
import time
import random

from app.desktop.models.camera_model import Camera, CameraStatus
from app.desktop.services.camera_service import CameraService


class CameraWorker(QThread):
    """Worker pour gérer les flux vidéo des caméras."""
    
    # Signaux
    frameReady = pyqtSignal(object)  # QImage
    statusChanged = pyqtSignal(str, str)  # cameraId, status
    errorOccurred = pyqtSignal(str, str)  # cameraId, errorMessage
    
    def __init__(self, camera_service: CameraService):
        super().__init__()
        self._camera_service = camera_service
        self._mutex = QMutex()
        self._condition = QWaitCondition()
        
        self._active_cameras: Dict[str, Dict[str, Any]] = {}
        self._running = False
        
    def add_camera(self, camera: Camera):
        """Ajoute une caméra à surveiller."""
        locker = QMutexLocker(self._mutex)
        if camera.id not in self._active_cameras:
            self._active_cameras[camera.id] = {
                'camera': camera,
                'active': True
            }
            self._condition.wakeAll()
    
    def remove_camera(self, camera_id: str):
        """Retire une caméra de la surveillance."""
        locker = QMutexLocker(self._mutex)
        if camera_id in self._active_cameras:
            self._active_cameras[camera_id]['active'] = False
            del self._active_cameras[camera_id]
    
    def start_camera(self, camera_id: str):
        """Démarre le flux d'une caméra."""
        locker = QMutexLocker(self._mutex)
        if camera_id in self._active_cameras:
            self._active_cameras[camera_id]['active'] = True
            self._condition.wakeAll()
    
    def stop_camera(self, camera_id: str):
        """Arrête le flux d'une caméra."""
        locker = QMutexLocker(self._mutex)
        if camera_id in self._active_cameras:
            self._active_cameras[camera_id]['active'] = False
    
    def run(self):
        """Boucle principale du worker."""
        self._running = True
        
        while self._running:
            locker = QMutexLocker(self._mutex)
            # Nettoyer les caméras inactives
            to_remove = []
            for cam_id, cam_data in self._active_cameras.items():
                if not cam_data['active']:
                    to_remove.append(cam_id)
            
            for cam_id in to_remove:
                del self._active_cameras[cam_id]
            
            # Si aucune caméra active, attendre
            if not self._active_cameras:
                self._condition.wait(self._mutex)
                locker.unlock()
                continue
            locker.unlock()
            
            # Traiter les caméras actives
            for cam_id, cam_data in list(self._active_cameras.items()):
                if not cam_data['active']:
                    continue
                
                camera = cam_data['camera']
                
                # Simuler des frames vidéo (remplacer par vrai flux quand prêt)
                frame = self._generate_simulated_frame(camera)
                if frame:
                    self.frameReady.emit((cam_id, frame))
                    self.statusChanged.emit(cam_id, CameraStatus.ONLINE.value)
            
            self.msleep(33)  # ~30 FPS
    
    def _generate_simulated_frame(self, camera: Camera) -> Optional[QImage]:
        """Génère une frame simulée pour le test."""
        # Créer une image de test
        width, height = 640, 480
        image = QImage(width, height, QImage.Format.Format_RGB32)
        
        # Remplir avec une couleur de base
        color = random.randint(50, 100)
        image.fill(color, color, color + 50)
        
        # Ajouter du bruit pour simuler du mouvement
        import random
        for _ in range(100):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            c = random.randint(150, 200)
            image.setPixelColor(x, y, c)
        
        return image
    
    def stop(self):
        """Arrête le worker."""
        self._running = False
        locker = QMutexLocker(self._mutex)
        self._active_cameras.clear()
        self._condition.wakeAll()
        self.wait()
