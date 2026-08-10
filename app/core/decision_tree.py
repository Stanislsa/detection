"""
Arbre de décision global.
Orchestre PhysicsEngine → FallDetector → GravityScorer → Persistance → Alerte.
"""

import time
from typing import Optional, Dict, Callable
from dataclasses import dataclass
import logging

from app.config import settings, PROFILE_CONFIG
from app.core.physics_engine import PhysicsEngine, PoseData
from app.core.fall_detector import FallDetector, FallStatus, FallDetectionResult
from app.core.gravity_scorer import GravityScorer, GravityLevel, GravityResult

logger = logging.getLogger(__name__)


@dataclass
class DecisionResult:
    """Résultat final de l'arbre de décision."""
    action: str                         # "no_action", "alert", "log_only"
    fall_detected: bool
    gravity_level: Optional[GravityLevel]
    gravity_score: Optional[float]
    alert_channels: list               # ["telegram", "email", "none"]
    message: str
    metadata: Dict


class DecisionTree:
    """
    Cerveau central du système.
    
    Pipeline :
    1. Reçoit les landmarks MediaPipe
    2. Calcule les grandeurs physiques (PhysicsEngine)
    3. Détecte la chute (FallDetector, 3 niveaux)
    4. Si chute confirmée → calcule la gravité (GravityScorer)
    5. Persiste en base de données
    6. Déclenche les alertes appropriées
    """
    
    def __init__(self, person_id: int, camera_id: int, 
                 profile_type: str = "senior_autonome",
                 alert_callback: Optional[Callable] = None):
        self.person_id = person_id
        self.camera_id = camera_id
        self.profile_type = profile_type
        
        # Modules
        self.physics = PhysicsEngine(frame_rate=settings.DEFAULT_FPS)
        self.detector = FallDetector(profile_type=profile_type)
        self.scorer = GravityScorer(profile_type=profile_type)
        
        # Callback pour les alertes
        self.alert_callback = alert_callback
        
        # État
        self.is_fall_in_progress = False
        self.current_fall_data: Optional[Dict] = None
        
        logger.info(f"DecisionTree initialisé pour person_id={person_id}, "
                   f"profile={profile_type}")
    
    def process_frame(self, pose: PoseData) -> DecisionResult:
        """
        Traite un frame et exécute l'arbre de décision complet.
        
        Returns:
            DecisionResult avec l'action à effectuer
        """
        # ─── ÉTAPE 1-3 : Détection de chute ───
        detection = self.detector.process(pose)
        
        # ─── NO FALL ───
        if detection.status == FallStatus.NO_FALL:
            return DecisionResult(
                action="no_action",
                fall_detected=False,
                gravity_level=None,
                gravity_score=None,
                alert_channels=[],
                message="Aucune anomalie détectée",
                metadata={"physics": detection.physics_state.__dict__}
            )
        
        # ─── SUSPECTED ───
        if detection.status == FallStatus.SUSPECTED:
            return DecisionResult(
                action="monitoring",
                fall_detected=False,
                gravity_level=None,
                gravity_score=None,
                alert_channels=[],
                message=f"Suspicion en cours ({detection.suspicion_duration:.1f}s)",
                metadata={
                    "suspicion_duration": detection.suspicion_duration,
                    "post_impact_time": detection.post_impact_time,
                    "confidence": detection.confidence_score
                }
            )
        
        # ─── FALSE ALARM ───
        if detection.status == FallStatus.FALSE_ALARM:
            logger.info(f"Fausse alerte : {detection.details.get('reason')}")
            return DecisionResult(
                action="log_only",
                fall_detected=False,
                gravity_level=None,
                gravity_score=None,
                alert_channels=[],
                message=f"Fausse alerte : {detection.details.get('reason')}",
                metadata={"reason": detection.details.get("reason")}
            )
        
        # ─── CONFIRMED FALL ───
        if detection.status == FallStatus.CONFIRMED:
            return self._handle_confirmed_fall(detection)
        
        # Cas impossible
        return DecisionResult(
            action="error",
            fall_detected=False,
            gravity_level=None,
            gravity_score=None,
            alert_channels=[],
            message="Statut inconnu",
            metadata={"status": detection.status.value}
        )
    
    def _handle_confirmed_fall(self, detection: FallDetectionResult) -> DecisionResult:
        """
        Gère une chute confirmée : scoring de gravité + décision d'alerte.
        """
        physics = detection.physics_state
        
        # ─── ÉTAPE 4 : Scoring de gravité ───
        # Détection de la partie touchée (simplifié : plus bas point)
        body_part = self._detect_impact_body_part(physics)
        
        # Détection de la posture
        posture = self._detect_posture(physics)
        
        # Détection du mouvement post-chute
        movement = self._detect_post_fall_movement(detection)
        
        gravity = self.scorer.calculate(
            impact_velocity=abs(physics.vertical_velocity),
            time_on_ground=detection.post_impact_time,
            age=70,  # TODO: récupérer depuis le profil
            body_part_hit=body_part,
            posture_on_ground=posture,
            trunk_angle=physics.trunk_angle,
            post_fall_movement=movement
        )
        
        # ─── ÉTAPE 5-6 : Décision d'alerte selon le niveau ───
        alert_channels = []
        action = "log_only"
        message = ""
        
        if gravity.level == GravityLevel.FAIBLE:
            action = "log_only"
            message = "Chute détectée mais gravité faible"
            
        elif gravity.level == GravityLevel.MOYENNE:
            action = "alert"
            alert_channels = ["telegram"]  # Notification légère
            message = f"Chute de gravité moyenne détectée (score: {gravity.score})"
            
        elif gravity.level == GravityLevel.ELEVEE:
            action = "alert"
            alert_channels = ["telegram", "email"]
            message = f"Chute de gravité élevée détectée (score: {gravity.score})"
            
        elif gravity.level == GravityLevel.CRITIQUE:
            action = "alert"
            alert_channels = ["telegram", "email"]
            message = f"🚨 CHUTE CRITIQUE DÉTECTÉE (score: {gravity.score}) - SECOURS RECOMMANDÉS"
        
        # ─── Métadonnées complètes ───
        metadata = {
            "detection": detection.details,
            "gravity": gravity.details,
            "physics": {
                "impact_velocity": abs(physics.vertical_velocity),
                "max_acceleration": physics.resultant_acceleration,
                "trunk_angle": physics.trunk_angle,
                "time_on_ground": detection.post_impact_time
            },
            "body_part": body_part,
            "posture": posture,
            "movement": movement
        }
        
        # ─── Callback d'alerte ───
        if action == "alert" and self.alert_callback:
            self.alert_callback(
                person_id=self.person_id,
                camera_id=self.camera_id,
                gravity=gravity,
                message=message,
                channels=alert_channels
            )
        
        logger.warning(f"CHUTE CONFIRMÉE - Niveau: {gravity.level.value}, "
                      f"Score: {gravity.score}, Canaux: {alert_channels}")
        
        return DecisionResult(
            action=action,
            fall_detected=True,
            gravity_level=gravity.level,
            gravity_score=gravity.score,
            alert_channels=alert_channels,
            message=message,
            metadata=metadata
        )
    
    def _detect_impact_body_part(self, physics: 'PhysicsState') -> str:
        """
        Détecte la partie du corps touchée en premier.
        Heuristique : le point le plus bas au moment de l'impact.
        """
        # Simplifié : analyse de la distance au sol
        if physics.distance_to_ground < 0.05:
            # Très proche du sol = chute sur le haut du corps
            if physics.trunk_angle > 70:
                return "tete" if physics.trunk_angle > 85 else "epaule"
            return "hanche"
        return "unknown"
    
    def _detect_posture(self, physics: 'PhysicsState') -> str:
        """
        Détecte la posture au sol.
        """
        angle = physics.trunk_angle
        
        if angle > 85:
            return "face_contre_terre"
        elif angle > 45:
            return "sur_le_cote"
        elif angle > 15:
            return "sur_le_dos"
        else:
            return "accroupi"
    
    def _detect_post_fall_movement(self, detection: FallDetectionResult) -> str:
        """
        Détecte le type de mouvement post-chute.
        """
        details = detection.details.get("post_impact", {})
        
        if details.get("recovery_detected"):
            return "redressement_rapide"
        
        # Analyser la variance pour détecter les mouvements
        variance = details.get("variance", 0)
        
        if variance > 0.05:
            return "mouvements_bras"
        elif variance > 0.01:
            return "mouvements_faibles"
        
        return "aucun_mouvement"
    
    def reset(self):
        """Réinitialise l'arbre de décision."""
        self.physics.reset()
        self.detector._reset_state()
        self.is_fall_in_progress = False
        self.current_fall_data = None
