"""
Service multi-caméra pour la détection de chutes en temps réel.

Gestion de plusieurs flux RTSP/webcam avec threading et optimisation CPU.
Intégration YOLO + MediaPipe pour ThinkPad i5 (8 Go RAM, pas de GPU).

Architecture:
- Thread par caméra pour capture
- Buffer circulaire par caméra
- Orchestrateur central pour traitement
- Optimisation frame skipping
"""

import cv2
import threading
import queue
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import numpy as np

from app.core.yolo_detector import YOLODetector, YOLOResult
from app.core.pose_processor import PoseEstimator
from app.core.fall_detector import FallDetector, FallDetectionResult
from app.config import settings


@dataclass
class CameraStream:
    """Flux de caméra avec buffer circulaire."""
    camera_id: str
    source: str  # RTSP URL ou webcam index
    capture: cv2.VideoCapture = field(init=False)
    frame_queue: queue.Queue = field(default_factory=lambda: queue.Queue(maxsize=30))
    is_running: bool = False
    thread: Optional[threading.Thread] = None
    fps: float = 0.0
    frame_count: int = 0
    last_frame_time: float = 0.0


@dataclass
class DetectionResult:
    """Résultat de détection pour une caméra."""
    camera_id: str
    yolo_result: Optional[YOLOResult] = None
    fall_result: Optional[FallDetectionResult] = None
    timestamp: float = field(default_factory=time.time)
    processing_time_ms: float = 0.0


