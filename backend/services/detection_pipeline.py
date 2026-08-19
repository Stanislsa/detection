"""
Pipeline de détection Edge AI — cœur applicatif (CDC).

Flux :
  frame → MediaPipe Pose (squelette) → critères de chute → gravité → décision alerte
  YOLO optionnel uniquement pour bbox personne (pas YOLO-Pose, conforme CDC).
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

import numpy as np

from backend.core.logger import get_logger
from backend.ai.fall_criteria import (
    compute_signals,
    criteria_for_profile,
    decide_fall,
)
from backend.services.severity_engine import assess_severity

logger = get_logger(__name__)


class DetectionPipelineService:
    """Orchestration frame → décision métier."""

    def __init__(self, ai_manager=None):
        self._ai = ai_manager
        self._ground_since: Dict[str, float] = {}  # camera_id → timestamp horizontal start
        self._last_vel: Dict[str, float] = {}

    def set_ai_manager(self, ai_manager) -> None:
        self._ai = ai_manager

    def process_frame(
        self,
        image: np.ndarray,
        *,
        camera_id: str = "default",
        person_profile: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()
        ts = timestamp or time.time()
        profile = person_profile or {}
        criteria = criteria_for_profile(profile)

        # 1) Détection pose / chute via AIManager (MediaPipe-centric)
        raw: Dict[str, Any] = {}
        if self._ai is not None:
            try:
                if hasattr(self._ai, "detect_fall"):
                    raw = self._ai.detect_fall(image, person_profile=profile) or {}
                elif hasattr(self._ai, "detect"):
                    raw = self._ai.detect(image) or {}
            except Exception as e:
                logger.error(f"AI detect_fall failed: {e}")
                raw = {"error": str(e), "fall_detected": False, "confidence": 0.0}

        # Extraire signaux (compat plusieurs formes de retour)
        mp = raw.get("mediapipe") if isinstance(raw.get("mediapipe"), dict) else raw
        trunk = float(mp.get("trunk_angle") or mp.get("trunk_angle_deg") or 0.0)
        v_y = float(mp.get("vertical_velocity") or mp.get("vertical_velocity_ms") or 0.0)
        is_h = bool(mp.get("is_horizontal") or mp.get("body_horizontal") or trunk >= 60)
        impact = float(mp.get("impact_accel") or mp.get("impact_accel_ms2") or 0.0)
        if impact == 0.0 and camera_id in self._last_vel:
            # approx accélération
            impact = abs(v_y - self._last_vel[camera_id]) / max(0.033, 0.1)
        self._last_vel[camera_id] = v_y

        # Temps au sol
        if is_h:
            if camera_id not in self._ground_since:
                self._ground_since[camera_id] = ts
            t_ground = ts - self._ground_since[camera_id]
        else:
            self._ground_since.pop(camera_id, None)
            t_ground = 0.0

        still = float(mp.get("stillness_ratio") or (0.8 if is_h and abs(v_y) < 0.3 else 0.2))

        signals = compute_signals(
            trunk_angle_deg=trunk,
            vertical_velocity_ms=v_y,
            is_horizontal=is_h,
            impact_accel_ms2=impact,
            stillness_ratio=still,
            time_on_ground_s=t_ground,
        )
        decision = decide_fall(signals, criteria)
        severity = assess_severity(signals, profile, decision["confidence"])

        # Si MediaPipe a déjà dit chute, ne pas l'écraser trop strictement
        if mp.get("fall_detected") and decision["confidence"] >= 0.5:
            decision["fall_detected"] = True

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "fall_detected": decision["fall_detected"],
            "confidence": decision["confidence"],
            "criteria_version": decision["criteria_version"],
            "signals": signals,
            "decision": decision,
            "severity": severity,
            "should_alert": bool(
                decision["fall_detected"] and severity.get("should_alert", True)
            ),
            "person_detected": bool(raw.get("yolo") or mp.get("landmarks") or trunk > 0),
            "method": "mediapipe_pose+criteria",
            "latency_ms": round(latency_ms, 2),
            "camera_id": camera_id,
            "raw": {k: raw[k] for k in raw if k != "landmarks"},
        }
