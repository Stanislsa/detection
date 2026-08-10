"""
Détecteur MediaPipe pour la pose et le suivi.
Spécialisé pour la détection de chutes via l'analyse de pose.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

from app.ai.base_detector import BaseDetector
from app.desktop.workers.detection_worker import DetectionResult
from app.core.logger import get_logger
from app.core.exceptions import DetectionException


class MediaPipePoseDetector(BaseDetector):
    """
    Détecteur de pose utilisant MediaPipe Pose.
    Extrait les landmarks du corps humain pour l'analyse.
    """
    
    def __init__(
        self,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        static_image_mode: bool = False
    ):
        """
        Initialise le détecteur de pose MediaPipe.
        
        Args:
            model_complexité: Complexité du modèle (0, 1, 2)
            min_detection_confidence: Seuil de confiance pour la détection
            min_tracking_confidence: Seuil de confiance pour le tracking
            static_image_mode: Mode image statique
        """
        super().__init__(confidence_threshold=min_detection_confidence)
        self.model_complexity = model_complexity
        self.min_tracking_confidence = min_tracking_confidence
        self.static_image_mode = static_image_mode
        self._mp_pose = None
        self._pose = None
    
    def load_model(self) -> bool:
        """
        Charge le modèle MediaPipe Pose.
        
        Returns:
            True si succès
        """
        if not MEDIAPIPE_AVAILABLE:
            self._logger.error("MediaPipe non installé. pip install mediapipe")
            raise DetectionException("MediaPipe non installé")
        
        try:
            self._logger.info("Chargement du modèle MediaPipe Pose")
            self._mp_pose = mp.solutions.pose
            self._pose = self._mp_pose.Pose(
                static_image_mode=self.static_image_mode,
                model_complexity=self.model_complexity,
                min_detection_confidence=self.confidence_threshold,
                min_tracking_confidence=self.min_tracking_confidence
            )
            self._is_loaded = True
            self._logger.info("Modèle MediaPipe Pose chargé avec succès")
            return True
            
        except Exception as e:
            self._logger.error(f"Erreur chargement modèle MediaPipe: {e}")
            raise DetectionException(f"Erreur chargement modèle: {e}")
    
    def detect(self, frame: np.ndarray, confidence_threshold: Optional[float] = None) -> List[DetectionResult]:
        """
        Effectue la détection de pose.
        
        Args:
            frame: Frame à analyser
            confidence_threshold: Seuil de confiance
        
        Returns:
            Liste des résultats (landmarks)
        """
        if not self._is_loaded:
            self._logger.warning("Modèle non chargé, tentative de chargement...")
            self.load_model()
        
        try:
            # Convertir en RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if frame.shape[2] == 3 else frame
            
            # Inférence
            results = self._pose.process(frame_rgb)
            
            # Post-traitement
            detections = []
            if results.pose_landmarks:
                detection = DetectionResult(
                    class_id=0,
                    class_name="pose",
                    confidence=results.pose_landmarks.visibility[0].mean() if results.pose_landmarks.visibility else 0.0,
                    bbox=(0, 0, frame.shape[1], frame.shape[0]),
                    additional_data={
                        "landmarks": self._extract_landmarks(results.pose_landmarks),
                        "visibility": [v for v in results.pose_landmarks.visibility]
                    }
                )
                detections.append(detection)
            
            return detections
            
        except Exception as e:
            self._logger.error(f"Erreur lors de la détection MediaPipe: {e}")
            return []
    
    def _extract_landmarks(self, pose_landmarks) -> List[Dict[str, float]]:
        """
        Extrait les landmarks depuis le résultat MediaPipe.
        
        Args:
            pose_landmarks: Landmarks MediaPipe
        
        Returns:
            Liste des landmarks avec coordonnées
        """
        landmarks = []
        for idx, landmark in enumerate(pose_landmarks.landmark):
            landmarks.append({
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility
            })
        return landmarks
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur le modèle.
        
        Returns:
            Dictionnaire d'informations
        """
        return {
            "type": "MediaPipePose",
            "model_complexity": self.model_complexity,
            "min_detection_confidence": self.confidence_threshold,
            "min_tracking_confidence": self.min_tracking_confidence,
            "is_loaded": self._is_loaded
        }


