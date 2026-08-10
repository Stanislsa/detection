"""
Calculateur de Score de Gravité pour les Chutes.

Reference:
- AHP (Analytic Hierarchy Process) for criteria weighting
- Multi-criteria decision analysis
"""

from dataclasses import dataclass, field
from typing import Optional, Dict
from enum import Enum
from datetime import datetime

from config.constants import (
    WEIGHTS_GRAVITY, GRAVITY_LEVELS,
    THRESHOLD_IMPACT_VELOCITY_LOW, THRESHOLD_IMPACT_VELOCITY_MED,
    THRESHOLD_IMPACT_VELOCITY_HIGH, THRESHOLD_TRUNK_ANGLE,
    THRESHOLD_TRUNK_ANGLE_STRONG
)


class GravityLevel(Enum):
    """Niveaux de gravité d'une chute."""
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"


class BodyPart(Enum):
    """Parties du corps potentiellement touchées."""
    TETE = "tete"
    HANCHE = "hanche"
    EPAULE = "epaule"
    GENOU = "genou"
    MAIN = "main"
    AUTRE = "autre"


class Posture(Enum):
    """Posture après la chute."""
    FACE_CONTRE_TERRE = "face_contre_terre"
    COTE = "cote"
    DOS = "dos"
    DEBOUT = "debout"
    INCONNUE = "inconnue"


class Reactivity(Enum):
    """Niveau de réactivité post-chute."""
    REDRESSEMENT_RAPIDE = "redressement_rapide"
    MOUVEMENTS_BRAS = "mouvements_bras"
    MOUVEMENTS_FAIBLES = "mouvements_faibles"
    AUCUN_MOUVEMENT = "aucun_mouvement"
    CONVULSIONS = "convulsions"


@dataclass
class GravityResult:
    """Résultat du calcul de gravité."""
    score: float  # Score global [0, 100]
    level: GravityLevel
    timestamp: float
    
    # Scores individuels
    intensity_score: float = 0.0
    time_on_ground_score: float = 0.0
    injury_probability_score: float = 0.0
    reactivity_score: float = 0.0
    
    # Détails par critère
    impact_velocity: float = 0.0
    time_on_ground: float = 0.0
    age: Optional[int] = None
    body_part: Optional[BodyPart] = None
    posture: Optional[Posture] = None
    trunk_angle: float = 0.0
    reactivity: Optional[Reactivity] = None
    
    # Métadonnées
    details: Dict[str, float] = field(default_factory=dict)


