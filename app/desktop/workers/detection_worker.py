"""
Worker pour la détection IA sur les frames vidéo.
Utilise QThread pour ne pas bloquer l'interface lors de l'inférence.
"""

from PyQt6.QtCore import pyqtSignal
from typing import Optional, List, Tuple, Dict, Any
import numpy as np
import cv2

from app.desktop.workers.base_worker import BaseWorker, WorkerStatus
from app.core.logger import get_logger


class DetectionResult:
    """Résultat de détection."""
    
    def __init__(
        self,
        class_id: int,
        class_name: str,
        confidence: float,
        bbox: Tuple[int, int, int, int],  # x, y, width, height
        additional_data: Dict[str, Any] = None
    ):
        self.class_id = class_id
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox
        self.additional_data = additional_data or {}


class DetectionWorker(BaseWorker):
    """
    Worker pour la détection IA sur les frames vidéo.
    Peut utiliser différents détecteurs (YOLO, MediaPipe, etc.).
    """
    
    # Signaux
    detection_ready = pyqtSignal(object, list)  # frame, List[DetectionResult]
    fps_changed = pyqtSignal(float)
    
    def __init__(self, detector=None, confidence_threshold: float = 0.5, parent=None):
        """
        Initialise le worker de détection.
        
        Args:
            detector: Instance du détecteur IA (YOLO, MediaPipe, etc.)
            confidence_threshold: Seuil de confiance
        """
        super().__init__(parent)
        self._detector = detector
        self._confidence_threshold = confidence_threshold
        self._fps = 0.0
        self._frame_count = 0
        self._start_time = 0
    
    def set_detector(self, detector):
        """
        Définit le détecteur IA.
        
        Args:
            detector: Instance du détecteur
        """
        self._detector = detector
        self._logger.info(f"Détecteur changé: {detector.__class__.__name__}")
    
    def set_confidence_threshold(self, threshold: float):
        """
        Définit le seuil de confiance.
        
        Args:
            threshold: Seuil de confiance (0.0 - 1.0)
        """
        self._confidence_threshold = max(0.0, min(1.0, threshold))
        self._logger.info(f"Seuil de confiance changé: {self._confidence_threshold}")
    
    def _run_impl(self):
        """Implémentation de la détection (boucle de traitement des frames)."""
        self._logger.info("Worker de détection démarré")
        self._start_time = cv2.getTickCount()
        
        # Ce worker traite les frames qui lui sont passées via une queue
        # Pour l'instant, c'est un template - l'implémentation réelle dépendra
        # de la façon dont les frames sont passées
        
        while not self._check_stop():
            if self._check_pause():
                continue
            
            # Attendre un frame à traiter
            self.msleep(10)
        
        self._logger.info("Worker de détection arrêté")
    
    def process_frame(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Traite un frame avec le détecteur IA.
        
        Args:
            frame: Frame à traiter
        
        Returns:
            Liste des résultats de détection
        """
        if self._detector is None:
            self._logger.warning("Aucun détecteur configuré")
            return []
        
        try:
            # Appeler le détecteur
            results = self._detector.detect(frame, self._confidence_threshold)
            
            # Calcul FPS
            self._frame_count += 1
            if self._frame_count % 30 == 0:
                current_time = cv2.getTickCount()
                elapsed = (current_time - self._start_time) / cv2.getTickFrequency()
                self._fps = self._frame_count / elapsed if elapsed > 0 else 0
                self.fps_changed.emit(self._fps)
            
            return results
            
        except Exception as e:
            self._logger.error(f"Erreur lors de la détection: {e}")
            return []
    
    def get_fps(self) -> float:
        """Retourne les FPS de détection actuels."""
        return self._fps


class FallDetectionWorker(DetectionWorker):
    """
    Worker spécialisé pour la détection de chutes.
    """
    
    # Signaux
    fall_detected = pyqtSignal(object, float)  # frame, confidence
    
    def __init__(self, detector=None, fall_confidence_threshold: float = 0.7, parent=None):
        """
        Initialise le worker de détection de chutes.
        
        Args:
            detector: Détecteur de chutes (MediaPipe, etc.)
            fall_confidence_threshold: Seuil de confiance pour les chutes
        """
        super().__init__(detector, fall_confidence_threshold, parent)
        self._fall_confidence_threshold = fall_confidence_threshold
    
    def process_frame(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Traite un frame pour détecter les chutes.
        
        Args:
            frame: Frame à traiter
        
        Returns:
            Liste des résultats de détection
        """
        results = super().process_frame(frame)
        
        # Vérifier si une chute est détectée
        for result in results:
            if result.class_name == "fall" and result.confidence >= self._fall_confidence_threshold:
                self.fall_detected.emit(frame, result.confidence)
                self._logger.warning(f"Chute détectée avec confiance {result.confidence:.2f}")
        
        return results


class IntrusionDetectionWorker(DetectionWorker):
    """
    Worker spécialisé pour la détection d'intrusions.
    """
    
    # Signaux
    intrusion_detected = pyqtSignal(object, float)  # frame, confidence
    
    def __init__(self, detector=None, intrusion_confidence_threshold: float = 0.6, parent=None):
        """
        Initialise le worker de détection d'intrusions.
        
        Args:
            detector: Détecteur d'intrusions (YOLO, etc.)
            intrusion_confidence_threshold: Seuil de confiance pour les intrusions
        """
        super().__init__(detector, intrusion_confidence_threshold, parent)
        self._intrusion_confidence_threshold = intrusion_confidence_threshold
    
    def process_frame(self, frame: np.ndarray) -> List[DetectionResult]:
        """
        Traite un frame pour détecter les intrusions.
        
        Args:
            frame: Frame à traiter
        
        Returns:
            Liste des résultats de détection
        """
        results = super().process_frame(frame)
        
        # Vérifier si une intrusion est détectée
        for result in results:
            if result.class_name == "person" and result.confidence >= self._intrusion_confidence_threshold:
                # Vérifier si la personne est dans une zone interdite
                if self._is_in_restricted_zone(result.bbox):
                    self.intrusion_detected.emit(frame, result.confidence)
                    self._logger.warning(f"Intrusion détectée avec confiance {result.confidence:.2f}")
        
        return results
    
    def _is_in_restricted_zone(self, bbox: Tuple[int, int, int, int]) -> bool:
        """
        Vérifie si la bounding box est dans une zone interdite.
        
        Args:
            bbox: Bounding box (x, y, width, height)
        
        Returns:
            True si dans une zone interdite
        """
        # Implémentation à personnaliser selon les zones définies
        # Pour l'instant, retourne False
        return False
