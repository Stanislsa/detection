"""
Intégration MediaPipe Pose pour l'estimation de posture.

Reference:
- MediaPipe Pose (Google, 2024) - BlazePose neural network
- 33 landmarks with (x, y, z) coordinates and visibility
"""

import cv2
import mediapipe as mp
from typing import Optional, Tuple, List
import numpy as np

from detection.physics_engine import PoseLandmarks, Landmark
from config.constants import DEFAULT_FPS


class PoseEstimator:
    """
    Wrapper autour de MediaPipe Pose pour l'estimation de posture.
    
    Interface entre le flux vidéo OpenCV et le moteur physique.
    """
    
    def __init__(
        self,
        model_complexity: int = 1,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        static_image_mode: bool = False,
        enable_segmentation: bool = False
    ):
        """
        Initialise le détecteur de posture MediaPipe.
        
        Args:
            model_complexity: 0 (Lite) ou 1 (Heavy). Lite = rapide, Heavy = précis
            min_detection_confidence: Seuil de confiance pour la détection [0, 1]
            min_tracking_confidence: Seuil de confiance pour le tracking [0, 1]
            static_image_mode: True pour images statiques, False pour vidéo
            enable_segmentation: Active la segmentation de la personne
        """
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.static_image_mode = static_image_mode
        self.enable_segmentation = enable_segmentation
        
        # Initialiser MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=True,
            enable_segmentation=enable_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Utilitaires de dessin (pour debug/UI)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Facteur de conversion pixel → mètre (à configurer selon la caméra)
        self.pixel_to_meter = 0.001  # 1 pixel = 1 mm par défaut
        self.image_width = 1920
        self.image_height = 1080
    
    def set_calibration(self, pixel_to_meter: float, image_width: int, image_height: int):
        """
        Configure la calibration pour la conversion pixels → mètres.
        
        Args:
            pixel_to_meter: Facteur de conversion (mètres par pixel)
            image_width: Largeur de l'image en pixels
            image_height: Hauteur de l'image en pixels
        """
        self.pixel_to_meter = pixel_to_meter
        self.image_width = image_width
        self.image_height = image_height
    
    def process_frame(self, frame: np.ndarray) -> Optional[PoseLandmarks]:
        """
        Traite une frame vidéo et extrait les landmarks MediaPipe.
        
        Processus:
        1. Conversion BGR → RGB (MediaPipe attend RGB)
        2. Inférence avec BlazePose
        3. Extraction des 33 landmarks
        4. Conversion en format PoseLandmarks
        
        Args:
            frame: Image OpenCV (BGR)
        
        Returns:
            PoseLandmarks avec les 33 landmarks ou None si aucune personne détectée
        """
        if frame is None:
            return None
        
        # Mettre à jour les dimensions de l'image
        self.image_height, self.image_width = frame.shape[:2]
        
        # Conversion BGR → RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Inférence MediaPipe
        results = self.pose.process(rgb_frame)
        
        # Vérifier si une personne est détectée
        if results.pose_landmarks is None:
            return None
        
        # Extraire les landmarks
        landmarks = self._extract_landmarks(results.pose_landmarks)
        
        # Créer la structure PoseLandmarks
        pose_landmarks = PoseLandmarks(
            landmarks=landmarks,
            timestamp=cv2.getTickCount() / cv2.getTickFrequency()
        )
        
        return pose_landmarks
    
    def _extract_landmarks(self, mp_landmarks) -> List[Landmark]:
        """
        Extrait les 33 landmarks depuis le résultat MediaPipe.
        
        Conversion de coordonnées normalisées [0,1] vers mètres.
        
        Formule:
        x_pixel = x_norm × width
        x_meter = x_pixel × pixel_to_meter
        
        Args:
            mp_landmarks: Landmarks MediaPipe
        
        Returns:
            Liste de 33 objets Landmark
        """
        landmarks = []
        
        for i in range(33):
            mp_lm = mp_landmarks.landmark[i]
            
            # Conversion normalisé → mètres
            x_meter = mp_lm.x * self.image_width * self.pixel_to_meter
            y_meter = mp_lm.y * self.image_height * self.pixel_to_meter
            z_meter = mp_lm.z * self.image_width * self.pixel_to_meter  # z est relatif à la largeur
            
            # Créer le Landmark
            landmark = Landmark(
                x=x_meter,
                y=y_meter,
                z=z_meter,
                visibility=mp_lm.visibility,
                timestamp=cv2.getTickCount() / cv2.getTickFrequency()
            )
            
            landmarks.append(landmark)
        
        return landmarks
    
    def draw_skeleton(
        self,
        frame: np.ndarray,
        pose_landmarks: Optional[PoseLandmarks] = None,
        show_connections: bool = True,
        show_landmarks: bool = True
    ) -> np.ndarray:
        """
        Dessine le squelette sur l'image (pour debug/UI).
        
        Args:
            frame: Image originale
            pose_landmarks: Landmarks à dessiner (si None, retraite la frame)
            show_connections: Dessiner les connexions entre articulations
            show_landmarks: Dessiner les points d'articulation
        
        Returns:
            Image avec le squelette dessiné
        """
        output_frame = frame.copy()
        
        # Si pas de landmarks fournis, traiter la frame
        if pose_landmarks is None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks is None:
                return output_frame
            
            # Dessiner avec MediaPipe
            self.mp_drawing.draw_landmarks(
                output_frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS if show_connections else None,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style() if show_landmarks else None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_pose_connections_style() if show_connections else None
            )
            
            return output_frame
        
        # Convertir nos landmarks vers le format MediaPipe pour le dessin
        mp_landmarks = self._convert_to_mediapipe_format(pose_landmarks)
        
        # Dessiner
        if show_connections:
            self.mp_drawing.draw_landmarks(
                output_frame,
                mp_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style() if show_landmarks else None,
                connection_drawing_spec=self.mp_drawing_styles.get_default_pose_connections_style()
            )
        elif show_landmarks:
            self.mp_drawing.draw_landmarks(
                output_frame,
                mp_landmarks,
                None,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
        
        return output_frame
    
    def _convert_to_mediapipe_format(self, pose_landmarks: PoseLandmarks):
        """
        Convertit nos Landmarks vers le format MediaPipe pour le dessin.
        
        Conversion mètres → normalisé [0,1].
        
        Args:
            pose_landmarks: Nos landmarks en mètres
        
        Returns:
        LandmarkList MediaPipe
        """
        from mediapipe.framework.formats import landmark_pb2
        
        mp_landmark_list = landmark_pb2.NormalizedLandmarkList()
        
        for lm in pose_landmarks.landmarks:
            mp_lm = mp_landmark_list.landmark.add()
            
            # Conversion mètres → normalisé
            mp_lm.x = lm.x / (self.image_width * self.pixel_to_meter)
            mp_lm.y = lm.y / (self.image_height * self.pixel_to_meter)
            mp_lm.z = lm.z / (self.image_width * self.pixel_to_meter)
            mp_lm.visibility = lm.visibility
        
        return mp_landmark_list
    
    def get_landmark_names(self) -> List[str]:
        """
        Retourne les noms des 33 landmarks MediaPipe.
        
        Returns:
            Liste des noms des landmarks
        """
        return [
            "nose", "left_eye_inner", "left_eye", "left_eye_outer",
            "right_eye_inner", "right_eye", "right_eye_outer",
            "left_ear", "right_ear", "mouth_left", "mouth_right",
            "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
            "left_wrist", "right_wrist", "left_pinky", "right_pinky",
            "left_index", "right_index", "left_thumb", "right_thumb",
            "left_hip", "right_hip", "left_knee", "right_knee",
            "left_ankle", "right_ankle", "left_heel", "right_heel",
            "left_foot_index", "right_foot_index"
        ]
    
    def close(self):
        """Libère les ressources MediaPipe."""
        if self.pose:
            self.pose.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