class GravityScorer:
    """
    Calculateur de score de gravité multi-critères.
    
    Formule globale:
    Gravity = 0.30*I + 0.35*T + 0.20*B + 0.15*R
    
    Où:
    - I = Score d'intensité (vitesse d'impact)
    - T = Score temps au sol
    - B = Score probabilité de blessure
    - R = Score réactivité post-chute
    """
    
    def __init__(self):
        """Initialise le calculateur de gravité."""
        self.weights = WEIGHTS_GRAVITY
    
    def calculate_gravity(
        self,
        impact_velocity: float,
        time_on_ground: float,
        age: Optional[int] = None,
        body_part: Optional[BodyPart] = None,
        posture: Optional[Posture] = None,
        trunk_angle: float = 0.0,
        reactivity: Optional[Reactivity] = None
    ) -> GravityResult:
        """
        Calcule le score de gravité global.
        
        Args:
            impact_velocity: Vitesse d'impact (m/s)
            time_on_ground: Temps passé au sol (secondes)
            age: Âge de la personne (années)
            body_part: Partie du corps touchée
            posture: Posture après la chute
            trunk_angle: Angle du tronc après chute (degrés)
            reactivity: Niveau de réactivité
        
        Returns:
            GravityResult avec score et niveau
        """
        # Calculer les scores individuels
        intensity_score = self._calculate_intensity_score(impact_velocity)
        time_score = self._calculate_time_on_ground_score(time_on_ground)
        injury_score = self._calculate_injury_probability_score(
            age, body_part, posture, trunk_angle
        )
        reactivity_score = self._calculate_reactivity_score(reactivity)
        
        # Score global pondéré (AHP)
        global_score = (
            self.weights["intensity"] * intensity_score +
            self.weights["time_on_ground"] * time_score +
            self.weights["injury_probability"] * injury_score +
            self.weights["post_fall_reactivity"] * reactivity_score
        )
        
        # Déterminer le niveau de gravité
        level = self._determine_gravity_level(global_score)
        
        # Détails
        details = {
            "intensity": intensity_score,
            "time_on_ground": time_score,
            "injury_probability": injury_score,
            "reactivity": reactivity_score
        }
        
        result = GravityResult(
            score=global_score,
            level=level,
            timestamp=datetime.now().timestamp(),
            intensity_score=intensity_score,
            time_on_ground_score=time_score,
            injury_probability_score=injury_score,
            reactivity_score=reactivity_score,
            impact_velocity=impact_velocity,
            time_on_ground=time_on_ground,
            age=age,
            body_part=body_part,
            posture=posture,
            trunk_angle=trunk_angle,
            reactivity=reactivity,
            details=details
        )
        
        return result
    
    def _calculate_intensity_score(self, impact_velocity: float) -> float:
        """
        Calcule le score d'intensité (fonction échelon).
        
        Formule:
        I(v) = 90 si v > 5.0 m/s
               60 si 3.0 < v ≤ 5.0
               30 si 1.5 < v ≤ 3.0
               10 si v ≤ 1.5
        
        Args:
            impact_velocity: Vitesse d'impact (m/s)
        
        Returns:
            Score d'intensité [0, 100]
        """
        if impact_velocity > THRESHOLD_IMPACT_VELOCITY_HIGH:
            return 90.0
        elif impact_velocity > THRESHOLD_IMPACT_VELOCITY_MED:
            return 60.0
        elif impact_velocity > THRESHOLD_IMPACT_VELOCITY_LOW:
            return 30.0
        else:
            return 10.0
    
    def _calculate_time_on_ground_score(self, time_on_ground: float) -> float:
        """
        Calcule le score temps au sol.
        
        Formule:
        T(t) = 100 si t > 60s
               80  si 30 < t ≤ 60
               55  si 15 < t ≤ 30
               25  si 5 < t ≤ 15
               5   si t ≤ 5
        
        Args:
            time_on_ground: Temps au sol (secondes)
        
        Returns:
            Score temps au sol [0, 100]
        """
        if time_on_ground > 60.0:
            return 100.0
        elif time_on_ground > 30.0:
            return 80.0
        elif time_on_ground > 15.0:
            return 55.0
        elif time_on_ground > 5.0:
            return 25.0
        else:
            return 5.0
    
    def _calculate_injury_probability_score(
        self,
        age: Optional[int],
        body_part: Optional[BodyPart],
        posture: Optional[Posture],
        trunk_angle: float
    ) -> float:
        """
        Calcule le score de probabilité de blessure (somme pondérée).
        
        Formule: B = age_score + body_part_score + posture_score + immobility_score
        
        Args:
            age: Âge de la personne
            body_part: Partie du corps touchée
            posture: Posture après la chute
            trunk_angle: Angle du tronc (degrés)
        
        Returns:
            Score de probabilité de blessure [0, 100]
        """
        score = 0.0
        
        # Score âge
        if age:
            if age > 80:
                score += 20.0
            elif age >= 65:
                score += 10.0
        
        # Score partie du corps
        if body_part:
            body_part_scores = {
                BodyPart.TETE: 40.0,
                BodyPart.HANCHE: 20.0,
                BodyPart.EPAULE: 15.0,
                BodyPart.GENOU: 10.0,
                BodyPart.MAIN: 5.0,
                BodyPart.AUTRE: 2.0
            }
            score += body_part_scores.get(body_part, 0.0)
        
        # Score posture
        if posture:
            posture_scores = {
                Posture.FACE_CONTRE_TERRE: 30.0,
                Posture.COTE: 15.0,
                Posture.DOS: 10.0,
                Posture.DEBOUT: 0.0,
                Posture.INCONNUE: 5.0
            }
            score += posture_scores.get(posture, 0.0)
        
        # Score immobilité (basé sur l'angle du tronc)
        if trunk_angle > THRESHOLD_TRUNK_ANGLE_STRONG:
            score += 30.0
        elif trunk_angle > THRESHOLD_TRUNK_ANGLE:
            score += 15.0
        
        # Plafonner à 100
        return min(score, 100.0)
    
    def _calculate_reactivity_score(self, reactivity: Optional[Reactivity]) -> float:
        """
        Calcule le score de réactivité post-chute.
        
        Formule:
        R = 10  si redressement rapide
          = 40  si mouvements bras
          = 60  si mouvements faibles
          = 90  si aucun mouvement
          = 100 si convulsions
        
        Args:
            reactivity: Niveau de réactivité
        
        Returns:
            Score de réactivité [0, 100]
        """
        if not reactivity:
            return 50.0  # Valeur par défaut si inconnue
        
        reactivity_scores = {
            Reactivity.REDRESSEMENT_RAPIDE: 10.0,
            Reactivity.MOUVEMENTS_BRAS: 40.0,
            Reactivity.MOUVEMENTS_FAIBLES: 60.0,
            Reactivity.AUCUN_MOUVEMENT: 90.0,
            Reactivity.CONVULSIONS: 100.0
        }
        
        return reactivity_scores.get(reactivity, 50.0)
    
    def _determine_gravity_level(self, score: float) -> GravityLevel:
        """
        Détermine le niveau de gravité à partir du score.
        
        Formule:
        - faible: (0, 25]
        - moyenne: (26, 50]
        - élevée: (51, 75]
        - critique: (76, 100]
        
        Args:
            score: Score global [0, 100]
        
        Returns:
            GravityLevel
        """
        for level, (min_score, max_score) in GRAVITY_LEVELS.items():
            if min_score <= score <= max_score:
                return GravityLevel(level.upper())
        
        # Fallback
        if score <= 25:
            return GravityLevel.FAIBLE
        elif score <= 50:
            return GravityLevel.MOYENNE
        elif score <= 75:
            return GravityLevel.ELEVEE
        else:
            return GravityLevel.CRITIQUE
    
    def update_gravity(
        self,
        previous_result: GravityResult,
        new_time_on_ground: float,
        new_reactivity: Optional[Reactivity] = None
    ) -> GravityResult:
        """
        Met à jour le score de gravité avec de nouvelles données.
        
        Utile pour le suivi en temps réel (ex: temps au sol qui augmente).
        
        Args:
            previous_result: Résultat précédent
            new_time_on_ground: Nouveau temps au sol
            new_reactivity: Nouvelle réactivité
        
        Returns:
            GravityResult mis à jour
        """
        return self.calculate_gravity(
            impact_velocity=previous_result.impact_velocity,
            time_on_ground=new_time_on_ground,
            age=previous_result.age,
            body_part=previous_result.body_part,
            posture=previous_result.posture,
            trunk_angle=previous_result.trunk_angle,
            reactivity=new_reactivity or previous_result.reactivity
        )
