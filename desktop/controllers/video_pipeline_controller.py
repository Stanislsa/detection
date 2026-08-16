"""
Controller pour le pipeline vidéo.
Connecte CameraWorker, VideoWorker et InferenceWorker.
Expose les signaux à QML pour l'affichage.
"""

from typing import Optional, Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot, QMutex
from PyQt6.QtGui import QImage

from desktop.workers.camera_worker import CameraWorker
from desktop.workers.video_worker import VideoWorker
from desktop.workers.inference_worker import InferenceWorker
from desktop.services.camera_service import CameraService
from desktop.controllers.video_image_provider import VideoImageProvider


class VideoPipelineController(QObject):
    """Controller principal du pipeline vidéo."""
    
    # Signaux pour QML
    frameReady = pyqtSignal(str, object)  # cameraId, QImage
    detectionsReady = pyqtSignal(str, object)  # cameraId, list of detections
    cameraStatusChanged = pyqtSignal(str, str)  # cameraId, status
    cameraError = pyqtSignal(str, str)  # cameraId, errorMessage
    
    def __init__(self, camera_service: CameraService):
        super().__init__()
        self._camera_service = camera_service
        self._mutex = QMutex()
        
        # Provider d'images
        self._image_provider = VideoImageProvider()
        
        # Initialiser les workers
        self._camera_worker = CameraWorker(camera_service)
        self._video_worker = VideoWorker(max_buffer_size=30)
        self._inference_worker = InferenceWorker(inference_interval=100)
        
        # Connecter les workers entre eux
        self._connect_workers()
        
        # Démarrer les workers
        self._camera_worker.start()
        self._video_worker.start()
        self._inference_worker.start()
        
        # État des caméras actives
        self._active_cameras: Dict[str, bool] = {}
    
    def _connect_workers(self):
        """Connecte les signaux entre les workers."""
        # CameraWorker → VideoWorker
        self._camera_worker.frameReady.connect(self._on_camera_frame)
        self._camera_worker.statusChanged.connect(self._on_camera_status)
        self._camera_worker.errorOccurred.connect(self._on_camera_error)
        
        # VideoWorker → QML
        self._video_worker.frameProcessed.connect(self._on_video_frame_processed)
        self._video_worker.bufferStatus.connect(self._on_buffer_status)
        
        # InferenceWorker → QML
        self._inference_worker.detectionReady.connect(self._on_inference_detection)
        self._inference_worker.inferenceStats.connect(self._on_inference_stats)
    
    @pyqtSlot(object)
    def _on_camera_frame(self, frame_data):
        """Frame reçue du CameraWorker."""
        camera_id, frame = frame_data
        # Envoyer au VideoWorker pour traitement
        self._video_worker.add_frame(camera_id, frame)
        # Envoyer à l'InferenceWorker pour détection
        self._inference_worker.add_frame(camera_id, frame)
    
    @pyqtSlot(str, str)
    def _on_camera_status(self, camera_id: str, status: str):
        """Statut de caméra changé."""
        self.cameraStatusChanged.emit(camera_id, status)
    
    @pyqtSlot(str, str)
    def _on_camera_error(self, camera_id: str, error: str):
        """Erreur de caméra."""
        self.cameraError.emit(camera_id, error)
    
    @pyqtSlot(str, object)
    def _on_video_frame_processed(self, camera_id: str, frame: QImage):
        """Frame traitée par VideoWorker."""
        # Stocker dans le provider pour QML
        self._image_provider.set_frame(camera_id, frame)
        # Envoyer à QML pour affichage
        self.frameReady.emit(camera_id, frame)
    
    @pyqtSlot(str, int)
    def _on_buffer_status(self, camera_id: str, buffer_size: int):
        """Statut du buffer vidéo."""
        # Peut être utilisé pour monitoring
        pass
    
    @pyqtSlot(str, list)
    def _on_inference_detection(self, camera_id: str, detections: List[Dict[str, Any]]):
        """Détections prêtes."""
        # Envoyer à QML pour affichage dans DetectionOverlay
        self.detectionsReady.emit(camera_id, detections)
    
    @pyqtSlot(str, float, int)
    def _on_inference_stats(self, camera_id: str, fps: float, frame_count: int):
        """Statistiques d'inférence."""
        # Peut être utilisé pour monitoring
        pass
    
    @pyqtSlot(str)
    def start_camera(self, camera_id: str):
        """Démarre le flux d'une caméra."""
        with self._mutex:
            camera = self._camera_service.get_camera(camera_id)
            if camera:
                self._camera_worker.add_camera(camera)
                self._camera_worker.start_camera(camera_id)
                self._active_cameras[camera_id] = True
    
    @pyqtSlot(str)
    def stop_camera(self, camera_id: str):
        """Arrête le flux d'une caméra."""
        with self._mutex:
            self._camera_worker.stop_camera(camera_id)
            self._video_worker.remove_camera(camera_id)
            self._inference_worker.remove_camera(camera_id)
            self._image_provider.clear_camera(camera_id)
            if camera_id in self._active_cameras:
                del self._active_cameras[camera_id]
    
    @pyqtSlot()
    def stop_all(self):
        """Arrête toutes les caméras."""
        with self._mutex:
            for camera_id in list(self._active_cameras.keys()):
                self.stop_camera(camera_id)
    
    def cleanup(self):
        """Nettoie les ressources."""
        self.stop_all()
        self._camera_worker.stop()
        self._video_worker.stop()
        self._inference_worker.stop()
    
    @property
    def image_provider(self):
        """Retourne le provider d'images."""
        return self._image_provider