-class MultiCameraService:
    """
    Service multi-caméra pour détection de chutes.
    
    Optimisé pour ThinkPad i5 :
    - Frame skipping (1 sur N)
    - Résolution réduite (640x480)
    - Threading pour parallélisation
    - Buffer circulaire pour économie RAM
    """
    
    def __init__(
        self,
        camera_sources: Dict[str, str],  # {camera_id: source}
        use_yolo: bool = True,
        use_openvino: bool = True,
        frame_skip: int = 3,
        target_resolution: tuple = (640, 480),
        enable_fall_detection: bool = True
    ):
        """
        Initialise le service multi-caméra.
        
        Args:
            camera_sources: Dictionnaire {camera_id: source}
            use_yolo: Utiliser YOLO pour pré-filtrage
            use_openvino: Utiliser OpenVINO pour optimisation CPU
            frame_skip: Sauter N frames (économise RAM/CPU)
            target_resolution: Résolution cible (width, height)
            enable_fall_detection: Activer détection de chutes
        """
        self.camera_sources = camera_sources
        self.use_yolo = use_yolo
        self.use_openvino = use_openvino
        self.frame_skip = frame_skip
        self.target_resolution = target_resolution
        self.enable_fall_detection = enable_fall_detection
        
        # Flux de caméras
        self.camera_streams: Dict[str, CameraStream] = {}
        
        # Détecteurs
        self.yolo_detector: Optional[YOLODetector] = None
        self.pose_estimators: Dict[str, PoseEstimator] = {}
        self.fall_detectors: Dict[str, FallDetector] = {}
        
        # Callbacks
        self.on_detection: Optional[Callable[[DetectionResult], None]] = None
        self.on_fall: Optional[Callable[[str, FallDetectionResult], None]] = None
        
        # Statistiques
        self.total_frames_processed = 0
        self.start_time = time.time()
    
    def initialize(self):
        """Initialise les caméras et détecteurs."""
        print(f"Initialisation de {len(self.camera_sources)} caméras...")
        
        # Initialiser YOLO si activé
        if self.use_yolo:
            print("Chargement YOLO11...")
            self.yolo_detector = YOLODetector(
                model_name="yolo11n.pt",
                use_openvino=self.use_openvino,
                frame_skip=self.frame_skip
            )
        
        # Initialiser les flux de caméras
        for camera_id, source in self.camera_sources.items():
            print(f"Ouverture caméra {camera_id}: {source}")
            
            # Créer le flux
            stream = CameraStream(camera_id=camera_id, source=source)
            
            # Ouvrir la capture
            stream.capture = cv2.VideoCapture(source)
            
            if not stream.capture.isOpened():
                print(f"Erreur: Impossible d'ouvrir {source}")
                continue
            
            # Configurer la résolution
            stream.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_resolution[0])
            stream.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_resolution[1])
            
            # Initialiser pose estimator
            self.pose_estimators[camera_id] = PoseEstimator(
                model_complexity=0,  # Lite pour performance
                use_yolo_roi=self.use_yolo
            )
            
            # Initialiser fall detector
            if self.enable_fall_detection:
                self.fall_detectors[camera_id] = FallDetector(
                    profile_type="senior_autonome",
                    frame_rate=30
                )
            
            self.camera_streams[camera_id] = stream
        
        print(f"{len(self.camera_streams)} caméras initialisées")
    
    def start(self):
        """Démarre tous les flux de caméras."""
        print("Démarrage des flux...")
        
        for camera_id, stream in self.camera_streams.items():
            stream.is_running = True
            stream.thread = threading.Thread(
                target=self._capture_thread,
                args=(camera_id,),
                daemon=True
            )
            stream.thread.start()
        
        print("Flux démarrés")
    
    def stop(self):
        """Arrête tous les flux de caméras."""
        print("Arrêt des flux...")
        
        for stream in self.camera_streams.values():
            stream.is_running = False
            if stream.thread:
                stream.thread.join(timeout=1.0)
            if stream.capture.isOpened():
                stream.capture.release()
        
        # Fermer les détecteurs
        if self.yolo_detector:
            self.yolo_detector.close()
        
        for estimator in self.pose_estimators.values():
            estimator.close()
        
        print("Flux arrêtés")
    
    def _capture_thread(self, camera_id: str):
        """
        Thread de capture pour une caméra.
        
        Args:
            camera_id: ID de la caméra
        """
        stream = self.camera_streams[camera_id]
        frame_count = 0
        
        while stream.is_running:
            ret, frame = stream.capture.read()
            
            if not ret:
                print(f"Erreur lecture caméra {camera_id}")
                time.sleep(0.1)
                continue
            
            # Frame skipping
            frame_count += 1
            if frame_count % self.frame_skip != 0:
                continue
            
            # Mettre dans la queue
            try:
                stream.frame_queue.put_nowait(frame)
            except queue.Full:
                # Queue pleine, ignorer frame
                pass
            
            # Calcul FPS
            current_time = time.time()
            if current_time - stream.last_frame_time >= 1.0:
                stream.fps = frame_count / (current_time - stream.last_frame_time)
                stream.last_frame_time = current_time
                frame_count = 0
    
    def process_all(self) -> Dict[str, DetectionResult]:
        """
        Traite toutes les caméras.
        
        Returns:
            Dictionnaire {camera_id: DetectionResult}
        """
        results = {}
        
        for camera_id, stream in self.camera_streams.items():
            # Récupérer frame depuis queue
            try:
                frame = stream.frame_queue.get_nowait()
            except queue.Empty:
                continue
            
            # Traitement
            result = self._process_frame(camera_id, frame)
            results[camera_id] = result
            
            # Callbacks
            if self.on_detection:
                self.on_detection(result)
            
            if self.on_fall and result.fall_result and result.fall_result.status.value == "confirmed":
                self.on_fall(camera_id, result.fall_result)
        
        self.total_frames_processed += len(results)
        return results
    
    def _process_frame(self, camera_id: str, frame: np.ndarray) -> DetectionResult:
        """
        Traite une frame d'une caméra.
        
        Args:
            camera_id: ID de la caméra
            frame: Image OpenCV
        
        Returns:
            DetectionResult
        """
        start_time = time.time()
        
        # Étape 1: YOLO (si activé)
        yolo_result = None
        roi = None
        
        if self.use_yolo and self.yolo_detector:
            yolo_result = self.yolo_detector.process_frame(frame)
            if yolo_result:
                roi = self.yolo_detector.get_primary_person_roi(frame)
        
        # Étape 2: MediaPipe Pose
        pose_estimator = self.pose_estimators[camera_id]
        
        if roi:
            pose_estimator.set_roi(roi)
        else:
            pose_estimator.clear_roi()
        
        pose_landmarks = pose_estimator.process_frame(frame)
        
        # Étape 3: Fall Detection
        fall_result = None
        if self.enable_fall_detection and pose_landmarks:
            fall_detector = self.fall_detectors[camera_id]
            
            # Convertir PoseLandmarks en PoseData
            from app.core.physics_engine import PoseData
            pose_data = PoseData(
                x=np.array([lm.x for lm in pose_landmarks.landmarks]),
                y=np.array([lm.y for lm in pose_landmarks.landmarks]),
                z=np.array([lm.z for lm in pose_landmarks.landmarks]),
                visibility=np.array([lm.visibility for lm in pose_landmarks.landmarks]),
                timestamp=pose_landmarks.timestamp
            )
            
            fall_result = fall_detector.process(pose_data)
        
        processing_time = (time.time() - start_time) * 1000
        
        return DetectionResult(
            camera_id=camera_id,
            yolo_result=yolo_result,
            fall_result=fall_result,
            timestamp=time.time(),
            processing_time_ms=processing_time
        )
    
    def get_statistics(self) -> Dict:
        """
        Retourne les statistiques du service.
        
        Returns:
            Dictionnaire de statistiques
        """
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "total_cameras": len(self.camera_streams),
            "active_cameras": len([s for s in self.camera_streams.values() if s.is_running]),
            "total_frames_processed": self.total_frames_processed,
            "average_fps": self.total_frames_processed / uptime if uptime > 0 else 0,
            "camera_fps": {
                camera_id: stream.fps
                for camera_id, stream in self.camera_streams.items()
            }
        }
    
    def set_detection_callback(self, callback: Callable[[DetectionResult], None]):
        """
        Définit le callback pour chaque détection.
        
        Args:
            callback: Fonction appelée avec DetectionResult
        """
        self.on_detection = callback
    
    def set_fall_callback(self, callback: Callable[[str, FallDetectionResult], None]):
        """
        Définit le callback pour les chutes détectées.
        
        Args:
            callback: Fonction appelée avec camera_id et FallDetectionResult
        """
        self.on_fall = callback


# Fonction utilitaire pour créer un fichier cameras.txt
def create_cameras_file(camera_sources: Dict[str, str], filename: str = "cameras.txt"):
    """
    Crée un fichier cameras.txt pour YOLO multi-caméra.
    
    Args:
        camera_sources: Dictionnaire {camera_id: source}
        filename: Nom du fichier de sortie
    """
    with open(filename, 'w') as f:
        for source in camera_sources.values():
            f.write(f"{source}\n")
    
    print(f"Fichier {filename} créé")
