"""
Calculateur de score de gravité des chutes.
Modèle multi-critères pondéré avec adaptation au profil.
"""

from typing import Dict, Tuple
from dataclasses import dataclass
from enum import Enum

from app.config import PROFILE_CONFIG, GRAVITY_LEVELS


class GravityLevel(Enum):
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"


@dataclass
class GravityResult:
    """Résultat du scoring de gravité."""
    score: float                    # 0-100
    level: GravityLevel
    details: Dict[str, float]       # Scores par critère


class GravityScorer:
    """
    Calculateur de gravité basé sur 4 critères pondérés :
    
    1. INTENSITÉ (I) : Vitesse d'impact
       → Énergie cinétique dissipée, force du choc
    
    2. TEMPS AU SOL (T) : Durée d'immobilité
       → Incapacité à se relever, risque d'aggravation
    
    3. PROBABILITÉ DE BLESSURE (B) : Facteurs de risque
       → Âge, partie touchée, posture, immobilité
    
    4. RÉACTIVITÉ (R) : Mouvements post-chute
       → Conscience, capacité à réagir
    """
    
    def __init__(self, profile_type: str = "senior_autonome"):
        self.profile = PROFILE_CONFIG.get(profile_type, PROFILE_CONFIG["senior_autonome"])
        self.weights = self.profile["gravity_time_weights"]
    
    def calculate(self,
                  impact_velocity: float,           # m/s
                  time_on_ground: float,             # secondes
                  age: int = 70,
                  body_part_hit: str = "unknown",
                  posture_on_ground: str = "unknown",
                  trunk_angle: float = 90.0,
                  post_fall_movement: str = "none") -> GravityResult:
        """
        Calcule le score de gravité complet.
        """
        # ─── 4 Scores individuels ───
        intensity = self._score_intensity(impact_velocity)
        time_score = self._score_time_on_ground(time_on_ground)
        injury = self._score_injury_probability(age, body_part_hit, 
                                                  posture_on_ground, trunk_angle)
        reactivity = self._score_reactivity(post_fall_movement)
        
        # ─── Score global pondéré ───
        total = (
            self.weights["intensity"] * intensity +
            self.weights["time_on_ground"] * time_score +
            self.weights["injury_probability"] * injury +
            self.weights["reactivity"] * reactivity
        )
        
        # ─── Niveau de gravité ───
        level = self._get_level(total)
        
        return GravityResult(
            score=round(total, 2),
            level=level,
            details={
                "intensity": round(intensity, 2),
                "time_on_ground": round(time_score, 2),
                "injury_probability": round(injury, 2),
                "reactivity": round(reactivity, 2)
            }
        )
    
    def _score_intensity(self, impact_velocity: float) -> float:
        """
        Score d'intensité basé sur la vitesse d'impact.
        Plus la vitesse est élevée → plus le choc est violent.
        """
        if impact_velocity > 5.0:
            return 90.0   # Impact très violent
        elif impact_velocity > 3.0:
            return 60.0   # Impact élevé
        elif impact_velocity > 1.5:
            return 30.0   # Impact modéré
        else:
            return 10.0   # Impact faible
    
    def _score_time_on_ground(self, time_on_ground: float) -> float:
        """
        Score basé sur le temps passé immobile au sol.
        Plus le temps est long → plus la situation est grave.
        """
        if time_on_ground > 60:
            return 100.0  # Immobilisation totale > 1 min
        elif time_on_ground > 30:
            return 80.0   # Incapacité probable
        elif time_on_ground > 15:
            return 55.0   # Difficulté à se relever
        elif time_on_ground > 5:
            return 25.0   # Hésitation
        else:
            return 5.0    # Récupération rapide
    
    def _score_injury_probability(self, age: int, body_part: str,
                                   posture: str, trunk_angle: float) -> float:
        """
        Score de probabilité de blessure.
        Somme de facteurs de risque.
        """
        score = 0.0
        
        # Âge (plus âgé = plus fragile)
        if age > 80:
            score += 20
        elif age > 65:
            score += 10
        
        # Partie du corps touchée en premier
        body_scores = {
            "tete": 40,        # Traumatisme crânien = très grave
            "hanche": 20,      # Fracture de hanche classique senior
            "epaule": 15,
            "genou": 10,
            "main": 5,
            "coude": 5,
            "pied": 3,
            "unknown": 15
        }
        score += body_scores.get(body_part, 15)
        
        # Posture au sol
        posture_scores = {
            "face_contre_terre": 30,   # Risque d'asphyxie
            "sur_le_cote": 15,
            "sur_le_dos": 10,
            "accroupi": 5,
            "unknown": 15
        }
        score += posture_scores.get(posture, 15)
        
        # Immobilité (angle du tronc stable = immobile)
        if trunk_angle > 80:
            score += 30   # Complètement immobile
        elif trunk_angle > 60:
            score += 15   # Peu mobile
        
        return min(score, 100.0)
    
    def _score_reactivity(self, movement: str) -> float:
        """
        Score de réactivité post-chute.
        Plus le score est élevé = MOINS de réactivité = PLUS grave.
        """
        movement_scores = {
            "redressement_rapide": 10,     # Se relève vite = bon signe
            "mouvements_bras": 40,          # Bouge mais ne se relève pas
            "mouvements_faibles": 60,       # Mouvements limités
            "aucun_mouvement": 90,          # Inconscience probable
            "convulsions": 100,             # Crise épileptique / AVC
            "none": 90
        }
        return movement_scores.get(movement, 90)
    
    def _get_level(self, score: float) -> GravityLevel:
        """Détermine le niveau de gravité selon le score."""
        if score >= 76:
            return GravityLevel.CRITIQUE
        elif score >= 51:
            return GravityLevel.ELEVEE
        elif score >= 26:
            return GravityLevel.MOYENNE
        else:
            return GravityLevel.FAIBLE
