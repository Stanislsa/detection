"""Tri normal / urgent / critique."""
from __future__ import annotations
import json, shutil
from pathlib import Path
from typing import Dict, List
from ml.config import RAW_DIR, CLASS_DIRS, CLASSES, METADATA_FILE, THRESH_URGENT, THRESH_CRITIQUE, TREE_MODEL
from ml.features import compute_indicators, vectorize, save_fragment_features

def severity_from_motion(m):
    if m >= THRESH_CRITIQUE: return "critique"
    if m >= THRESH_URGENT: return "urgent"
    return "normal"

def load_index():
    if not METADATA_FILE.exists(): return []
    return json.loads(METADATA_FILE.read_text(encoding="utf-8")).get("items") or []

def _assign_labels(items):
    scored = [(it.get("id") or Path(it.get("path","x")).name, float(it.get("motion_score") or 0)) for it in items]
    scored.sort(key=lambda x: x[1]); n, out = len(scored), {}
    for i, (fid, score) in enumerate(scored):
        abs_l = severity_from_motion(score)
        if abs_l == "critique" or (n >= 3 and i >= n - max(1, n//5)): out[fid] = "critique"
        elif abs_l == "urgent" or (n >= 3 and i >= n - max(2, n//3)): out[fid] = "urgent"
        else: out[fid] = "normal"
    if len(set(out.values())) == 1 and n >= 3:
        for i, (fid, _) in enumerate(scored):
            out[fid] = "normal" if i < n//3 else ("urgent" if i < 2*n//3 else "critique")
    return out

def triage_all(use_model=True):
    for d in CLASS_DIRS.values(): d.mkdir(parents=True, exist_ok=True)
    items = load_index() or [json.loads(p.read_text()) for p in RAW_DIR.glob("*/meta.json")]
    labels_map = _assign_labels(items)
    counts = {c: 0 for c in CLASSES}
    model = None
    if use_model and TREE_MODEL.exists():
        try:
            import joblib; model = joblib.load(TREE_MODEL)
        except Exception as e:
            print(f"[triage] model: {e}")
    for it in items:
        clip_dir = Path(it.get("path") or "")
        if not clip_dir.exists(): continue
        fid = it.get("id") or clip_dir.name
        motion = float(it.get("motion_score") or 0)
        label = labels_map.get(fid, severity_from_motion(motion))
        conf, method = 0.65, "motion_rank"
        inds = compute_indicators(clip_dir)
        if model and inds:
            try:
                rf, classes = model["random_forest"], list(model.get("classes") or CLASSES)
                proba = rf.predict_proba([vectorize(inds)])[0]
                idx = int(proba.argmax()); label, conf, method = classes[idx], float(proba[idx]), "random_forest"
            except Exception as e:
                print(f"[triage] predict: {e}")
        if inds: save_fragment_features(fid, inds, label=label)
        dest = CLASS_DIRS[label] / clip_dir.name
        if dest.exists(): shutil.rmtree(dest)
        shutil.copytree(clip_dir, dest)
        meta = dict(it); meta.update({"label": label, "confidence": round(conf,3), "triage_method": method})
        (dest/"meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        counts[label] += 1
        print(f"[triage] {fid} → {label} ({method})")
    print(f"[triage] normal={counts['normal']} urgent={counts['urgent']} critique={counts['critique']}")
    return counts
