"""
Worker pour la capture vidéo des caméras.
Utilise QThread pour ne pas bloquer l'interface lors de la capture.
"""

from PyQt6.QtCore import pyqtSignal
from typing import Optional, Tuple
import cv2
import numpy as np

from app.desktop.workers.base_worker import BaseWorker, WorkerStatus
from app.core.logger import get_logger


class CameraWorker(BaseWorker):
    """
    Worker pour la capture vidéo depuis une source (webcam, RTSP, fichier).
    """
    
    # Signaux
    frame_ready = pyqtSignal(np.ndarray)  # Nouveau frame disponible
    camera_connected = pyqtSignal(str)  # camera_id
    camera_disconnected = pyqtSignal(str)  # camera_id
    fps_changed = pyqtSignal(float)  # FPS actuels
    
    def __init__(self, camera_id: str, source: str, source_type: str = "webcam", parent=None):
        """
        Initialise le worker de caméra.
        
        Args:
            camera_id: ID de la caméra
            source: Source vidéo (webcam index, RTSP URL, fichier)
            source_type: Type de source (webcam, rtsp, file)
        """
        super().__init__(parent)
        self.camera_id = camera_id
        self.source = source
        self.source_type = source_type
        self._cap: Optional[cv2.VideoCapture] = None
        self._fps = 0.0
        self._frame_count = 0
        self._start_time = 0
    
    def _run_impl(self):
        """Implémentation de la capture vidéo."""
        self._logger.info(f"Démarrage capture caméra {self.camera_id} depuis {self.source}")
        
        # Ouverture de la source
        if not self._open_camera():
            self.error.emit(f"Impossible d'ouvrir la caméra {self.camera_id}")
            return
        
        self.camera_connected.emit(self.camera_id)
        self._start_time = cv2.getTickCount()
        
        # Boucle de capture
        while not self._check_stop():
            if self._check_pause():
                continue
            
            # Lecture du frame
            ret, frame = self._cap.read()
            
            if not ret:
                self._logger.warning(f"Erreur lecture frame caméra {self.camera_id}")
                # Tentative de reconnexion
                if self._should_reconnect():
                    continue
                else:
                    break
            
            # Calcul FPS
            self._frame_count += 1
            if self._frame_count % 30 == 0:
                current_time = cv2.getTickCount()
                elapsed = (current_time - self._start_time) / cv2.getTickFrequency()
                self._fps = self._frame_count / elapsed if elapsed > 0 else 0
                self.fps_changed.emit(self._fps)
            
            # Émission du frame
            self.frame_ready.emit(frame)
            
            # Petit délai pour éviter de surcharger le CPU
            self.msleep(1)
        
        # Nettoyage
        self._close_camera()
        self.camera_disconnected.emit(self.camera_id)
        self._logger.info(f"Arrêt capture caméra {self.camera_id}")
    
    def _open_camera(self) -> bool:
        """
        Ouvre la source vidéo.
        
        Returns:
            True si succès
        """
        try:
            if self.source_type == "webcam":
                # Webcam: convertir en entier
                index = int(self.source) if self.source.isdigit() else 0
                self._cap = cv2.VideoCapture(index)
            elif self.source_type == "rtsp":
                # RTSP: utiliser URL avec options
                self._cap = cv2.VideoCapture(self.source, cv2.CAP_FFMPEG)
                self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Réduire buffer
            elif self.source_type == "file":
                # Fichier vidéo
                self._cap = cv2.VideoCapture(self.source)
            else:
                self._logger.error(f"Type de source inconnu: {self.source_type}")
                return False
            
            # Vérifier l'ouverture
            if not self._cap.isOpened():
                self._logger.error(f"Impossible d'ouvrir la source: {self.source}")
                return False
            
            # Configuration
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self._cap.set(cv2.CAP_PROP_FPS, 30)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Erreur ouverture caméra: {e}")
            return False
    
    def _close_camera(self):
        """Ferme la source vidéo."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
    
    def _should_reconnect(self) -> bool:
        """
        Vérifie si une reconnexion est nécessaire.
        
        Returns:
            True si reconnexion tentée avec succès
        """
        self._logger.info("Tentative de reconnexion...")
        self._close_camera()
        self.msleep(1000)  # Attendre 1 seconde
        
        if self._open_camera():
            self._logger.info("Reconnexion réussie")
            return True
        
        return False
    
    def get_resolution(self) -> Tuple[int, int]:
        """
        Retourne la résolution actuelle.
        
        Returns:
            (width, height)
        """
        if self._cap is not None:
            width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)
        return (0, 0)
    
    def get_fps(self) -> float:
        """Retourne les FPS actuels."""
        return self._fps
    
    def stop(self):
        """Arrête le worker et ferme la caméra."""
        super().stop()
        self._close_camera()
