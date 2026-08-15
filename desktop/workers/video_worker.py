"""
Worker pour le traitement vidéo.
Gère le buffering et le prétraitement des frames vidéo.
"""

from typing import Optional, Dict, Any, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QMutex, QMutexLocker, QWaitCondition
from PyQt6.QtGui import QImage
import queue
import threading
from collections import deque


class VideoWorker(QThread):
    """Worker pour traiter les frames vidéo."""
    
    # Signaux
    frameProcessed = pyqtSignal(str, object)  # cameraId, processed_frame
    bufferStatus = pyqtSignal(str, int)  # cameraId, buffer_size
    
    def __init__(self, max_buffer_size: int = 30):
        super().__init__()
        self._max_buffer_size = max_buffer_size
        self._mutex = QMutex()
        self._condition = QWaitCondition()
        
        # Buffer par caméra
        self._buffers: Dict[str, deque] = {}
        self._running = False
        
    def add_frame(self, camera_id: str, frame: QImage):
        """Ajoute une frame au buffer d'une caméra."""
        with self._mutex:
            if camera_id not in self._buffers:
                self._buffers[camera_id] = deque(maxlen=self._max_buffer_size)
            
            buffer = self._buffers[camera_id]
            buffer.append(frame)
            
            # Notifier le statut du buffer
            self.bufferStatus.emit(camera_id, len(buffer))
            
            self._condition.wakeAll()
    
    def remove_camera(self, camera_id: str):
        """Retire une caméra du traitement."""
        with self._mutex:
            if camera_id in self._buffers:
                del self._buffers[camera_id]
    
    def get_latest_frame(self, camera_id: str) -> Optional[QImage]:
        """Récupère la frame la plus récente d'une caméra."""
        with self._mutex:
            if camera_id in self._buffers and self._buffers[camera_id]:
                return self._buffers[camera_id][-1]
        return None
    
    def run(self):
        """Boucle principale du worker."""
        self._running = True
        
        while self._running:
            locker = QMutexLocker(self._mutex)
            # Nettoyer les buffers vides
            to_remove = []
            for cam_id, buffer in self._buffers.items():
                if not buffer:
                    to_remove.append(cam_id)
            
            for cam_id in to_remove:
                del self._buffers[cam_id]
            
            # Si aucune frame à traiter, attendre
            if not self._buffers:
                self._condition.wait(self._mutex)
                locker.unlock()
                continue
            locker.unlock()
            
            # Traiter les frames
            for cam_id, buffer in list(self._buffers.items()):
                if buffer:
                    # Prendre la frame la plus récente
                    frame = buffer[-1]
                    
                    # Prétraitement (redimensionnement, conversion, etc.)
                    processed_frame = self._preprocess_frame(frame)
                    
                    # Émettre la frame traitée
                    self.frameProcessed.emit(cam_id, processed_frame)
            
            self.msleep(33)  # ~30 FPS
    
    def _preprocess_frame(self, frame: QImage) -> QImage:
        """Prétraite une frame pour l'affichage ou l'inférence."""
        # Copier la frame pour éviter les problèmes de concurrence
        processed = frame.copy()
        
        # Redimensionner si nécessaire (optionnel)
        # if processed.width() > 1920 or processed.height() > 1080:
        #     processed = processed.scaled(1920, 1080, Qt.AspectRatioMode.KeepAspectRatio)
        
        return processed
    
    def stop(self):
        """Arrête le worker."""
        self._running = False
        locker = QMutexLocker(self._mutex)
        self._buffers.clear()
        self._condition.wakeAll()
        self.wait()
