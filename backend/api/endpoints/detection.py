"""API détection frame — cœur IA Edge."""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.dependencies import get_db, get_current_user

router = APIRouter()


class DetectJsonBody(BaseModel):
    """Image en base64 optionnel — pour tests API."""
    image_b64: Optional[str] = None
    camera_id: str = "default"
    person_id: Optional[int] = None
    profile: Optional[Dict[str, Any]] = None


def _get_pipeline():
    from backend.services.detection_pipeline import DetectionPipelineService
    from backend.ai.manager import AIManager

    pipe = DetectionPipelineService()
    try:
        ai = AIManager()
        pipe.set_ai_manager(ai)
    except Exception:
        pass
    return pipe


def _profile_from_db(db: Session, person_id: Optional[int]) -> Dict[str, Any]:
    if not person_id:
        return {}
    try:
        from backend.database.crud import get_person
        p = get_person(db, person_id)
        if not p:
            return {}
        return {
            "age": getattr(p, "age", None),
            "profile_type": str(getattr(p, "profile_type", None) or getattr(p, "mobility", None) or ""),
            "height": getattr(p, "height", None),
            "weight": getattr(p, "weight", None),
        }
    except Exception:
        return {}


@router.post("/process-frame")
async def process_frame(
    file: UploadFile = File(...),
    camera_id: str = Form("default"),
    person_id: Optional[int] = Form(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyse une frame (multipart) : squelette MediaPipe → critères chute → gravité.
    """
    data = await file.read()
    if not data:
        raise HTTPException(400, "image vide")
    try:
        import cv2
        arr = np.frombuffer(data, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception as e:
        raise HTTPException(400, f"decode image: {e}")
    if image is None:
        raise HTTPException(400, "format image invalide")

    profile = _profile_from_db(db, person_id)
    pipe = _get_pipeline()
    result = pipe.process_frame(image, camera_id=camera_id, person_profile=profile)
    # ne pas renvoyer landmarks bruts massifs
    result.pop("raw", None)
    return result


@router.get("/criteria")
async def get_criteria(current_user=Depends(get_current_user)):
    """Expose les seuils formels de décision (CDC)."""
    from backend.ai.fall_criteria import FallCriteria, CRITERIA_VERSION, PROFILE_OVERRIDES
    return {
        "version": CRITERIA_VERSION,
        "default": FallCriteria().to_dict(),
        "profiles": PROFILE_OVERRIDES,
        "description": {
            "trunk_angle_fall_deg": "Angle tronc (°) au-delà duquel on suspecte une chute",
            "vertical_speed_ms": "Vitesse verticale minimale (m/s)",
            "time_on_ground_alert_s": "Temps au sol avant confirmation alerte",
            "confidence_threshold": "Score composite minimal",
        },
    }


@router.post("/simulate-signals")
async def simulate_signals(
    body: Dict[str, Any],
    current_user=Depends(get_current_user),
):
    """
    Test unitaire métier : injecte des signaux sans image.
    Body exemple: {"trunk_angle_deg": 75, "vertical_velocity_ms": 2.5, "is_horizontal": 1, ...}
    """
    from backend.ai.fall_criteria import decide_fall, criteria_for_profile, compute_signals
    from backend.services.severity_engine import assess_severity

    profile = body.get("profile") or {}
    signals = compute_signals(
        trunk_angle_deg=float(body.get("trunk_angle_deg", 0)),
        vertical_velocity_ms=float(body.get("vertical_velocity_ms", 0)),
        is_horizontal=bool(body.get("is_horizontal", 0)),
        impact_accel_ms2=float(body.get("impact_accel_ms2", 0)),
        stillness_ratio=float(body.get("stillness_ratio", 0)),
        time_on_ground_s=float(body.get("time_on_ground_s", 0)),
    )
    decision = decide_fall(signals, criteria_for_profile(profile))
    severity = assess_severity(signals, profile, decision["confidence"])
    return {"signals": signals, "decision": decision, "severity": severity}
