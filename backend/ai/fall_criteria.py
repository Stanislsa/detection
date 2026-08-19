"""
Critères formels de décision de chute — alignés CDC SI20220029.

Décision basée sur le squelette MediaPipe (anonymisation), pas sur l'image brute.

Indicateurs :
  - angle du tronc vs horizontal
  - vitesse verticale (m/s estimée)
  - accélération d'impact
  - horizontalité du corps
  - immobilité / temps au sol
  - inertie post-impact

Version sémantique des seuils pour traçabilité des KPI.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


CRITERIA_VERSION = "1.0.0"


@dataclass(frozen=True)
class FallCriteria:
    """Seuils versionnés de détection de chute."""

    version: str = CRITERIA_VERSION
    # Angle tronc (degrés) : 0 = vertical, 90 = horizontal
    trunk_angle_fall_deg: float = 55.0
    trunk_angle_critical_deg: float = 70.0
    # Vitesse verticale négative (vers le sol), m/s
    vertical_speed_ms: float = 1.8
    vertical_speed_critical_ms: float = 2.8
    # Accélération d'impact (m/s²)
    impact_accel_ms2: float = 6.0
    # Temps au sol (s) avant confirmation d'alerte
    time_on_ground_alert_s: float = 8.0
    time_on_ground_critical_s: float = 15.0
    # Immobilité (ratio de frames quasi-statiques 0-1)
    stillness_ratio: float = 0.65
    # Confiance minimale pour valider
    confidence_threshold: float = 0.72
    # Pondérations score composite
    w_angle: float = 0.28
    w_velocity: float = 0.27
    w_horizontal: float = 0.18
    w_impact: float = 0.15
    w_stillness: float = 0.12

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Profils CDC : âge, mobilité → adaptation des seuils
PROFILE_OVERRIDES: Dict[str, Dict[str, float]] = {
    "senior_fragile": {
        "trunk_angle_fall_deg": 48.0,
        "vertical_speed_ms": 1.4,
        "time_on_ground_alert_s": 5.0,
        "confidence_threshold": 0.65,
    },
    "senior_autonome": {
        "trunk_angle_fall_deg": 52.0,
        "vertical_speed_ms": 1.6,
        "time_on_ground_alert_s": 7.0,
    },
    "adulte": {},
    "handicape": {
        "trunk_angle_fall_deg": 50.0,
        "time_on_ground_alert_s": 6.0,
        "stillness_ratio": 0.55,
        "confidence_threshold": 0.68,
    },
}


def criteria_for_profile(profile: Optional[Dict[str, Any]] = None) -> FallCriteria:
    """Construit FallCriteria adapté au profil (âge, mobilité, type)."""
    base = FallCriteria()
    if not profile:
        return base
    key = str(
        profile.get("profile_type")
        or profile.get("mobility")
        or profile.get("type")
        or ""
    ).lower()
    # Heuristique âge
    age = profile.get("age")
    if age is not None:
        try:
            age = int(age)
            if age >= 80:
                key = key or "senior_fragile"
            elif age >= 65:
                key = key or "senior_autonome"
        except (TypeError, ValueError):
            pass
    overrides = PROFILE_OVERRIDES.get(key, {})
    if not overrides and profile.get("velocity_threshold") is not None:
        # compat ancien champ
        try:
            overrides = {"vertical_speed_ms": abs(float(profile["velocity_threshold"]))}
        except (TypeError, ValueError):
            overrides = {}
    if not overrides:
        return base
    data = base.to_dict()
    data.update(overrides)
    return FallCriteria(**data)


def compute_signals(
    *,
    trunk_angle_deg: float,
    vertical_velocity_ms: float,
    is_horizontal: bool,
    impact_accel_ms2: float = 0.0,
    stillness_ratio: float = 0.0,
    time_on_ground_s: float = 0.0,
) -> Dict[str, float]:
    """Normalise les signaux bruts pour la décision."""
    return {
        "trunk_angle_deg": float(trunk_angle_deg),
        "vertical_velocity_ms": float(vertical_velocity_ms),
        "is_horizontal": 1.0 if is_horizontal else 0.0,
        "impact_accel_ms2": float(impact_accel_ms2),
        "stillness_ratio": float(stillness_ratio),
        "time_on_ground_s": float(time_on_ground_s),
    }


def decide_fall(
    signals: Dict[str, float],
    criteria: Optional[FallCriteria] = None,
) -> Dict[str, Any]:
    """
    Décide s'il y a chute + score de confiance.

    Règles (OR pondéré) :
    1. Angle tronc élevé ET (vitesse verticale forte OU horizontalité)
    2. Impact fort + horizontalité
    3. Temps au sol dépassé + immobilité (confirmation post-chute)
    """
    c = criteria or FallCriteria()
    angle = float(signals.get("trunk_angle_deg", 0.0))
    v_y = abs(float(signals.get("vertical_velocity_ms", 0.0)))
    horiz = float(signals.get("is_horizontal", 0.0)) >= 0.5
    impact = abs(float(signals.get("impact_accel_ms2", 0.0)))
    still = float(signals.get("stillness_ratio", 0.0))
    t_ground = float(signals.get("time_on_ground_s", 0.0))

    # Scores partiels 0-1
    s_angle = min(1.0, max(0.0, (angle - 30.0) / max(c.trunk_angle_critical_deg - 30.0, 1.0)))
    s_vel = min(1.0, max(0.0, v_y / max(c.vertical_speed_critical_ms, 0.1)))
    s_horiz = 1.0 if horiz else (0.4 if angle > c.trunk_angle_fall_deg else 0.0)
    s_impact = min(1.0, max(0.0, impact / max(c.impact_accel_ms2 * 1.5, 0.1)))
    s_still = min(1.0, max(0.0, still / max(c.stillness_ratio, 0.01)))

    confidence = (
        c.w_angle * s_angle
        + c.w_velocity * s_vel
        + c.w_horizontal * s_horiz
        + c.w_impact * s_impact
        + c.w_stillness * s_still
    )
    confidence = float(max(0.0, min(1.0, confidence)))

    # Règles booléennes
    rule_dynamic = (angle >= c.trunk_angle_fall_deg and v_y >= c.vertical_speed_ms) or (
        angle >= c.trunk_angle_critical_deg and horiz
    )
    rule_impact = impact >= c.impact_accel_ms2 and (horiz or angle >= c.trunk_angle_fall_deg)
    rule_ground = t_ground >= c.time_on_ground_alert_s and still >= c.stillness_ratio * 0.8

    fall_detected = bool(
        (confidence >= c.confidence_threshold and (rule_dynamic or rule_impact))
        or rule_ground
        or (confidence >= 0.85 and horiz)
    )

    return {
        "fall_detected": fall_detected,
        "confidence": round(confidence, 4),
        "criteria_version": c.version,
        "rules": {
            "dynamic": rule_dynamic,
            "impact": rule_impact,
            "time_on_ground": rule_ground,
        },
        "partial_scores": {
            "angle": round(s_angle, 4),
            "velocity": round(s_vel, 4),
            "horizontal": round(s_horiz, 4),
            "impact": round(s_impact, 4),
            "stillness": round(s_still, 4),
        },
        "thresholds": {
            "trunk_angle_fall_deg": c.trunk_angle_fall_deg,
            "vertical_speed_ms": c.vertical_speed_ms,
            "time_on_ground_alert_s": c.time_on_ground_alert_s,
            "confidence_threshold": c.confidence_threshold,
        },
        "signals": signals,
    }
