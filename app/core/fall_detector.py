"""
Détecteur de chute hiérarchique à 3 niveaux.
N1: Seuils physiques | N2: Score confiance | N3: Analyse post-impact
"""

import time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import numpy as np

from app.config import settings, FALL_CONFIDENCE_WEIGHTS, PROFILE_CONFIG
from app.core.physics_engine import PhysicsEngine, PhysicsState, PoseData


class FallStatus(Enum):
    NO_FALL = "no_fall"
    SUSPECTED = "suspected"
    CONFIRMED = "confirmed"
    FALSE_ALARM = "false_alarm"


@dataclass
class FallDetectionResult:
    """Résultat structuré de la détection."""
    status: FallStatus
    confidence_score: float           # 0.0 - 1.0
    physics_state: PhysicsState
    timestamp: float
    suspicion_duration: float = 0.0    # secondes depuis suspicion
    post_impact_time: float = 0.0      # secondes depuis impact
    details: Dict = field(default_factory=dict)


class FallDetector:
    """
    Détecteur hiérarchique à 3 niveaux :
    
    NIVEAU 1 - Seuils physiques (rapide, filtrage) :
        • Accélération résultante > 3g (Bourke)
        • Angle tronc > 60° (Wu)
        • Vitesse verticale < -2.5 m/s (Srikongtham)
        • Chute libre détectée
    
    NIVEAU 2 - Score de confiance (pondération) :
        • Combinaison pondérée des critères physiques
        • Seuil : 0.75 pour passage au niveau 3
    
    NIVEAU 3 - Analyse post-impact (confirmation) :
        • Immobilité (variance position < 0.01 m²)
        • Temps au sol (adapté au profil)
        • Détection de récupération (redressement)
    """
    
    def __init__(self, profile_type: str = "senior_autonome", 
                 frame_rate: int = None):
        self.physics_engine = PhysicsEngine(frame_rate=frame_rate)
        
        # Configuration selon le profil
        self.profile = PROFILE_CONFIG.get(profile_type, PROFILE_CONFIG["senior_autonome"])
        
        # Machine à états
        self.status = FallStatus.NO_FALL
        self.suspicion_start: Optional[float] = None
        self.impact_time: Optional[float] = None
        
        # Buffers d'analyse
        self.suspicion_buffer: deque = deque(maxlen=30)      # 1s de suspicion
        self.post_impact_buffer: deque = deque(maxlen=90)     # 3s post-impact
        self.position_history: deque = deque(maxlen=90)       # Positions pour variance
        
        # Seuils
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
    
    def process(self, pose: PoseData) -> FallDetectionResult:
        """
        Traite un frame et détermine s'il y a chute.
        
        Returns:
            FallDetectionResult avec statut et métadonnées
        """
        current_time = time.time()
        
        # ─── ÉTAPE 1 : Calculs physiques ───
        physics = self.physics_engine.process(pose)
        
        # ─── ÉTAPE 2 : NIVEAU 1 - Seuils physiques ───
        level1 = self._level1_threshold_check(physics)
        
        if not level1["suspicion"]:
            # Pas de suspicion : réinitialiser et retourner
            self._reset_state()
            return FallDetectionResult(
                status=FallStatus.NO_FALL,
                confidence_score=0.0,
                physics_state=physics,
                timestamp=current_time,
                details={"level1_flags": level1}
            )
        
        # ─── Suspicion détectée ───
        if self.suspicion_start is None:
            self.suspicion_start = current_time
        
        suspicion_duration = current_time - self.suspicion_start
        self.suspicion_buffer.append(physics)
        
        # ─── ÉTAPE 3 : NIVEAU 2 - Score de confiance ───
        confidence = self._calculate_confidence(physics, level1)
        
        if confidence < self.confidence_threshold:
            # Confiance insuffisante : maintenir suspicion
            return FallDetectionResult(
                status=FallStatus.SUSPECTED,
                confidence_score=confidence,
                physics_state=physics,
                timestamp=current_time,
                suspicion_duration=suspicion_duration,
                details={
                    "level1_flags": level1,
                    "waiting_for": "higher_confidence"
                }
            )
        
        # ─── Confiance suffisante : passage NIVEAU 3 ───
        if self.impact_time is None:
            self.impact_time = current_time
        
        self.post_impact_buffer.append(physics)
        self.position_history.append(physics.center_of_mass)
        
        post_impact_time = current_time - self.impact_time
        
        # ─── ÉTAPE 4 : NIVEAU 3 - Analyse post-impact ───
        analysis = self._analyze_post_impact(post_impact_time)
        
        if analysis["confirmed"]:
            self.status = FallStatus.CONFIRMED
            return FallDetectionResult(
                status=FallStatus.CONFIRMED,
                confidence_score=confidence,
                physics_state=physics,
                timestamp=current_time,
                suspicion_duration=suspicion_duration,
                post_impact_time=post_impact_time,
                details={
                    "level1_flags": level1,
                    "post_impact": analysis,
                    "time_to_detection_ms": int((current_time - self.suspicion_start) * 1000)
                }
            )
        
        if analysis["false_alarm"]:
            self._reset_state()
            return FallDetectionResult(
                status=FallStatus.FALSE_ALARM,
                confidence_score=confidence,
                physics_state=physics,
                timestamp=current_time,
                details={"reason": analysis["reason"]}
            )
        
        # En attente de plus de données
        return FallDetectionResult(
            status=FallStatus.SUSPECTED,
            confidence_score=confidence,
            physics_state=physics,
            timestamp=current_time,
            suspicion_duration=suspicion_duration,
            post_impact_time=post_impact_time,
            details={"waiting_for": "post_impact_confirmation"}
        )
    
    # ═══════════════════════════════════════════════════════
    # NIVEAU 1 : SEUILS PHYSIQUES
    # ═══════════════════════════════════════════════════════
    
    def _level1_threshold_check(self, p: PhysicsState) -> Dict:
        """
        Vérification rapide par seuils physiques.
        Suspicion si ≥ 2 critères parmi 4.
        """
        flags = {
            "high_acceleration": p.resultant_acceleration > settings.FALL_ACCEL_THRESHOLD * settings.GRAVITY,
            "trunk_inclined": p.trunk_angle > settings.FALL_TRUNK_ANGLE_THRESHOLD,
            "high_vertical_speed": p.vertical_velocity < settings.FALL_VERTICAL_VELOCITY_THRESHOLD,
            "free_fall": p.is_free_fall,
            "ground_contact": p.is_ground_contact,
            "criteria_met": 0,
            "suspicion": False
        }
        
        flags["criteria_met"] = sum([
            flags["high_acceleration"],
            flags["trunk_inclined"],
            flags["high_vertical_speed"],
            flags["free_fall"]
        ])
        
        # Suspicion : au moins 2 critères OU chute libre + contact sol
        flags["suspicion"] = (
            flags["criteria_met"] >= 2 or 
            (flags["free_fall"] and flags["ground_contact"])
        )
        
        return flags
    
    # ═══════════════════════════════════════════════════════
    # NIVEAU 2 : SCORE DE CONFIANCE
    # ═══════════════════════════════════════════════════════
    
    def _calculate_confidence(self, p: PhysicsState, flags: Dict) -> float:
        """
        Score de confiance pondéré.
        Score = Σ(w_i × s_i)
        """
        scores = {
            "vertical_velocity": self._score_velocity(p.vertical_velocity),
            "acceleration": self._score_acceleration(p.resultant_acceleration),
            "trunk_angle": self._score_angle(p.trunk_angle),
            "inertia": self._score_inertia(p.moment_of_inertia),
            "distance_to_ground": self._score_distance(p.distance_to_ground)
        }
        
        confidence = sum(
            FALL_CONFIDENCE_WEIGHTS[key] * scores[key]
            for key in FALL_CONFIDENCE_WEIGHTS
        )
        
        return min(confidence, 1.0)
    
    def _score_velocity(self, vy: float) -> float:
        """Score vitesse verticale (descendante = élevé)."""
        if vy < -4.0: return 1.0
        if vy < -2.5: return 0.8
        if vy < -1.5: return 0.5
        if vy < 0: return 0.2
        return 0.0
    
    def _score_acceleration(self, a: float) -> float:
        """Score accélération (impact = élevé)."""
        threshold = settings.FALL_ACCEL_THRESHOLD * settings.GRAVITY
        if a > threshold * 2: return 1.0
        if a > threshold: return 0.8
        if a > threshold * 0.5: return 0.4
        return 0.0
    
    def _score_angle(self, theta: float) -> float:
        """Score angle du tronc (incliné = élevé)."""
        if theta > 80: return 1.0
        if theta > 60: return 0.8
        if theta > 45: return 0.5
        if theta > 30: return 0.2
        return 0.0
    
    def _score_inertia(self, inertia: float) -> float:
        """Score moment d'inertie (variation = élevé)."""
        # Simplifié : valeur fixe, à améliorer avec historique
        return 0.5
    
    def _score_distance(self, dist: float) -> float:
        """Score distance au sol (proche = élevé)."""
        if dist < 0.1: return 1.0
        if dist < 0.3: return 0.5
        return 0.0
    
    # ═══════════════════════════════════════════════════════
    # NIVEAU 3 : ANALYSE POST-IMPACT
    # ═══════════════════════════════════════════════════════
    
    def _analyze_post_impact(self, time_on_ground: float) -> Dict:
        """
        Détermine si la chute est confirmée ou fausse alerte.
        """
        result = {
            "confirmed": False,
            "false_alarm": False,
            "reason": "",
            "variance": 0.0,
            "recovery_detected": False,
            "time_on_ground": time_on_ground
        }
        
        # Besoin d'au moins 1 seconde de données
        if len(self.position_history) < 30:
            return result
        
        # 1. Variance de position (immobilité)
        positions = list(self.position_history)
        variance = self._calculate_position_variance(positions)
        result["variance"] = variance
        
        # 2. Détection de récupération
        recovery = self._detect_recovery()
        result["recovery_detected"] = recovery
        
        # ─── Décision ───
        
        # Si récupération rapide → fausse alerte
        if recovery and time_on_ground < 5.0:
            result["false_alarm"] = True
            result["reason"] = "Récupération rapide détectée (< 5s)"
            return result
        
        # Si immobile trop longtemps → confirmation
        is_immobile = variance < settings.IMMOBILITY_VARIANCE_THRESHOLD
        immobility_threshold = self.profile["immobility_threshold"]
        
        if is_immobile and time_on_ground > immobility_threshold:
            result["confirmed"] = True
            result["reason"] = f"Immobilité confirmée ({time_on_ground:.1f}s)"
            return result
        
        # Si temps max d'observation dépassé → confirmation
        max_observation = self.profile["delay_observation"] + 5  # Marge de 5s
        if time_on_ground > max_observation:
            result["confirmed"] = True
            result["reason"] = f"Temps d'observation maximal dépassé ({time_on_ground:.1f}s)"
            return result
        
        return result
    
    def _calculate_position_variance(self, positions: List[Tuple[float, float]]) -> float:
        """Variance des positions pour détecter l'immobilité."""
        if len(positions) < 2:
            return float('inf')
        
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        
        return np.var(xs) + np.var(ys)
    
    def _detect_recovery(self) -> bool:
        """Détecte les mouvements de redressement."""
        if len(self.post_impact_buffer) < 10:
            return False
        
        # Analyse de la tendance de l'angle du tronc
        recent_angles = [state.trunk_angle for state in list(self.post_impact_buffer)[-10:]]
        
        if len(recent_angles) >= 2:
            delta = recent_angles[-1] - recent_angles[0]
            # Diminution de l'angle = redressement
            if delta < -15:
                return True
        
        # TODO: Analyser les mouvements des bras et jambes
        
        return False
    
    def _reset_state(self):
        """Réinitialise la machine à états."""
        self.status = FallStatus.NO_FALL
        self.suspicion_start = None
        self.impact_time = None
        self.suspicion_buffer.clear()
        self.post_impact_buffer.clear()
        self.position_history.clear()
        self.physics_engine.reset()
    
    def set_profile(self, profile_type: str):
        """
        Change le profil utilisateur.
        
        Args:
            profile_type: Nouveau type de profil
        """
        self.profile = PROFILE_CONFIG.get(profile_type, PROFILE_CONFIG["senior_autonome"])
        self._reset_state()
    
    def reset(self):
        """Réinitialise le détecteur."""
        self._reset_state()
    
    def get_status(self) -> FallStatus:
        """Retourne l'état actuel."""
        return self.status
