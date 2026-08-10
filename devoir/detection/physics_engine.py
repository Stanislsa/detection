"""
Moteur de Calculs Physiques pour la Détection de Chutes.

Reference: 
- Dempster (1955) - Anthropometric model
- Bourke et al. (2007) - Fall detection thresholds
- Euler (1765) - Moment of inertia
- Galilée/Newton - Kinematics
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from collections import deque
import math
from datetime import datetime

from config.constants import (
    GRAVITY, BODY_SEGMENT_MASS, THRESHOLD_ACCEL_RESULTANT,
    THRESHOLD_ANGULAR_VELOCITY, THRESHOLD_VERTICAL_VELOCITY
)
from ai_engine.geometry.vectors import (
    dot_product, norm, subtract_vectors, scalar_multiply
)


@dataclass
class Landmark:
    """Structure d'un landmark MediaPipe."""
    x: float
    y: float
    z: float
    visibility: float
    timestamp: float


@dataclass
class PoseLandmarks:
    """Structure des 33 points MediaPipe."""
    landmarks: List[Landmark] = field(default_factory=list)
    timestamp: float = 0.0
    
    def __post_init__(self):
        if not self.landmarks:
            self.timestamp = datetime.now().timestamp()


@dataclass
class PhysicsState:
    """État physique calculé à un instant t."""
    timestamp: float
    
    # Centre de masse
    center_of_mass: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Vitesses (m/s)
    vertical_velocity: float = 0.0
    velocity_vector: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Accélérations (m/s²)
    vertical_acceleration: float = 0.0
    resultant_acceleration: float = 0.0
    acceleration_vector: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    # Angles (degrés)
    trunk_angle: float = 0.0
    
    # Vitesse angulaire (deg/s)
    angular_velocity: float = 0.0
    
    # Inertie
    moment_of_inertia: float = 0.0
    
    # Indicateurs de chute libre
    is_free_fall: bool = False


