"""
Features squelette pour l'apprentissage (MediaPipe Pose).

Aligné CDC + détection live :
  YOLO (optionnel) → bbox personne → MediaPipe landmarks
  → séries temporelles (angle tronc, v_y, horizontalité, immobilité)
  → vecteur d'indicateurs pour les arbres (normal / urgent / critique)
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import cv2
except ImportError as e:
    raise SystemExit("opencv-python requis pour skeleton_features") from e

# Indices MediaPipe Pose (33 landmarks)
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker
LM_NOSE = 0
LM_L_SHOULDER, LM_R_SHOULDER = 11, 12
LM_L_HIP, LM_R_HIP = 23, 24
LM_L_ANKLE, LM_R_ANKLE = 27, 28
LM_L_WRIST, LM_R_WRIST = 15, 16


SKELETON_INDICATOR_IDS: List[str] = [
    "sk_trunk_angle_mean",
    "sk_trunk_angle_max",
    "sk_trunk_angle_std",
    "sk_trunk_angle_final",
    "sk_vertical_speed_max",
    "sk_vertical_speed_mean",
    "sk_impact_proxy",
    "sk_horizontal_ratio",
    "sk_time_on_ground_proxy",
    "sk_stillness_landmarks",
    "sk_hip_drop",
    "sk_head_hip_delta_y",
    "sk_pose_visibility",
    "sk_frames_with_pose",
    "sk_person_detected_ratio",
]


def _mid(a: Dict, b: Dict) -> Tuple[float, float, float]:
    return (
        (float(a["x"]) + float(b["x"])) / 2.0,
        (float(a["y"]) + float(b["y"])) / 2.0,
        (float(a.get("visibility", 1)) + float(b.get("visibility", 1))) / 2.0,
    )


def trunk_angle_deg(landmarks: List[Dict]) -> Optional[float]:
    """Angle tronc vs vertical (0=debout, 90=allongé), via milieu épaules → milieu hanches."""
    try:
        sh = _mid(landmarks[LM_L_SHOULDER], landmarks[LM_R_SHOULDER])
        hip = _mid(landmarks[LM_L_HIP], landmarks[LM_R_HIP])
        dx = sh[0] - hip[0]
        dy = sh[1] - hip[1]  # y image vers le bas
        # Vecteur tronc (hanche → épaule) ; vertical image = (0, -1) vers le haut
        # angle with vertical up
        vx, vy = dx, -dy  # invert y for "up"
        norm = (vx * vx + vy * vy) ** 0.5
        if norm < 1e-6:
            return None
        cos_a = max(-1.0, min(1.0, vy / norm))  # dot with (0,1) after invert → vertical up
        # Actually vertical up is (0, 1) in our inverted space if vy points up
        angle = float(np.degrees(np.arccos(cos_a)))
        return angle
    except Exception:
        return None


def is_horizontal(landmarks: List[Dict], angle_thresh: float = 55.0) -> bool:
    a = trunk_angle_deg(landmarks)
    return a is not None and a >= angle_thresh


def center_hip_y(landmarks: List[Dict]) -> Optional[float]:
    try:
        return _mid(landmarks[LM_L_HIP], landmarks[LM_R_HIP])[1]
    except Exception:
        return None


def mean_visibility(landmarks: List[Dict]) -> float:
    if not landmarks:
        return 0.0
    return float(np.mean([float(lm.get("visibility", 0)) for lm in landmarks]))


def landmark_motion(prev: List[Dict], cur: List[Dict]) -> float:
    """Déplacement moyen des points (proxy immobilité)."""
    n = min(len(prev), len(cur))
    if n == 0:
        return 0.0
    dists = []
    for i in range(n):
        dx = float(cur[i]["x"]) - float(prev[i]["x"])
        dy = float(cur[i]["y"]) - float(prev[i]["y"])
        dists.append((dx * dx + dy * dy) ** 0.5)
    return float(np.mean(dists))


_pose_model = None


def _get_pose(complexity: int = 1):
    global _pose_model
    if _pose_model is not None:
        return _pose_model
    try:
        import mediapipe as mp
        _pose_model = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=complexity,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        return _pose_model
    except Exception as e:
        raise RuntimeError(f"MediaPipe Pose indisponible: {e}") from e


def _landmarks_from_mp(results) -> Optional[List[Dict]]:
    if not results or not results.pose_landmarks:
        return None
    out = []
    for lm in results.pose_landmarks.landmark:
        out.append({
            "x": float(lm.x),
            "y": float(lm.y),
            "z": float(lm.z),
            "visibility": float(lm.visibility),
        })
    return out


def _try_yolo_crop(frame_bgr: np.ndarray) -> np.ndarray:
    """Optionnel : crop personne YOLO pour stabiliser la pose."""
    try:
        from ultralytics import YOLO
        # modèle léger ; chargé une fois via attribut fonction
        if not hasattr(_try_yolo_crop, "_model"):
            _try_yolo_crop._model = YOLO("yolov8n.pt")
        res = _try_yolo_crop._model.predict(frame_bgr, classes=[0], verbose=False)
        if not res:
            return frame_bgr
        boxes = res[0].boxes
        if boxes is None or len(boxes) == 0:
            return frame_bgr
        # meilleure conf
        confs = boxes.conf.cpu().numpy()
        i = int(np.argmax(confs))
        x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
        h, w = frame_bgr.shape[:2]
        bw, bh = x2 - x1, y2 - y1
        x1 = max(0, int(x1 - 0.1 * bw))
        y1 = max(0, int(y1 - 0.1 * bh))
        x2 = min(w, int(x2 + 0.1 * bw))
        y2 = min(h, int(y2 + 0.1 * bh))
        if x2 > x1 + 8 and y2 > y1 + 8:
            return frame_bgr[y1:y2, x1:x2]
    except Exception:
        pass
    return frame_bgr


def extract_pose_sequence(
    clip_dir: Path,
    max_frames: int = 24,
    use_yolo_crop: bool = True,
) -> List[Optional[List[Dict]]]:
    """Charge f*.jpg du clip et retourne une pose par frame (None si échec)."""
    pose = _get_pose()
    frames = sorted(clip_dir.glob("f*.jpg"))[:max_frames]
    seq: List[Optional[List[Dict]]] = []
    for fp in frames:
        img = cv2.imread(str(fp))
        if img is None:
            seq.append(None)
            continue
        if use_yolo_crop:
            img = _try_yolo_crop(img)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)
        seq.append(_landmarks_from_mp(results))
    return seq


def compute_skeleton_indicators(
    clip_dir: Path,
    max_frames: int = 24,
    use_yolo_crop: bool = True,
    fps: float = 10.0,
) -> Optional[Dict[str, float]]:
    """
    Calcule le vecteur de features squelette pour un fragment.
    Retourne None si aucune pose détectée.
    """
    clip_dir = Path(clip_dir)
    try:
        seq = extract_pose_sequence(clip_dir, max_frames=max_frames, use_yolo_crop=use_yolo_crop)
    except RuntimeError:
        return None

    angles: List[float] = []
    hip_ys: List[float] = []
    horiz_flags: List[bool] = []
    motions: List[float] = []
    vis_list: List[float] = []
    prev = None
    n_pose = 0

    for landmarks in seq:
        if landmarks is None:
            continue
        n_pose += 1
        a = trunk_angle_deg(landmarks)
        if a is not None:
            angles.append(a)
            horiz_flags.append(a >= 55.0)
        hy = center_hip_y(landmarks)
        if hy is not None:
            hip_ys.append(hy)
        vis_list.append(mean_visibility(landmarks))
        if prev is not None:
            motions.append(landmark_motion(prev, landmarks))
        prev = landmarks

    if n_pose == 0 or not angles:
        return None

    angles_a = np.array(angles, dtype=np.float64)
    dt = 1.0 / max(fps, 1.0)

    # Vitesses verticales (hip y image ↓ = chute positive en y image)
    v_list: List[float] = []
    if len(hip_ys) >= 2:
        for i in range(1, len(hip_ys)):
            v_list.append((hip_ys[i] - hip_ys[i - 1]) / dt)
    v_a = np.array(v_list) if v_list else np.array([0.0])

    impact = 0.0
    if len(v_a) >= 2:
        impact = float(np.max(np.abs(np.diff(v_a)) / dt))

    # Temps au sol proxy : fraction frames horizontales * durée clip
    horiz_ratio = float(np.mean(horiz_flags)) if horiz_flags else 0.0
    duration = max(len(seq), 1) * dt
    time_on_ground = horiz_ratio * duration

    still = float(np.mean(np.array(motions) < 0.01)) if motions else 0.0
    hip_drop = float(hip_ys[-1] - hip_ys[0]) if len(hip_ys) >= 2 else 0.0

    # head - hip delta y (positif si tête plus bas que hanche en coords image = tête vers le bas)
    head_hip = 0.0
    for landmarks in seq:
        if landmarks is None:
            continue
        try:
            head_y = float(landmarks[LM_NOSE]["y"])
            hip_y = center_hip_y(landmarks)
            if hip_y is not None:
                head_hip = head_y - hip_y  # dernière valeur utile
        except Exception:
            pass

    n_frames = max(len(seq), 1)
    out = {
        "sk_trunk_angle_mean": float(np.mean(angles_a)),
        "sk_trunk_angle_max": float(np.max(angles_a)),
        "sk_trunk_angle_std": float(np.std(angles_a)),
        "sk_trunk_angle_final": float(angles_a[-1]),
        "sk_vertical_speed_max": float(np.max(np.abs(v_a))),
        "sk_vertical_speed_mean": float(np.mean(np.abs(v_a))),
        "sk_impact_proxy": float(impact),
        "sk_horizontal_ratio": horiz_ratio,
        "sk_time_on_ground_proxy": float(time_on_ground),
        "sk_stillness_landmarks": still,
        "sk_hip_drop": hip_drop,
        "sk_head_hip_delta_y": float(head_hip),
        "sk_pose_visibility": float(np.mean(vis_list)) if vis_list else 0.0,
        "sk_frames_with_pose": float(n_pose),
        "sk_person_detected_ratio": float(n_pose) / float(n_frames),
    }
    return out


def skeleton_available() -> bool:
    try:
        _get_pose()
        return True
    except Exception:
        return False