class MediaPipeFallDetector(MediaPipePoseDetector):
    """
    Détecteur de chutes basé sur MediaPipe Pose.
    Analyse la pose pour détecter les chutes.
    """
    
    def __init__(
        self,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        fall_threshold: float = 0.7
    ):
        """
        Initialise le détecteur de chutes.
        
        Args:
            model_complexity: Complexité du modèle
            min_detection_confidence: Seuil de confiance détection
            min_tracking_confidence: Seuil de confiance tracking
            fall_threshold: Seuil de confiance pour les chutes
        """
        super().__init__(model_complexity, min_detection_confidence, min_tracking_confidence)
        self.fall_threshold = fall_threshold
        self._previous_landmarks = None
    
    def detect(self, frame: np.ndarray, confidence_threshold: Optional[float] = None) -> List[DetectionResult]:
        """
        Effectue la détection de chutes.
        
        Args:
            frame: Frame à analyser
            confidence_threshold: Seuil de confiance
        
        Returns:
            Liste des résultats de détection de chutes
        """
        pose_results = super().detect(frame, confidence_threshold)
        
        if not pose_results:
            return []
        
        # Analyser la pose pour détecter les chutes
        fall_detections = []
        for result in pose_results:
            landmarks = result.additional_data.get("landmarks", [])
            
            if landmarks:
                fall_confidence = self._analyze_fall(landmarks)
                
                if fall_confidence >= self.fall_threshold:
                    fall_result = DetectionResult(
                        class_id=1,
                        class_name="fall",
                        confidence=fall_confidence,
                        bbox=result.bbox,
                        additional_data={
                            "landmarks": landmarks,
                            "fall_analysis": self._get_fall_analysis(landmarks)
                        }
                    )
                    fall_detections.append(fall_result)
        
        return fall_detections
    
    def _analyze_fall(self, landmarks: List[Dict[str, float]]) -> float:
        """
        Analyse la pose pour détecter une chute.
        
        Args:
            landmarks: Landmarks de la pose
        
        Returns:
            Confiance de chute (0.0 - 1.0)
        """
        # Indices des landmarks importants
        # 0: nez, 11: hanche gauche, 12: hanche droite, 23: cheville gauche, 24: cheville droite
        
        try:
            nose = landmarks[0]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]
            
            # Calculer l'angle du corps
            hip_x = (left_hip["x"] + right_hip["x"]) / 2
            hip_y = (left_hip["y"] + right_hip["y"]) / 2
            
            ankle_x = (left_ankle["x"] + right_ankle["x"]) / 2
            ankle_y = (left_ankle["y"] + right_ankle["y"]) / 2
            
            # Si la hanche est plus basse que la cheville → position couchée
            if hip_y > ankle_y:
                return 0.9
            
            # Calculer l'angle vertical
            vertical_angle = abs(hip_y - nose["y"])
            
            # Si l'angle est grand → probablement une chute
            if vertical_angle > 0.3:
                return min(1.0, vertical_angle * 2)
            
            return 0.0
            
        except (IndexError, KeyError) as e:
            self._logger.warning(f"Erreur analyse chute: {e}")
            return 0.0
    
    def _get_fall_analysis(self, landmarks: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Retourne l'analyse détaillée de la chute.
        
        Args:
            landmarks: Landmarks de la pose
        
        Returns:
            Dictionnaire d'analyse
        """
        return {
            "body_angle": self._calculate_body_angle(landmarks),
            "is_horizontal": self._is_horizontal(landmarks),
            "head_position": self._get_head_position(landmarks)
        }
    
    def _calculate_body_angle(self, landmarks: List[Dict[str, float]]) -> float:
        """Calcule l'angle du corps."""
        try:
            nose = landmarks[0]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            
            hip_x = (left_hip["x"] + right_hip["x"]) / 2
            hip_y = (left_hip["y"] + right_hip["y"]) / 2
            
            dx = hip_x - nose["x"]
            dy = hip_y - nose["y"]
            
            angle = np.arctan2(dy, dx) * 180 / np.pi
            return abs(angle)
            
        except (IndexError, KeyError):
            return 0.0
    
    def _is_horizontal(self, landmarks: List[Dict[str, float]]) -> bool:
        """Vérifie si le corps est horizontal."""
        try:
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]
            
            hip_y = (left_hip["y"] + right_hip["y"]) / 2
            ankle_y = (left_ankle["y"] + right_ankle["y"]) / 2
            
            return hip_y > ankle_y
            
        except (IndexError, KeyError):
            return False
    
    def _get_head_position(self, landmarks: List[Dict[str, float]]) -> str:
        """Retourne la position de la tête."""
        try:
            nose = landmarks[0]
            
            if nose["y"] < 0.3:
                return "high"
            elif nose["y"] > 0.7:
                return "low"
            else:
                return "middle"
                
        except (IndexError, KeyError):
            return "unknown"


# Import cv2 pour la conversion BGR->RGB
import cv2
