"""
Score de gravité post-chute — CDC module décisionnel.

Niveaux : faible | moyenne | elevee | critique
Sorties : gravity_score 0-100, injury_probability, impact_intensity, time_on_ground.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


def assess_severity(
    signals: Dict[str, float],
    person_profile: Optional[Dict[str, Any]] = None,
    fall_confidence: float = 0.0,
) -> Dict[str, Any]:
    angle = float(signals.get("trunk_angle_deg", 0.0))
    v_y = abs(float(signals.get("vertical_velocity_ms", 0.0)))
    impact = abs(float(signals.get("impact_accel_ms2", 0.0)))
    t_ground = float(signals.get("time_on_ground_s", 0.0))
    still = float(signals.get("stillness_ratio", 0.0))

    # Intensité d'impact 0-1
    impact_intensity = min(1.0, impact / 12.0 + v_y / 5.0 * 0.4)

    # Score 0-100
    score = 0.0
    score += min(35.0, angle / 90.0 * 35.0)
    score += min(25.0, v_y / 3.5 * 25.0)
    score += min(20.0, impact_intensity * 20.0)
    score += min(15.0, min(t_ground, 30.0) / 30.0 * 15.0)
    score += min(5.0, still * 5.0)
    score = max(0.0, min(100.0, score * (0.7 + 0.3 * float(fall_confidence))))

    # Facteur âge / fragilité
    injury_boost = 1.0
    if person_profile:
        age = person_profile.get("age")
        try:
            age = int(age) if age is not None else None
        except (TypeError, ValueError):
            age = None
        if age and age >= 80:
            injury_boost = 1.35
        elif age and age >= 65:
            injury_boost = 1.2
        ptype = str(person_profile.get("profile_type") or "").lower()
        if "fragile" in ptype or "handicape" in ptype:
            injury_boost = max(injury_boost, 1.3)

    injury_probability = max(0.0, min(1.0, (score / 100.0) * 0.85 * injury_boost))

    if score >= 76:
        level, label = "critique", "critique"
    elif score >= 51:
        level, label = "elevee", "urgent"
    elif score >= 26:
        level, label = "moyenne", "urgent"
    else:
        level, label = "faible", "normal"

    # Temps d'observation recommandé avant alerte (s)
    if level == "critique":
        observe_s = 3.0
    elif level == "elevee":
        observe_s = 6.0
    elif level == "moyenne":
        observe_s = 10.0
    else:
        observe_s = 15.0
    if person_profile and person_profile.get("age"):
        try:
            if int(person_profile["age"]) >= 75:
                observe_s *= 0.7
        except (TypeError, ValueError):
            pass

    return {
        "gravity_level": level,
        "gravity_score": round(score, 1),
        "severity_label": label,  # normal | urgent | critique (produit)
        "injury_probability": round(injury_probability, 4),
        "impact_intensity": round(impact_intensity, 4),
        "time_on_ground_s": round(t_ground, 2),
        "recommended_observe_s": round(observe_s, 1),
        "should_alert": label in ("urgent", "critique") or t_ground >= observe_s,
    }
