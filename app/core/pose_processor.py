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

from app.core.physics_engine import PoseData
from app.config import settings


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
        enable_segmentation: bool = False,
        use_yolo_roi: bool = False
    ):
        """
        Initialise le détecteur de posture MediaPipe.
        
        Args:
            model_complexity: 0 (Lite) ou 1 (Heavy). Lite = rapide, Heavy = précis
            min_detection_confidence: Seuil de confiance pour la détection [0, 1]
            min_tracking_confidence: Seuil de confiance pour le tracking [0, 1]
            static_image_mode: True pour images statiques, False pour vidéo
            enable_segmentation: Active la segmentation de la personne
            use_yolo_roi: Utiliser ROI YOLO pour optimisation
        """
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.static_image_mode = static_image_mode
        self.enable_segmentation = enable_segmentation
        self.use_yolo_roi = use_yolo_roi
        self.current_roi = None  # ROI actuelle (x1, y1, x2, y2)
        
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
    
    def set_roi(self, bbox: Tuple[int, int, int, int]):
        """
        Définit la Region of Interest (ROI) pour optimisation YOLO.
        
        Args:
            bbox: Bounding box (x1, y1, x2, y2)
        """
        self.current_roi = bbox
    
    def clear_roi(self):
        """Supprime la ROI actuelle."""
        self.current_roi = None
    
    def process_frame(self, frame: np.ndarray) -> Optional[PoseData]:
        """
        Traite une frame vidéo et extrait les landmarks MediaPipe.
        
        Processus:
        1. Application ROI si activée (optimisation YOLO)
        2. Conversion BGR → RGB (MediaPipe attend RGB)
        3. Inférence avec BlazePose
        4. Extraction des 33 landmarks
        5. Conversion en format PoseLandmarks
        
        Args:
            frame: Image OpenCV (BGR)
        
        Returns:
            PoseData avec les 33 landmarks ou None si aucune personne détectée
        """
        if frame is None:
            return None
        
        # Mettre à jour les dimensions de l'image
        self.image_height, self.image_width = frame.shape[:2]
        
        # Appliquer ROI si activée (optimisation YOLO)
        processed_frame = frame
        roi_offset = (0, 0)
        
        if self.use_yolo_roi and self.current_roi is not None:
            x1, y1, x2, y2 = self.current_roi
            # Ajouter une marge de 10%
            margin_x = int((x2 - x1) * 0.1)
            margin_y = int((y2 - y1) * 0.1)
            x1 = max(0, x1 - margin_x)
            y1 = max(0, y1 - margin_y)
            x2 = min(self.image_width, x2 + margin_x)
            y2 = min(self.image_height, y2 + margin_y)
            
            # Extraire la ROI
            processed_frame = frame[y1:y2, x1:x2]
            roi_offset = (x1, y1)
            
            # Si ROI vide, retourner None
            if processed_frame.size == 0:
                return None
        
        # Conversion BGR → RGB
        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        
        # Inférence MediaPipe
        results = self.pose.process(rgb_frame)
        
        # Vérifier si une personne est détectée
        if results.pose_landmarks is None:
            return None
        
        # Extraire les landmarks avec ajustement ROI
        x_coords, y_coords, z_coords, visibility = self._extract_landmarks(results.pose_landmarks, roi_offset)
        
        # Créer la structure PoseData
        pose_data = PoseData(
            x=x_coords,
            y=y_coords,
            z=z_coords,
            visibility=visibility,
            timestamp=cv2.getTickCount() / cv2.getTickFrequency()
        )
        
        return pose_data
    
    def _extract_landmarks(self, mp_landmarks, roi_offset: Tuple[int, int] = (0, 0)) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Extrait les 33 landmarks depuis le résultat MediaPipe.
        
        Conversion de coordonnées normalisées [0,1] vers mètres.
        
        Formule:
        x_pixel = x_norm × roi_width + roi_offset_x
        x_meter = x_pixel × pixel_to_meter
        
        Args:
            mp_landmarks: Landmarks MediaPipe
            roi_offset: Offset de la ROI (x_offset, y_offset)
        
        Returns:
            Tuple de 4 arrays numpy: (x_coords, y_coords, z_coords, visibility)
        """
        roi_x, roi_y = roi_offset
        
        # Dimensions de la ROI si utilisée, sinon dimensions complètes
        if self.use_yolo_roi and self.current_roi is not None:
            roi_width = self.current_roi[2] - self.current_roi[0]
            roi_height = self.current_roi[3] - self.current_roi[1]
        else:
            roi_width = self.image_width
            roi_height = self.image_height
        
        x_coords = np.zeros(33)
        y_coords = np.zeros(33)
        z_coords = np.zeros(33)
        visibility = np.zeros(33)
        
        for i in range(33):
            mp_lm = mp_landmarks.landmark[i]
            
            # Conversion normalisé → pixels (avec ajustement ROI)
            x_pixel = mp_lm.x * roi_width + roi_x
            y_pixel = mp_lm.y * roi_height + roi_y
            
            # Conversion pixels → mètres
            x_coords[i] = x_pixel * self.pixel_to_meter
            y_coords[i] = y_pixel * self.pixel_to_meter
            z_coords[i] = mp_lm.z * self.image_width * self.pixel_to_meter  # z est relatif à la largeur
            visibility[i] = mp_lm.visibility
        
        return x_coords, y_coords, z_coords, visibility
    
    def draw_skeleton(
        self,
        frame: np.ndarray,
        pose_data: Optional[PoseData] = None,
        show_connections: bool = True,
        show_landmarks: bool = True
    ) -> np.ndarray:
        """
        Dessine le squelette sur l'image (pour debug/UI).
        
        Args:
            frame: Image originale
            pose_data: Données de pose (si None, retraite la frame)
            show_connections: Dessiner les connexions entre articulations
            show_landmarks: Dessiner les points d'articulation
        
        Returns:
            Image avec le squelette dessiné
        """
        output_frame = frame.copy()
        
        # Si pas de landmarks fournis, traiter la frame
        if pose_data is None:
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
        
        # Convertir nos PoseData vers le format MediaPipe pour le dessin
        mp_landmarks = self._convert_to_mediapipe_format(pose_data)
        
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
    
    def _convert_to_mediapipe_format(self, pose_data: PoseData):
        """
        Convertit nos PoseData vers le format MediaPipe pour le dessin.
        
        Conversion mètres → normalisé [0,1].
        
        Args:
            pose_data: Nos données de pose en mètres
        
        Returns:
            LandmarkList MediaPipe
        """
        from mediapipe.framework.formats import landmark_pb2
        
        mp_landmark_list = landmark_pb2.NormalizedLandmarkList()
        
        for i in range(33):
            mp_lm = mp_landmark_list.landmark.add()
            
            # Conversion mètres → normalisé
            mp_lm.x = pose_data.x[i] / (self.image_width * self.pixel_to_meter)
            mp_lm.y = pose_data.y[i] / (self.image_height * self.pixel_to_meter)
            mp_lm.z = pose_data.z[i] / (self.image_width * self.pixel_to_meter)
            mp_lm.visibility = pose_data.visibility[i]
        
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
