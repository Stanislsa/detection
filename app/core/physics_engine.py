"""
Moteur de calculs physiques pour la détection de chutes.
Implémente les lois de Newton, le modèle de Dempster, et les seuils de Bourke.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field
from collections import deque
import time

from app.config import settings, BODY_SEGMENT_MASS, GRAVITY_LEVELS


@dataclass
class PoseData:
    """Données brutes des landmarks MediaPipe (33 points)."""
    x: np.ndarray           # Shape: (33,) - coordonnées normalisées [0,1]
    y: np.ndarray
    z: np.ndarray
    visibility: np.ndarray  # Confiance de détection [0,1]
    timestamp: float = field(default_factory=time.time)


@dataclass
class PhysicsState:
    """État physique calculé à un instant t."""
    # Position
    center_of_mass: Tuple[float, float]     # (x, y) en mètres (normalisés)
    
    # Cinématique verticale
    vertical_velocity: float                 # m/s (négatif = descente)
    vertical_acceleration: float             # m/s²
    
    # Cinématique globale
    resultant_acceleration: float            # m/s² (norme des 3 axes)
    
    # Rotation
    trunk_angle: float                       # degrés par rapport à verticale
    angular_velocity: float                  # deg/s
    
    # Stabilité
    moment_of_inertia: float                 # kg·m² (normalisé)
    
    # Position au sol
    distance_to_ground: float                # mètres (hauteur des pieds)
    
    # État
    is_free_fall: bool                       # Détection chute libre
    is_ground_contact: bool                  # Contact au sol confirmé
    
    # Métadonnées
    timestamp: float
    frame_number: int = 0


class PhysicsEngine:
    """
    Moteur physique basé sur :
    - Newton (1687) : Lois du mouvement (F=ma, dérivées)
    - Dempster (1955) : Modèle anthropométrique (répartition masses)
    - Euler (1765) : Moment d'inertie (stabilité rotation)
    - Bourke et al. (2007) : Seuils de détection (accélération, vitesse angulaire)
    """
    
    def __init__(self, frame_rate: int = None, pixel_scale: float = 1.0):
        self.frame_rate = frame_rate or settings.DEFAULT_FPS
        self.dt = 1.0 / self.frame_rate
        self.pixel_scale = pixel_scale  # Conversion pixel → mètre
        
        # Historique circulaire pour les dérivées (5 frames = ~167ms)
        self.history: deque = deque(maxlen=5)
        self.frame_count = 0
        
        # État précédent
        self._prev_cm: Optional[Tuple[float, float]] = None
        self._prev_vy: Optional[float] = None
        self._prev_theta: Optional[float] = None
        self._prev_inertia: Optional[float] = None
    
    def process(self, pose: PoseData) -> PhysicsState:
        """
        Traite un nouveau frame et calcule l'état physique complet.
        
        Pipeline :
        1. Stockage historique
        2. Centre de masse (Dempster)
        3. Vitesse verticale (Galilée)
        4. Accélération verticale (Newton)
        5. Accélération résultante (Bourke)
        6. Angle du tronc (Euclide)
        7. Vitesse angulaire (Bourke)
        8. Moment d'inertie (Euler)
        9. Distance au sol
        10. Détection chute libre
        """
        self.frame_count += 1
        self.history.append(pose)
        
        # 1. Centre de Masse (Dempster, 1955)
        cm = self._compute_center_of_mass(pose)
        
        # 2. Vitesse verticale
        vy = self._compute_vertical_velocity(cm)
        
        # 3. Accélération verticale
        ay = self._compute_vertical_acceleration(vy)
        
        # 4. Accélération résultante (3 axes)
        a_res = self._compute_resultant_acceleration(pose)
        
        # 5. Angle du tronc
        theta = self._compute_trunk_angle(pose)
        
        # 6. Vitesse angulaire
        omega = self._compute_angular_velocity(theta)
        
        # 7. Moment d'inertie
        inertia = self._compute_moment_of_inertia(pose, cm)
        
        # 8. Distance au sol
        dist_ground = self._compute_distance_to_ground(pose)
        
        # 9. Détection chute libre
        is_free_fall = self._detect_free_fall(ay, vy)
        
        # 10. Contact au sol
        is_ground = dist_ground < 0.15  # 15cm = contact
        
        # Mise à jour état précédent
        self._prev_cm = cm
        self._prev_vy = vy
        self._prev_theta = theta
        self._prev_inertia = inertia
        
        return PhysicsState(
            center_of_mass=cm,
            vertical_velocity=vy,
            vertical_acceleration=ay,
            resultant_acceleration=a_res,
            trunk_angle=theta,
            angular_velocity=omega,
            moment_of_inertia=inertia,
            distance_to_ground=dist_ground,
            is_free_fall=is_free_fall,
            is_ground_contact=is_ground,
            timestamp=pose.timestamp,
            frame_number=self.frame_count
        )
    
    # ═══════════════════════════════════════════════════════
    # MÉTHODES DE CALCUL PHYSIQUE
    # ═══════════════════════════════════════════════════════
    
    def _compute_center_of_mass(self, pose: PoseData) -> Tuple[float, float]:
        """
        Centre de masse selon Dempster (1955).
        CM = Σ(m_i × p_i) / Σ(m_i)
        """
        total_mass = 0.0
        cm_x = 0.0
        cm_y = 0.0
        
        for idx, mass_ratio in BODY_SEGMENT_MASS.items():
            if idx < len(pose.x) and pose.visibility[idx] > 0.5:
                total_mass += mass_ratio
                cm_x += mass_ratio * pose.x[idx]
                cm_y += mass_ratio * pose.y[idx]
        
        if total_mass > 0:
            cm_x /= total_mass
            cm_y /= total_mass
        
        # Conversion en mètres (échelle normalisée → réelle)
        return (cm_x * self.pixel_scale, cm_y * self.pixel_scale)
    
    def _compute_vertical_velocity(self, cm: Tuple[float, float]) -> float:
        """
        Vitesse verticale du CM.
        v_y = Δy / Δt  (Galilée / Newton)
        """
        if self._prev_cm is None:
            return 0.0
        
        delta_y = cm[1] - self._prev_cm[1]
        return delta_y / self.dt
    
    def _compute_vertical_acceleration(self, vy: float) -> float:
        """
        Accélération verticale.
        a_y = Δv_y / Δt  (Newton, 1687)
        """
        if self._prev_vy is None:
            return 0.0
        
        return (vy - self._prev_vy) / self.dt
    
    def _compute_resultant_acceleration(self, pose: PoseData) -> float:
        """
        Accélération résultante sur les 3 axes.
        a_rés = √(a_x² + a_y² + a_z²)  (Bourke et al., 2007)
        
        Calculée par dérivée seconde numérique sur l'historique.
        """
        if len(self.history) < 3:
            return 0.0
        
        # Récupération des 3 derniers CM sur chaque axe
        recent = list(self.history)[-3:]
        cms_x = [self._compute_center_of_mass_single(p, 0) for p in recent]
        cms_y = [self._compute_center_of_mass_single(p, 1) for p in recent]
        cms_z = [np.mean(p.z[p.visibility > 0.5]) if np.any(p.visibility > 0.5) else 0.0 
                 for p in recent]
        
        # Dérivée seconde : a ≈ (x(t) - 2x(t-dt) + x(t-2dt)) / dt²
        ax = self._second_derivative(cms_x)
        ay = self._second_derivative(cms_y)
        az = self._second_derivative(cms_z)
        
        a_res = np.sqrt(ax**2 + ay**2 + az**2)
        
        # Conversion en m/s² (échelle + temps)
        return a_res * self.pixel_scale / (self.dt ** 2)
    
    def _compute_center_of_mass_single(self, pose: PoseData, axis: int) -> float:
        """Calcule une coordonnée du CM (0=x, 1=y)."""
        total_mass = 0.0
        coord = 0.0
        coords = pose.x if axis == 0 else pose.y
        
        for idx, mass_ratio in BODY_SEGMENT_MASS.items():
            if idx < len(coords) and pose.visibility[idx] > 0.5:
                total_mass += mass_ratio
                coord += mass_ratio * coords[idx]
        
        return coord / total_mass if total_mass > 0 else 0.0
    
    def _compute_trunk_angle(self, pose: PoseData) -> float:
        """
        Angle du tronc par rapport à la verticale.
        θ = arccos( (v_tronc · v_vertical) / |v_tronc| )  (Euclide)
        """
        # Points médians : épaules (11,12) et hanches (23,24)
        shoulder_x = (pose.x[11] + pose.x[12]) / 2
        shoulder_y = (pose.y[11] + pose.y[12]) / 2
        hip_x = (pose.x[23] + pose.x[24]) / 2
        hip_y = (pose.y[23] + pose.y[24]) / 2
        
        # Vecteur tronc (du haut vers le bas)
        trunk_vec = np.array([hip_x - shoulder_x, hip_y - shoulder_y])
        vertical_vec = np.array([0.0, 1.0])
        
        # Normes
        trunk_norm = np.linalg.norm(trunk_vec)
        if trunk_norm < 1e-10:
            return 0.0
        
        # Produit scalaire
        cos_theta = np.dot(trunk_vec, vertical_vec) / trunk_norm
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        
        theta = np.degrees(np.arccos(cos_theta))
        return theta
    
    def _compute_angular_velocity(self, theta: float) -> float:
        """
        Vitesse angulaire du tronc.
        ω = Δθ / Δt  (Bourke et al., 2007)
        """
        if self._prev_theta is None:
            return 0.0
        
        delta_theta = theta - self._prev_theta
        return delta_theta / self.dt
    
    def _compute_moment_of_inertia(self, pose: PoseData, 
                                    cm: Tuple[float, float]) -> float:
        """
        Moment d'inertie du corps par rapport au CM.
        I = Σ(m_i × d_i²)  (Euler, 1765)
        
        d_i = distance entre le landmark i et le CM.
        """
        inertia = 0.0
        
        for idx, mass_ratio in BODY_SEGMENT_MASS.items():
            if idx < len(pose.x) and pose.visibility[idx] > 0.5:
                dx = pose.x[idx] * self.pixel_scale - cm[0]
                dy = pose.y[idx] * self.pixel_scale - cm[1]
                distance_sq = dx**2 + dy**2
                inertia += mass_ratio * distance_sq
        
        return inertia
    
    def _compute_distance_to_ground(self, pose: PoseData) -> float:
        """
        Distance moyenne des chevilles au sol (bas de l'image).
        h = 1 - moyenne(y_chevilles)
        """
        ankle_y = (pose.y[27] + pose.y[28]) / 2
        # Conversion : 1.0 = haut, 0.0 = bas de l'image
        return (1.0 - ankle_y) * self.pixel_scale
    
    def _detect_free_fall(self, ay: float, vy: float) -> bool:
        """
        Détection de chute libre.
        Conditions : accélération verticale ≈ -g ET vitesse descendante
        
        a_y < -0.8g  (décélération gravitationnelle)
        v_y < -1.0 m/s  (mouvement descendant significatif)
        """
        return (ay < -settings.GRAVITY * 0.8) and (vy < -1.0)
    
    # ═══════════════════════════════════════════════════════
    # UTILITAIRES
    # ═══════════════════════════════════════════════════════
    
    @staticmethod
    def _second_derivative(values: List[float]) -> float:
        """
        Dérivée seconde numérique (accélération).
        a ≈ (x(t) - 2x(t-dt) + x(t-2dt)) / dt²
        """
        if len(values) < 3:
            return 0.0
        return (values[-1] - 2 * values[-2] + values[-3])
    
    def reset(self):
        """Réinitialise l'état du moteur."""
        self.history.clear()
        self.frame_count = 0
        self._prev_cm = None
        self._prev_vy = None
        self._prev_theta = None
        self._prev_inertia = None
