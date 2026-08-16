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
