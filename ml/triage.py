"""Tri normal/urgent/critique — bootstrap + modèle + erreurs."""
from __future__ import annotations
import json, shutil
from pathlib import Path
from typing import Dict, List
from ml.config import RAW_DIR, CLASS_DIRS, CLASSES, METADATA_FILE, THRESH_URGENT, THRESH_CRITIQUE, TREE_MODEL
from ml.features import compute_indicators, vectorize, save_fragment_features
from ml.errors import PredictionError, ModelNotFoundError

def severity_from_motion(m: float) -> str:
    if m >= THRESH_CRITIQUE: return "critique"
    if m >= THRESH_URGENT: return "urgent"
    return "normal"

def load_index() -> List[dict]:
    if not METADATA_FILE.exists(): return []
    try:
        return json.loads(METADATA_FILE.read_text(encoding="utf-8")).get("items") or []
    except Exception as e:
        print(f"[triage] index: {e}"); return []

def _assign_labels_bootstrap(items):
    scored = [(it.get("id") or Path(it.get("path","x")).name, float(it.get("motion_score") or 0)) for it in items]
    scored.sort(key=lambda x: x[1]); n, out = len(scored), {}
    if n == 0: return out
    if n == 1: out[scored[0][0]] = severity_from_motion(scored[0][1]); return out
    if n == 2:
        out[scored[0][0]] = "normal"
        out[scored[1][0]] = "critique" if scored[1][1] >= THRESH_URGENT else "urgent"
        return out
    for i, (fid, score) in enumerate(scored):
        if score >= THRESH_CRITIQUE * 1.5: out[fid] = "critique"
        elif i < n // 3: out[fid] = "normal"
        elif i < (2 * n) // 3: out[fid] = "urgent"
        else: out[fid] = "critique"
    return out

def triage_all(use_model: bool = True) -> Dict[str, int]:
    for d in CLASS_DIRS.values(): d.mkdir(parents=True, exist_ok=True)
    items = load_index()
    if not items:
        for p in RAW_DIR.glob("*/meta.json"):
            try: items.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception as e: print(f"[triage] meta {p}: {e}")
    labels_map = _assign_labels_bootstrap(items)
    counts = {c: 0 for c in CLASSES}; errors = []; use_ml = use_model and TREE_MODEL.exists()
    for it in items:
        try:
            clip_dir = Path(it.get("path") or "")
            if not clip_dir.exists(): continue
            fid = it.get("id") or clip_dir.name
            motion = float(it.get("motion_score") or 0)
            label = labels_map.get(fid, severity_from_motion(motion))
            conf, method = 0.65, "bootstrap_rank"
            try: inds = compute_indicators(clip_dir)
            except Exception as e:
                inds = None; errors.append({"id": fid, "stage": "features", "error": str(e)})
            if use_ml and inds is not None:
                try:
                    from ml.trees import predict_proba_vec
                    pred, conf, _ = predict_proba_vec(vectorize(inds))
                    label, method = pred, "ml_model"
                except (ModelNotFoundError, PredictionError) as e:
                    errors.append({"id": fid, "stage": "predict", "error": str(e)})
                except Exception as e:
                    errors.append({"id": fid, "stage": "predict", "error": str(e)})
            if inds is not None:
                try: save_fragment_features(fid, inds, label=label)
                except Exception as e: print(f"[triage] save {fid}: {e}")
            dest = CLASS_DIRS.get(label, CLASS_DIRS["normal"]) / clip_dir.name
            if dest.exists(): shutil.rmtree(dest)
            shutil.copytree(clip_dir, dest)
            meta = dict(it); meta.update({"label": label, "confidence": round(float(conf), 3), "triage_method": method})
            (dest / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
            counts[label] = counts.get(label, 0) + 1
            print(f"[triage] {fid} → {label} ({method})")
        except Exception as e:
            errors.append({"id": it.get("id"), "stage": "triage", "error": str(e)})
    report = {"counts": counts, "total": sum(counts.values()), "errors": errors}
    try:
        (CLASS_DIRS["normal"].parent / "triage_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e: print(f"[triage] rapport: {e}")
    print(f"[triage] normal={counts.get('normal',0)} urgent={counts.get('urgent',0)} critique={counts.get('critique',0)}")
    return counts
