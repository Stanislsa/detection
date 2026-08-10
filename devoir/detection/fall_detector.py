"""
Détecteur de Chute Hiérarchique.

Reference:
- Srikongtham et al. - Vertical velocity threshold
- Bourke et al. (2007) - Acceleration threshold
- Noury et al. - Trunk angle threshold
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from collections import deque
from enum import Enum
import math

from config.constants import (
    THRESHOLD_ACCEL_RESULTANT, THRESHOLD_ANGULAR_VELOCITY,
    THRESHOLD_VERTICAL_VELOCITY, THRESHOLD_TRUNK_ANGLE,
    THRESHOLD_IMMOBILITY_VARIANCE, THRESHOLD_IMMOBILITY_TIME,
    WEIGHTS_FALL_CONFIDENCE, DELAY_PROFILE
)
from detection.physics_engine import PhysicsState


class FallStatus(Enum):
    """États possibles de la détection de chute."""
    NO_FALL = "no_fall"
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    FALSE_ALARM = "false_alarm"


@dataclass
class FallDetectionResult:
    """Résultat structuré de la détection de chute."""
    status: FallStatus
    confidence_score: float
    timestamp: float
    
    # Scores individuels
    vertical_velocity_score: float = 0.0
    acceleration_score: float = 0.0
    trunk_angle_score: float = 0.0
    inertia_score: float = 0.0
    distance_to_ground_score: float = 0.0
    
    # Critères déclenchés
    criteria_triggered: List[str] = field(default_factory=list)
    
    # Données post-impact
    immobility_variance: float = 0.0
    immobility_time: float = 0.0
    is_immobile: bool = False
    is_recovering: bool = False
    trunk_angle_change: float = 0.0
    
    # Métadonnées
    profile_type: str = "senior_autonome"


class FallDetector:
    """
    Détecteur de chute hiérarchique avec machine à états.
    
    Niveaux de détection:
    1. Filtrage rapide par seuils physiques
    2. Scoring de confiance pondéré
    3. Analyse post-impact (immobilité vs récupération)
    """
    
    def __init__(self, profile_type: str = "senior_autonome", fps: float = 30.0):
        """
        Initialise le détecteur de chute.
        
        Args:
            profile_type: Type de profil (senior_fragile, senior_autonome, adulte, handicape)
            fps: Frames par seconde pour le calcul des durées
        """
        self.profile_type = profile_type
        self.fps = fps
        self.frame_interval = 1.0 / fps
        
        # Machine à états
        self.current_status = FallStatus.NO_FALL
        self.suspicion_start_time: Optional[float] = None
        
        # Historique pour analyse post-impact (90 frames = 3s à 30 FPS)
        self.post_impact_window_size = int(3.0 * fps)
        self.post_impact_history: deque[Tuple[float, Tuple[float, float]]] = deque(maxlen=self.post_impact_window_size)
        
        # Délai d'observation selon profil
        self.observation_delay = DELAY_PROFILE.get(profile_type, 12.0)
        
        # Compteur de critères pour voting
        self.criteria_count = 0
    
    def set_profile(self, profile_type: str):
        """
        Change le profil utilisateur.
        
        Args:
            profile_type: Nouveau type de profil
        """
        self.profile_type = profile_type
        self.observation_delay = DELAY_PROFILE.get(profile_type, 12.0)
    
    def process_frame(self, physics_state: PhysicsState, current_time: float) -> FallDetectionResult:
        """
        Traite une frame et effectue la détection hiérarchique.
        
        Args:
            physics_state: État physique calculé
            current_time: Timestamp actuel
        
        Returns:
            FallDetectionResult
        """
        # Niveau 1: Filtrage rapide par seuils physiques
        criteria_triggered = self._check_thresholds(physics_state)
        
        # Niveau 2: Scoring de confiance pondéré
        scores = self._calculate_confidence_scores(physics_state)
        confidence_score = self._calculate_weighted_score(scores)
        
        # Voting: suspicion si ≥ 2 critères parmi 4
        self.criteria_count = len(criteria_triggered)
        
        # Machine à états
        result = self._update_state_machine(
            physics_state, current_time, confidence_score, 
            scores, criteria_triggered
        )
        
        # Niveau 3: Analyse post-impact (si suspected ou confirmed)
        if self.current_status in [FallStatus.SUSPECTED, FallStatus.CONFIRMED]:
            self._analyze_post_impact(physics_state, result)
        
        result.profile_type = self.profile_type
        
        return result
    
    def _check_thresholds(self, state: PhysicsState) -> List[str]:
        """
        Niveau 1: Vérifie les seuils physiques (voting à seuils).
        
        Critères:
        - Accélération résultante > 3g
        - Vitesse angulaire > 200 deg/s
        - Vitesse verticale < -2.5 m/s
        - Angle du tronc > 60°
        
        Args:
            state: État physique
        
        Returns:
            Liste des critères déclenchés
        """
        triggered = []
        
        # Accélération résultante (Bourke et al.)
        if state.resultant_acceleration > THRESHOLD_ACCEL_RESULTANT:
            triggered.append("acceleration")
        
        # Vitesse angulaire (Bourke et al., 2007)
        if abs(state.angular_velocity) > THRESHOLD_ANGULAR_VELOCITY:
            triggered.append("angular_velocity")
        
        # Vitesse verticale (Srikongtham et al.)
        if state.vertical_velocity < THRESHOLD_VERTICAL_VELOCITY:
            triggered.append("vertical_velocity")
        
        # Angle du tronc (Noury et al.)
        if state.trunk_angle > THRESHOLD_TRUNK_ANGLE:
            triggered.append("trunk_angle")
        
        return triggered
    
    def _calculate_confidence_scores(self, state: PhysicsState) -> dict:
        """
        Niveau 2: Calcule les scores individuels (sigmoïdes discrètes).
        
        Args:
            state: État physique
        
        Returns:
            Dictionnaire des scores individuels
        """
        scores = {}
        
        # Score vitesse verticale (sigmoïde discrète)
        scores["vertical_velocity"] = self._score_vertical_velocity(state.vertical_velocity)
        
        # Score accélération
        scores["acceleration"] = self._score_acceleration(state.resultant_acceleration)
        
        # Score angle du tronc
        scores["trunk_angle"] = self._score_trunk_angle(state.trunk_angle)
        
        # Score inertie
        scores["inertia"] = self._score_inertia(state.moment_of_inertia)
        
        # Score distance au sol (approximation par centre de masse y)
        scores["distance_to_ground"] = self._score_distance_to_ground(state.center_of_mass[1])
        
        return scores
    
    def _score_vertical_velocity(self, velocity: float) -> float:
        """
        Score de vitesse verticale (sigmoïde discrète).
        
        s(v_y) = 1.0 si v_y < -4.0
                0.8 si -4.0 ≤ v_y < -2.5
                0.5 si -2.5 ≤ v_y < -1.5
                0.2 si -1.5 ≤ v_y < 0
                0.0 si v_y ≥ 0
        
        Args:
            velocity: Vitesse verticale (m/s)
        
        Returns:
            Score [0, 1]
        """
        if velocity < -4.0:
            return 1.0
        elif velocity < -2.5:
            return 0.8
        elif velocity < -1.5:
            return 0.5
        elif velocity < 0.0:
            return 0.2
        else:
            return 0.0
    
    def _score_acceleration(self, acceleration: float) -> float:
        """
        Score d'accélération résultante.
        
        Args:
            acceleration: Accélération résultante (m/s²)
        
        Returns:
            Score [0, 1]
        """
        threshold = THRESHOLD_ACCEL_RESULTANT
        if acceleration < threshold * 0.5:
            return 0.0
        elif acceleration < threshold:
            return 0.5
        elif acceleration < threshold * 1.5:
            return 0.8
        else:
            return 1.0
    
    def _score_trunk_angle(self, angle: float) -> float:
        """
        Score d'angle du tronc.
        
        Args:
            angle: Angle du tronc (degrés)
        
        Returns:
            Score [0, 1]
        """
        if angle < THRESHOLD_TRUNK_ANGLE * 0.5:
            return 0.0
        elif angle < THRESHOLD_TRUNK_ANGLE:
            return 0.5
        elif angle < THRESHOLD_TRUNK_ANGLE * 1.25:
            return 0.8
        else:
            return 1.0
    
    def _score_inertia(self, inertia: float) -> float:
        """
        Score d'inertie (variation du moment d'inertie).
        
        Args:
            inertia: Moment d'inertie
        
        Returns:
            Score [0, 1]
        """
        # Score basé sur la variation relative (simplifié)
        # En pratique, nécessiterait un historique pour calculer la variation
        if inertia < 0.01:
            return 0.0
        elif inertia < 0.05:
            return 0.5
        else:
            return 1.0
    
    def _score_distance_to_ground(self, distance_y: float) -> float:
        """
        Score de distance au sol (basé sur coordonnée y du centre de masse).
        
        Args:
            distance_y: Coordonnée y du centre de masse
        
        Returns:
            Score [0, 1]
        """
        # Plus y est grand (proche du bas en MediaPipe), plus le score est élevé
        if distance_y < 0.3:
            return 0.0
        elif distance_y < 0.6:
            return 0.5
        else:
            return 1.0
    
    def _calculate_weighted_score(self, scores: dict) -> float:
        """
        Calcule le score de confiance pondéré.
        
        Formule: Score_chute = ∑ w_i * s_i
        
        Poids:
        - w_vitesse = 0.35 (Srikongtham et al.)
        - w_accélération = 0.25 (Bourke et al.)
        - w_angle = 0.25 (Noury et al.)
        - w_inertie = 0.10
        - w_distance = 0.05
        
        Args:
            scores: Dictionnaire des scores individuels
        
        Returns:
            Score pondéré [0, 1]
        """
        weighted_score = (
            WEIGHTS_FALL_CONFIDENCE["vertical_velocity"] * scores["vertical_velocity"] +
            WEIGHTS_FALL_CONFIDENCE["acceleration"] * scores["acceleration"] +
            WEIGHTS_FALL_CONFIDENCE["trunk_angle"] * scores["trunk_angle"] +
            WEIGHTS_FALL_CONFIDENCE["inertia"] * scores["inertia"] +
            WEIGHTS_FALL_CONFIDENCE["distance_to_ground"] * scores["distance_to_ground"]
        )
        
        return weighted_score
    
    def _update_state_machine(
        self, 
        state: PhysicsState, 
        current_time: float, 
        confidence_score: float,
        scores: dict,
        criteria_triggered: List[str]
    ) -> FallDetectionResult:
        """
        Met à jour la machine à états.
        
        Transitions:
        NO_FALL → SUSPECTED: si ≥ 2 critères et score > 0.5
        SUSPECTED → CONFIRMED: si immobilité détectée après délai
        SUSPECTED → FALSE_ALARM: si récupération détectée
        CONFIRMED → NO_FALL: reset après traitement
        
        Args:
            state: État physique
            current_time: Timestamp actuel
            confidence_score: Score de confiance
            scores: Scores individuels
            criteria_triggered: Critères déclenchés
        
        Returns:
            FallDetectionResult
        """
        result = FallDetectionResult(
            status=self.current_status,
            confidence_score=confidence_score,
            timestamp=current_time,
            vertical_velocity_score=scores["vertical_velocity"],
            acceleration_score=scores["acceleration"],
            trunk_angle_score=scores["trunk_angle"],
            inertia_score=scores["inertia"],
            distance_to_ground_score=scores["distance_to_ground"],
            criteria_triggered=criteria_triggered
        )
        
        # Transition NO_FALL → SUSPECTED
        if self.current_status == FallStatus.NO_FALL:
            if self.criteria_count >= 2 and confidence_score > 0.5:
                self.current_status = FallStatus.SUSPECTED
                self.suspicion_start_time = current_time
                self.post_impact_history.clear()
                result.status = FallStatus.SUSPECTED
        
        # Transition SUSPECTED → CONFIRMED ou FALSE_ALARM
        elif self.current_status == FallStatus.SUSPECTED:
            elapsed_time = current_time - self.suspicion_start_time
            
            if elapsed_time >= self.observation_delay:
                if result.is_immobile:
                    self.current_status = FallStatus.CONFIRMED
                    result.status = FallStatus.CONFIRMED
                elif result.is_recovering:
                    self.current_status = FallStatus.FALSE_ALARM
                    result.status = FallStatus.FALSE_ALARM
        
        # Reset après confirmation
        elif self.current_status == FallStatus.CONFIRMED:
            # Reset après un certain temps (à implémenter par l'appelant)
            pass
        
        return result
    
    def _analyze_post_impact(self, state: PhysicsState, result: FallDetectionResult):
        """
        Niveau 3: Analyse post-impact (immobilité vs récupération).
        
        Formule variance: σ² = Var(x) + Var(y) = (1/n)∑(x_i - x̄)² + (1/n)∑(y_i - ȳ)²
        Seuil immobilité: σ² < 0.01 m²
        
        Détection redressement: Δθ = θ_final - θ_initial < -15°
        
        Args:
            state: État physique actuel
            result: Résultat à mettre à jour
        """
        # Ajouter position actuelle à l'historique
        com_x, com_y = state.center_of_mass[0], state.center_of_mass[1]
        self.post_impact_history.append((state.timestamp, (com_x, com_y)))
        
        # Calculer la variance de position
        if len(self.post_impact_history) >= 10:  # Minimum 10 frames
            variance = self._calculate_position_variance()
            result.immobility_variance = variance
            result.is_immobile = variance < THRESHOLD_IMMOBILITY_VARIANCE
            
            # Temps d'immobilité
            if result.is_immobile:
                first_time = self.post_impact_history[0][0]
                current_time = state.timestamp
                result.immobility_time = current_time - first_time
                result.is_immobile = result.immobility_time >= THRESHOLD_IMMOBILITY_TIME
        
        # Détection de récupération (redressement)
        if len(self.post_impact_history) >= 30:  # ~1 seconde de données
            trunk_angle_change = self._calculate_trunk_angle_change(state.trunk_angle)
            result.trunk_angle_change = trunk_angle_change
            
            # Redressement détecté si l'angle diminue de plus de 15°
            if trunk_angle_change < -15.0:
                result.is_recovering = True
    
    def _calculate_position_variance(self) -> float:
        """
        Calcule la variance de position pour l'immobilité.
        
        Formule: σ² = Var(x) + Var(y) = (1/n)∑(x_i - x̄)² + (1/n)∑(y_i - ȳ)²
        
        Returns:
            Variance totale
        """
        if len(self.post_impact_history) < 2:
            return float('inf')
        
        positions = [pos for _, pos in self.post_impact_history]
        x_values = [pos[0] for pos in positions]
        y_values = [pos[1] for pos in positions]
        
        # Moyennes
        mean_x = sum(x_values) / len(x_values)
        mean_y = sum(y_values) / len(y_values)
        
        # Variances
        var_x = sum((x - mean_x) ** 2 for x in x_values) / len(x_values)
        var_y = sum((y - mean_y) ** 2 for y in y_values) / len(y_values)
        
        return var_x + var_y
    
    def _calculate_trunk_angle_change(self, current_angle: float) -> float:
        """
        Calcule le changement d'angle du tronc pour détecter le redressement.
        
        Formule: Δθ = θ_final - θ_initial
        
        Args:
            current_angle: Angle actuel du tronc
        
        Returns:
        Changement d'angle en degrés
        """
        if len(self.post_impact_history) < 30:
            return 0.0
        
        # Angle initial (début de la fenêtre)
        # Note: en pratique, il faudrait stocker les angles dans l'historique
        # Ici, on utilise une approximation basée sur le temps
        initial_angle = current_angle  # Placeholder
        
        return current_angle - initial_angle
    
    def reset(self):
        """Réinitialise le détecteur à l'état NO_FALL."""
        self.current_status = FallStatus.NO_FALL
        self.suspicion_start_time = None
        self.post_impact_history.clear()
        self.criteria_count = 0
    
    def get_status(self) -> FallStatus:
        """Retourne l'état actuel du détecteur."""
        return self.current_status
