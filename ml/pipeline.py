"""Pipeline apprentissage: hyperparams + F1 + erreurs."""
from __future__ import annotations
import argparse, json, sys, traceback
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ml.config import VIDEO_DIR, FEATURES_DIR, MODELS_DIR, PIPELINE_LOG, MIN_ACCEPTABLE_F1_MACRO
from ml.fragment import fragment_all, discover_videos
from ml.features import extract_and_store_from_raw, extract_and_store_from_classes, build_feature_table
from ml.triage import triage_all
from ml.trees import train_trees, describe_trees
from ml.indicators import catalog_as_dict, indicators_by_family
from ml.errors import LearningError, safe_call

def run_pipeline(video_dir=None, skip_train=False, skip_hyper=False):
    print("=" * 64); print("  SENTINELAI — APPRENTISSAGE (image + SQUELETTE + F1)"); print("=" * 64)
    try:
        from ml.skeleton_features import skeleton_available
        print("  MediaPipe Pose:", "OK" if skeleton_available() else "INDISPONIBLE (features sk_* = 0)")
    except Exception as e:
        print("  MediaPipe Pose: erreur", e)
    errors = []
    for fam, inds in indicators_by_family().items():
        print(f"  [{fam}] {', '.join(i.id for i in inds)}")
    vdir = Path(video_dir) if video_dir else None
    try: videos = discover_videos(vdir)
    except Exception as e: errors.append({"stage": "discover", "error": str(e)}); videos = []
    print(f"\n[pipeline] {len(videos)} vidéo(s)")
    if not videos: return {"status": "no_videos", "errors": errors}
    print("\n>>> 1/6 Fragmentation")
    metas, err = safe_call(fragment_all, vdir, label="fragment")
    if err: errors.append(err)
    if not metas: return {"status": "no_fragments", "errors": errors}
    print("\n>>> 2/6 Features")
    rows, err = safe_call(extract_and_store_from_raw, label="features_raw")
    if err: errors.append(err)
    safe_call(build_feature_table, rows, label="feature_table")
    print("\n>>> 3/6 Tri bootstrap")
    counts1, err = safe_call(triage_all, False, default={}, label="triage_bootstrap")
    if err: errors.append(err)
    print("\n>>> 4/6 Features labellisées")
    rows2, err = safe_call(extract_and_store_from_classes, label="features_classes")
    if err: errors.append(err)
    safe_call(build_feature_table, rows2, label="feature_table2")
    train_report = {"status": "skipped"}; counts2 = counts1 or {}
    if not skip_train:
        print("\n>>> 5/6 Train + hyperparam + analyse F1")
        try:
            train_report = train_trees(skip_hyper=skip_hyper)
            if train_report.get("errors"): errors.extend(train_report["errors"])
        except LearningError as e:
            train_report = {"status": "failed", "errors": [e.to_dict()]}; errors.append(e.to_dict())
        except Exception as e:
            train_report = {"status": "failed", "error": str(e)}
            errors.append({"error": {"code": "UNEXPECTED", "message": str(e)}})
        if train_report.get("status") == "completed":
            print("\n>>> 6/6 Re-tri modèle")
            counts2, err = safe_call(triage_all, True, default=counts1, label="triage_ml")
            if err: errors.append(err)
    quality = train_report.get("quality", "n/a")
    summary = {"status": "completed" if train_report.get("status") in ("completed","skipped") else "degraded",
        "n_videos": len(videos), "n_fragments": len(metas) if metas else 0,
        "triage_final": counts2, "train": {"status": train_report.get("status"), "quality": quality,
            "best_model": train_report.get("best_model"),
            "f1_macro": (train_report.get("f1_analysis") or {}).get("f1_macro"),
            "hyperparam": train_report.get("hyperparam")},
        "errors": errors, "n_errors": len(errors), "finished_at": datetime.utcnow().isoformat()}
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PIPELINE_LOG.write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\n[pipeline] quality={quality} errors={len(errors)} → {PIPELINE_LOG}")
    return summary

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--video-dir", type=Path, default=None)
    p.add_argument("--skip-train", action="store_true")
    p.add_argument("--skip-hyper", action="store_true")
    p.add_argument("--ordered-preprocess", action="store_true",
                   help="Pipeline ordonné: brut→EDA→clean→split→scale→ML")
    p.add_argument("--list-indicators", action="store_true")
    p.add_argument("--describe-trees", action="store_true")
    args = p.parse_args(argv)
    if getattr(args, "ordered_preprocess", False):
        from ml.preprocess import run_full_pipeline
        # Si features absentes, lancer d'abord extract classique sans train
        r = run_full_pipeline(skip_hyper=args.skip_hyper)
        print(r)
        return 0 if r.get("status") == "completed" else 1
    if args.list_indicators:
        print(json.dumps(catalog_as_dict(), indent=2, ensure_ascii=False)); return 0
    if args.describe_trees:
        print(json.dumps(describe_trees(), indent=2, ensure_ascii=False)); return 0
    (args.video_dir or VIDEO_DIR).mkdir(parents=True, exist_ok=True)
    r = run_pipeline(args.video_dir, args.skip_train, args.skip_hyper)
    if r.get("status") == "no_videos": return 2
    if r.get("train", {}).get("status") == "failed": return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
