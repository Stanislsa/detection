"""Catalogue des 21 indicateurs (motion, appearance, dynamics)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass(frozen=True)
class Indicator:
    id: str
    name: str
    family: str
    description: str
    range_hint: str

INDICATORS: Tuple[Indicator, ...] = (
    Indicator("motion_mean", "Mouvement moyen", "motion", "Moyenne |diff| frames", "0-255"),
    Indicator("motion_max", "Mouvement max", "motion", "Pic de mouvement", "0-255"),
    Indicator("motion_std", "Variance mouvement", "motion", "Instabilite", ">=0"),
    Indicator("motion_energy", "Energie mouvement", "motion", "Intensite cumulee", ">=0"),
    Indicator("optical_flow_mag", "Flux optique proxy", "motion", "Gradient spatial moyen", ">=0"),
    Indicator("luma_mean", "Luminosite moyenne", "appearance", "Niveau de gris moyen", "0-255"),
    Indicator("luma_std", "Contraste", "appearance", "Ecart-type luminosite", ">=0"),
    Indicator("luma_min", "Luminosite min", "appearance", "Zone sombre", "0-255"),
    Indicator("luma_max", "Luminosite max", "appearance", "Zone claire", "0-255"),
    Indicator("edge_density", "Densite contours", "appearance", "Proportion Canny", "0-1"),
    Indicator("hist_b0", "Hist bin0", "appearance", "Pixels tres sombres", "0-1"),
    Indicator("hist_b1", "Hist bin1", "appearance", "Pixels sombres", "0-1"),
    Indicator("hist_b2", "Hist bin2", "appearance", "Pixels mi-sombres", "0-1"),
    Indicator("hist_b3", "Hist bin3", "appearance", "Pixels moyens-bas", "0-1"),
    Indicator("hist_b4", "Hist bin4", "appearance", "Pixels moyens-hauts", "0-1"),
    Indicator("hist_b5", "Hist bin5", "appearance", "Pixels clairs", "0-1"),
    Indicator("hist_b6", "Hist bin6", "appearance", "Pixels tres clairs", "0-1"),
    Indicator("hist_b7", "Hist bin7", "appearance", "Pixels satures", "0-1"),
    Indicator("n_frames", "Nombre frames", "dynamics", "Longueur clip", ">=1"),
    Indicator("motion_trend", "Tendance mouvement", "dynamics", "Pente / acceleration", "reel"),
    Indicator("stillness_ratio", "Ratio immobilite", "dynamics", "Fraction frames calmes", "0-1"),
    # --- Features squelette (MediaPipe) — apprentissage aligné détection live ---
    Indicator("sk_trunk_angle_mean", "Angle tronc moyen", "skeleton", "Inclinaison moyenne 0-90", "0-90"),
    Indicator("sk_trunk_angle_max", "Angle tronc max", "skeleton", "Pic d inclinaison", "0-90"),
    Indicator("sk_trunk_angle_std", "Variance angle tronc", "skeleton", "Variabilite posture", ">=0"),
    Indicator("sk_trunk_angle_final", "Angle tronc final", "skeleton", "Posture en fin de clip", "0-90"),
    Indicator("sk_vertical_speed_max", "Vitesse verticale max", "skeleton", "Pic chute (hanches)", ">=0"),
    Indicator("sk_vertical_speed_mean", "Vitesse verticale moy", "skeleton", "Dynamique verticale", ">=0"),
    Indicator("sk_impact_proxy", "Impact proxy", "skeleton", "Variation brutale de vitesse", ">=0"),
    Indicator("sk_horizontal_ratio", "Ratio horizontal", "skeleton", "Fraction frames au sol", "0-1"),
    Indicator("sk_time_on_ground_proxy", "Temps au sol proxy", "skeleton", "Duree horizontalite", "s"),
    Indicator("sk_stillness_landmarks", "Immobilite squelette", "skeleton", "Faible mouvement landmarks", "0-1"),
    Indicator("sk_hip_drop", "Descente hanches", "skeleton", "Delta y hanche debut-fin", "reel"),
    Indicator("sk_head_hip_delta_y", "Tete vs hanche", "skeleton", "Alignement tete-hanche", "reel"),
    Indicator("sk_pose_visibility", "Visibilite pose", "skeleton", "Confiance landmarks moy", "0-1"),
    Indicator("sk_frames_with_pose", "Frames avec pose", "skeleton", "Nb frames pose detectee", ">=0"),
    Indicator("sk_person_detected_ratio", "Ratio pose/frames", "skeleton", "Couverture pose du clip", "0-1"),
)
INDICATOR_IDS: List[str] = [i.id for i in INDICATORS]
INDICATOR_BY_ID: Dict[str, Indicator] = {i.id: i for i in INDICATORS}

def indicators_by_family():
    out = {}
    for ind in INDICATORS:
        out.setdefault(ind.family, []).append(ind)
    return out

def catalog_as_dict():
    return [{"id": i.id, "name": i.name, "family": i.family,
             "description": i.description, "range_hint": i.range_hint} for i in INDICATORS]
