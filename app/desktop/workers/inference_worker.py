"""
Worker pour l'inférence de détection.
Exécute les modèles de détection dans un thread séparé.
"""

from typing import Optional, Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QMutex, QMutexLocker, QWaitCondition
from PyQt6.QtGui import QImage
import queue
from collections import deque
from datetime import datetime
import random

from app.desktop.models.camera_model import Detection, DetectionType


class InferenceWorker(QThread):
    """Worker pour exécuter l'inférence de détection."""
    
    # Signaux
    detectionReady = pyqtSignal(str, list)  # cameraId, list of detections
    inferenceStats = pyqtSignal(str, float, int)  # cameraId, fps, frame_count
    
    def __init__(self, inference_interval: int = 100):  # ms entre inférences
        super().__init__()
        self._inference_interval = inference_interval
        self._mutex = QMutex()
        self._condition = QWaitCondition()
        
        # Buffer de frames par caméra
        self._frame_buffers: Dict[str, deque] = {}
        self._running = False
        
        # Statistiques
        self._frame_counts: Dict[str, int] = {}
        self._last_inference_times: Dict[str, datetime] = {}
        
    def add_frame(self, camera_id: str, frame: QImage):
        """Ajoute une frame pour inférence."""
        locker = QMutexLocker(self._mutex)
        if camera_id not in self._frame_buffers:
            self._frame_buffers[camera_id] = deque(maxlen=5)  # Garder 5 frames max
            self._frame_counts[camera_id] = 0
        
        self._frame_buffers[camera_id].append(frame)
        self._condition.wakeAll()
    
    def remove_camera(self, camera_id: str):
        """Retire une caméra de l'inférence."""
        locker = QMutexLocker(self._mutex)
        if camera_id in self._frame_buffers:
            del self._frame_buffers[camera_id]
        if camera_id in self._frame_counts:
            del self._frame_counts[camera_id]
        if camera_id in self._last_inference_times:
            del self._last_inference_times[camera_id]
    
    def run(self):
        """Boucle principale du worker."""
        self._running = True
        
        while self._running:
            locker = QMutexLocker(self._mutex)
            # Nettoyer les buffers vides
            to_remove = []
            for cam_id, buffer in self._frame_buffers.items():
                if not buffer:
                    to_remove.append(cam_id)
            
            for cam_id in to_remove:
                del self._frame_buffers[cam_id]
            
            # Si aucune frame à traiter, attendre
            if not self._frame_buffers:
                self._condition.wait(self._mutex)
                locker.unlock()
                continue
            locker.unlock()
            
            # Traiter les frames pour inférence
            for cam_id, buffer in list(self._frame_buffers.items()):
                if buffer:
                    # Vérifier l'intervalle d'inférence
                    now = datetime.now()
                    last_time = self._last_inference_times.get(cam_id)
                    
                    if last_time is None or (now - last_time).total_seconds() * 1000 >= self._inference_interval:
                        # Prendre la frame la plus récente
                        frame = buffer[-1]
                        
                        # Exécuter l'inférence
                        detections = self._run_inference(cam_id, frame)
                        
                        # Émettre les détections
                        self.detectionReady.emit(cam_id, detections)
                        
                        # Mettre à jour les stats
                        self._frame_counts[cam_id] = self._frame_counts.get(cam_id, 0) + 1
                        self._last_inference_times[cam_id] = now
                        
                        # Calculer un FPS approximatif
                        fps = 1000.0 / self._inference_interval
                        self.inferenceStats.emit(cam_id, fps, self._frame_counts[cam_id])
            
            self.msleep(10)  # Petite pause pour éviter 100% CPU
    
    def _run_inference(self, camera_id: str, frame: QImage) -> List[Dict[str, Any]]:
        """
        Exécute l'inférence sur une frame.
        Pour l'instant, simule des détections.
        """
        # TODO: Intégrer un vrai modèle d'inférence (YOLO, etc.)
        
        # Simulation de détections
        detections = []
        
        # Simuler aléatoirement des détections de personnes
        if random.random() > 0.7:  # 30% de chance de détection
            num_detections = random.randint(1, 3)
            
            for i in range(num_detections):
                # Coordonnées aléatoires dans la frame
                x = random.randint(50, frame.width() - 150)
                y = random.randint(50, frame.height() - 150)
                w = random.randint(50, 100)
                h = random.randint(100, 200)
                confidence = random.uniform(0.7, 0.95)
                
                detection = {
                    'type': DetectionType.PERSON.value,
                    'label': 'Person',
                    'confidence': confidence,
                    'bbox': [x, y, w, h],
                    'timestamp': datetime.now().isoformat()
                }
                detections.append(detection)
        
        return detections
    
    def stop(self):
        """Arrête le worker."""
        self._running = False
        locker = QMutexLocker(self._mutex)
        self._frame_buffers.clear()
        self._frame_counts.clear()
        self._last_inference_times.clear()
        self._condition.wakeAll()
        self.wait()
