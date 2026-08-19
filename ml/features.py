"""Extraction + stockage features dans data/features/."""
from __future__ import annotations
import csv, json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from ml.config import (
    FEATURES_RAW, FEATURES_PROCESSED, FEATURES_BY_CLASS, FEATURES_TABLE,
    FEATURES_MATRIX, LABELS_VECTOR, FEATURES_META, RAW_DIR, CLASS_DIRS,
    CLASSES, STILLNESS_THRESH,
)
from ml.indicators import INDICATOR_IDS, catalog_as_dict
try:
    import cv2
except ImportError as e:
    raise SystemExit("opencv-python requis") from e

def _load_gray_frames(clip_dir: Path, max_frames: int = 20):
    grays = []
    for fp in sorted(clip_dir.glob("f*.jpg"))[:max_frames]:
        img = cv2.imread(str(fp), cv2.IMREAD_GRAYSCALE)
        if img is not None:
            grays.append(img.astype(np.float32))
    return grays

def compute_indicators(clip_dir: Path) -> Optional[Dict[str, float]]:
    grays = _load_gray_frames(clip_dir)
    if not grays:
        return None
    diffs = [float(np.mean(np.abs(grays[i] - grays[i-1]))) for i in range(1, len(grays))]
    da = np.array(diffs) if diffs else np.array([0.0])
    mid = grays[len(grays)//2]
    gx = float(np.abs(np.diff(mid, axis=1)).mean()) if mid.shape[1] > 1 else 0.0
    gy = float(np.abs(np.diff(mid, axis=0)).mean()) if mid.shape[0] > 1 else 0.0
    stack = np.stack(grays)
    edges = cv2.Canny(mid.astype(np.uint8), 50, 150)
    hist, _ = np.histogram(mid, bins=8, range=(0, 256), density=True)
    trend = float(np.polyfit(np.arange(len(da)), da, 1)[0]) if len(da) >= 2 else 0.0
    values = {
        "motion_mean": float(np.mean(da)), "motion_max": float(np.max(da)),
        "motion_std": float(np.std(da)), "motion_energy": float(np.sum(da)/max(len(grays),1)),
        "optical_flow_mag": (gx+gy)/2,
        "luma_mean": float(np.mean(stack)), "luma_std": float(np.std(stack)),
        "luma_min": float(np.min(stack)), "luma_max": float(np.max(stack)),
        "edge_density": float(np.mean(edges > 0)),
        **{f"hist_b{i}": float(hist[i]) for i in range(8)},
        "n_frames": float(len(grays)), "motion_trend": trend,
        "stillness_ratio": float(np.mean(da < STILLNESS_THRESH)),
    }
    # Fusion features image + squelette (MediaPipe)
    try:
        from ml.skeleton_features import compute_skeleton_indicators, SKELETON_INDICATOR_IDS
        sk = compute_skeleton_indicators(clip_dir)
        if sk:
            values.update(sk)
            print(f"[features:skeleton] {clip_dir.name} pose OK")
        else:
            for k in SKELETON_INDICATOR_IDS:
                values.setdefault(k, 0.0)
            print(f"[features:skeleton] {clip_dir.name} no pose → zeros")
    except Exception as e:
        from ml.skeleton_features import SKELETON_INDICATOR_IDS
        for k in SKELETON_INDICATOR_IDS:
            values.setdefault(k, 0.0)
        print(f"[features:skeleton] skip ({e})")
    return {k: float(values.get(k, 0.0)) for k in INDICATOR_IDS}

def vectorize(indicators: Dict[str, float]) -> np.ndarray:
    return np.array([indicators[k] for k in INDICATOR_IDS], dtype=np.float32)

def save_fragment_features(fragment_id, indicators, label=None, extra=None):
    FEATURES_RAW.mkdir(parents=True, exist_ok=True)
    path = FEATURES_RAW / f"{fragment_id}.json"
    payload = {"id": fragment_id, "label": label, "indicators": indicators,
               "indicator_order": INDICATOR_IDS, "updated_at": datetime.utcnow().isoformat(),
               **(extra or {})}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

def extract_and_store_from_raw():
    rows = []
    if not RAW_DIR.exists():
        return rows
    for clip in sorted(RAW_DIR.iterdir()):
        if not clip.is_dir():
            continue
        inds = compute_indicators(clip)
        if not inds:
            continue
        meta = json.loads((clip/"meta.json").read_text()) if (clip/"meta.json").exists() else {}
        save_fragment_features(clip.name, inds, label=meta.get("label"), extra={"source_path": str(clip)})
        rows.append({"id": clip.name, "label": meta.get("label"), **inds})
        print(f"[features] {clip.name} → {len(inds)} indicateurs")
    return rows

def extract_and_store_from_classes():
    rows = []
    for label in CLASSES:
        root = CLASS_DIRS[label]
        if not root.exists():
            continue
        for clip in sorted(root.iterdir()):
            if not clip.is_dir():
                continue
            inds = compute_indicators(clip)
            if not inds:
                continue
            save_fragment_features(clip.name, inds, label=label)
            rows.append({"id": clip.name, "label": label, **inds})
    return rows

def build_feature_table(rows=None):
    FEATURES_PROCESSED.mkdir(parents=True, exist_ok=True)
    FEATURES_BY_CLASS.mkdir(parents=True, exist_ok=True)
    if rows is None:
        rows = []
        for fp in sorted(FEATURES_RAW.glob("*.json")):
            data = json.loads(fp.read_text(encoding="utf-8"))
            rows.append({"id": data.get("id"), "label": data.get("label"), **(data.get("indicators") or {})})
    if not rows:
        return np.zeros((0, len(INDICATOR_IDS))), np.array([]), []
    ids, X_list, y_list = [], [], []
    for r in rows:
        if not all(k in r for k in INDICATOR_IDS):
            continue
        ids.append(str(r["id"]))
        X_list.append([float(r[k]) for k in INDICATOR_IDS])
        y_list.append(r.get("label") or "unknown")
    X, y = np.array(X_list, dtype=np.float32), np.array(y_list)
    fields = ["id", "label"] + INDICATOR_IDS
    with open(FEATURES_TABLE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in rows:
            if str(r.get("id")) in ids:
                w.writerow({k: r.get(k, "") for k in fields})
    for label in CLASSES:
        subset = [r for r in rows if r.get("label") == label]
        with open(FEATURES_BY_CLASS / f"{label}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
            for r in subset:
                w.writerow({k: r.get(k, "") for k in fields})
    np.save(FEATURES_MATRIX, X); np.save(LABELS_VECTOR, y)
    meta = {"n_samples": int(X.shape[0]), "n_features": int(X.shape[1]) if X.ndim==2 else 0,
            "feature_names": INDICATOR_IDS, "catalog": catalog_as_dict(),
            "updated_at": datetime.utcnow().isoformat()}
    FEATURES_META.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[features] Table → {FEATURES_TABLE} X={X.shape}")
    return X, y, ids