class PhysicsEngine:
    """
    Moteur principal de calculs physiques avec historique circulaire (5 frames).
    
    Implémente les lois physiques pour la détection de chute.
    """
    
    def __init__(self, history_size: int = 5):
        """
        Initialise le moteur physique.
        
        Args:
            history_size: Taille de l'historique circulaire (défaut: 5 frames)
        """
        self.history_size = history_size
        self.history: deque[PhysicsState] = deque(maxlen=history_size)
        self.frame_interval = 1.0 / 30.0  # 30 FPS par défaut
    
    def set_frame_interval(self, fps: float):
        """
        Définit l'intervalle entre frames.
        
        Args:
            fps: Frames par seconde
        """
        self.frame_interval = 1.0 / fps
    
    def process_frame(self, pose_landmarks: PoseLandmarks) -> PhysicsState:
        """
        Traite une frame et calcule l'état physique complet.
        
        Args:
            pose_landmarks: Landmarks MediaPipe de la frame actuelle
        
        Returns:
            PhysicsState calculé
        """
        # Calculer le centre de masse
        com = self._calculate_center_of_mass(pose_landmarks)
        
        # Calculer les vitesses
        velocity, vertical_velocity = self._calculate_velocity(com)
        
        # Calculer les accélérations
        acceleration, vertical_acceleration, resultant_accel = self._calculate_acceleration(velocity)
        
        # Calculer l'angle du tronc
        trunk_angle = self._calculate_trunk_angle(pose_landmarks)
        
        # Calculer la vitesse angulaire
        angular_velocity = self._calculate_angular_velocity(trunk_angle)
        
        # Calculer le moment d'inertie
        moment_of_inertia = self._calculate_moment_of_inertia(pose_landmarks, com)
        
        # Détecter la chute libre
        is_free_fall = self._detect_free_fall(vertical_acceleration, vertical_velocity)
        
        # Créer l'état physique
        state = PhysicsState(
            timestamp=pose_landmarks.timestamp,
            center_of_mass=com,
            vertical_velocity=vertical_velocity,
            velocity_vector=velocity,
            vertical_acceleration=vertical_acceleration,
            resultant_acceleration=resultant_accel,
            acceleration_vector=acceleration,
            trunk_angle=trunk_angle,
            angular_velocity=angular_velocity,
            moment_of_inertia=moment_of_inertia,
            is_free_fall=is_free_fall
        )
        
        # Ajouter à l'historique
        self.history.append(state)
        
        return state
    
    def _calculate_center_of_mass(self, pose: PoseLandmarks) -> Tuple[float, float, float]:
        """
        Calcule le centre de masse selon le modèle de Dempster (1955).
        
        Formule:
        CM_x = (∑ m_i * x_i) / (∑ m_i)
        CM_y = (∑ m_i * y_i) / (∑ m_i)
        
        Où m_i = masse du segment (ratio du poids total selon Dempster)
        
        Args:
            pose: Landmarks MediaPipe
        
        Returns:
            Coordonnées du centre de masse (x, y, z)
        """
        total_mass = 0.0
        weighted_x = 0.0
        weighted_y = 0.0
        weighted_z = 0.0
        
        for idx, landmark in enumerate(pose.landmarks):
            if idx in BODY_SEGMENT_MASS:
                mass = BODY_SEGMENT_MASS[idx]
                total_mass += mass
                weighted_x += mass * landmark.x
                weighted_y += mass * landmark.y
                weighted_z += mass * landmark.z
        
        if total_mass == 0:
            return (0.0, 0.0, 0.0)
        
        return (weighted_x / total_mass, weighted_y / total_mass, weighted_z / total_mass)
    
    def _calculate_velocity(self, current_com: Tuple[float, float, float]) -> Tuple[Tuple[float, float, float], float]:
        """
        Calcule la vitesse verticale selon Galilée/Newton.
        
        Formule: v_y(t) = (CM_y(t) - CM_y(t-1)) / Δt
        
        Args:
            current_com: Centre de masse actuel
        
        Returns:
            (velocity_vector, vertical_velocity)
        """
        if len(self.history) < 1:
            return ((0.0, 0.0, 0.0), 0.0)
        
        prev_state = self.history[-1]
        prev_com = prev_state.center_of_mass
        
        # Vitesse = (position_actuelle - position_précédente) / Δt
        delta = subtract_vectors(current_com, prev_com)
        velocity = scalar_multiply(delta, 1.0 / self.frame_interval)
        
        # Vitesse verticale (composante y, inversée car y augmente vers le bas)
        vertical_velocity = -velocity[1]
        
        return (velocity, vertical_velocity)
    
    def _calculate_acceleration(self, current_velocity: Tuple[float, float, float]) -> Tuple[Tuple[float, float, float], float, float]:
        """
        Calcule l'accélération selon Newton.
        
        Formule: a_y(t) = (v_y(t) - v_y(t-1)) / Δt
        Accélération résultante: a_res = sqrt(a_x² + a_y² + a_z²)
        
        Args:
            current_velocity: Vecteur vitesse actuel
        
        Returns:
            (acceleration_vector, vertical_acceleration, resultant_acceleration)
        """
        if len(self.history) < 1:
            return ((0.0, 0.0, 0.0), 0.0, 0.0)
        
        prev_state = self.history[-1]
        prev_velocity = prev_state.velocity_vector
        
        # Accélération = (vitesse_actuelle - vitesse_précédente) / Δt
        delta = subtract_vectors(current_velocity, prev_velocity)
        acceleration = scalar_multiply(delta, 1.0 / self.frame_interval)
        
        # Accélération verticale
        vertical_acceleration = -acceleration[1]
        
        # Accélération résultante (Bourke et al.)
        resultant_accel = norm(acceleration)
        
        return (acceleration, vertical_acceleration, resultant_accel)
    
    def _calculate_trunk_angle(self, pose: PoseLandmarks) -> float:
        """
        Calcule l'angle du tronc par produit scalaire.
        
        Formule:
        v_tronc = (x_hanche - x_épaule, y_hanche - y_épaule)
        θ = arccos((v_tronc · v_vertical) / (|v_tronc| * |v_vertical|))
        
        Args:
            pose: Landmarks MediaPipe
        
        Returns:
            Angle du tronc en degrés
        """
        # Points MediaPipe pour les épaules et hanches
        left_shoulder = pose.landmarks[11]
        right_shoulder = pose.landmarks[12]
        left_hip = pose.landmarks[23]
        right_hip = pose.landmarks[24]
        
        # Centre des épaules
        shoulder_center = (
            (left_shoulder.x + right_shoulder.x) / 2,
            (left_shoulder.y + right_shoulder.y) / 2,
            (left_shoulder.z + right_shoulder.z) / 2
        )
        
        # Centre des hanches
        hip_center = (
            (left_hip.x + right_hip.x) / 2,
            (left_hip.y + right_hip.y) / 2,
            (left_hip.z + right_hip.z) / 2
        )
        
        # Vecteur tronc (de épaules vers hanches)
        trunk_vector = subtract_vectors(hip_center, shoulder_center)
        
        # Vecteur vertical (vers le bas)
        vertical_vector = (0.0, 1.0, 0.0)
        
        # Angle par produit scalaire
        dot = dot_product(trunk_vector, vertical_vector)
        trunk_norm = norm(trunk_vector)
        vertical_norm = norm(vertical_vector)
        
        if trunk_norm == 0 or vertical_norm == 0:
            return 0.0
        
        cos_theta = dot / (trunk_norm * vertical_norm)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        
        angle_rad = math.acos(cos_theta)
        angle_deg = math.degrees(angle_rad)
        
        return angle_deg
    
    def _calculate_angular_velocity(self, current_trunk_angle: float) -> float:
        """
        Calcule la vitesse angulaire selon Bourke et al. (2007).
        
        Formule: ω = Δθ / Δt = (θ(t) - θ(t-1)) / Δt
        
        Args:
            current_trunk_angle: Angle du tronc actuel en degrés
        
        Returns:
            Vitesse angulaire en degrés/seconde
        """
        if len(self.history) < 1:
            return 0.0
        
        prev_state = self.history[-1]
        prev_angle = prev_state.trunk_angle
        
        delta_angle = current_trunk_angle - prev_angle
        angular_velocity = delta_angle / self.frame_interval
        
        return angular_velocity
    
    def _calculate_moment_of_inertia(self, pose: PoseLandmarks, com: Tuple[float, float, float]) -> float:
        """
        Calcule le moment d'inertie selon Euler (1765).
        
        Formule: I = ∑ m_i * d_i² = ∑ m_i * [(x_i - CM_x)² + (y_i - CM_y)²]
        
        Args:
            pose: Landmarks MediaPipe
            com: Centre de masse
        
        Returns:
            Moment d'inertie
        """
        moment_of_inertia = 0.0
        
        for idx, landmark in enumerate(pose.landmarks):
            if idx in BODY_SEGMENT_MASS:
                mass = BODY_SEGMENT_MASS[idx]
                
                # Distance au carré par rapport au centre de masse
                dx = landmark.x - com[0]
                dy = landmark.y - com[1]
                distance_squared = dx * dx + dy * dy
                
                moment_of_inertia += mass * distance_squared
        
        return moment_of_inertia
    
    def _detect_free_fall(self, vertical_acceleration: float, vertical_velocity: float) -> bool:
        """
        Détecte la chute libre.
        
        Critères: a_y < -0.8g ET v_y < -1.0 m/s
        
        Args:
            vertical_acceleration: Accélération verticale (m/s²)
            vertical_velocity: Vitesse verticale (m/s)
        
        Returns:
            True si chute libre détectée
        """
        threshold_accel = -0.8 * GRAVITY
        threshold_velocity = -1.0
        
        return vertical_acceleration < threshold_accel and vertical_velocity < threshold_velocity
    
    def get_previous_state(self, offset: int = 1) -> Optional[PhysicsState]:
        """
        Récupère un état précédent de l'historique.
        
        Args:
            offset: Décalage dans l'historique (1 = précédent immédiat)
        
        Returns:
            PhysicsState ou None si indisponible
        """
        if len(self.history) <= offset:
            return None
        return self.history[-(offset + 1)]
    
    def clear_history(self):
        """Efface l'historique des états."""
        self.history.clear()
