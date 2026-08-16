"""Pipeline: videos → fragments → features → tri → arbres."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ml.config import VIDEO_DIR, FEATURES_DIR, MODELS_DIR, PIPELINE_LOG
from ml.fragment import fragment_all, discover_videos
from ml.features import extract_and_store_from_raw, extract_and_store_from_classes, build_feature_table
from ml.triage import triage_all
from ml.trees import train_trees, describe_trees
from ml.indicators import catalog_as_dict, indicators_by_family

def run_pipeline(video_dir=None, skip_train=False):
    print("="*64); print("  SENTINELAI — Features + Arbres + Tri"); print("="*64)
    for fam, inds in indicators_by_family().items():
        print(f"  {fam}: {', '.join(i.id for i in inds)}")
    metas = fragment_all(Path(video_dir) if video_dir else None)
    if not metas: return {"status": "no_videos"}
    rows = extract_and_store_from_raw(); build_feature_table(rows)
    counts1 = triage_all(use_model=False)
    rows2 = extract_and_store_from_classes(); build_feature_table(rows2)
    train_report = {"status": "skipped"}
    if not skip_train:
        train_report = train_trees()
        counts2 = triage_all(use_model=True)
    else:
        counts2 = counts1
    summary = {"status": "completed", "n_fragments": len(metas), "indicators": catalog_as_dict(),
               "features_dir": str(FEATURES_DIR), "triage_initial": counts1, "triage_final": counts2,
               "trees": train_report.get("trees"), "trees_description": describe_trees(),
               "finished_at": datetime.utcnow().isoformat()}
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PIPELINE_LOG.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[pipeline] → {PIPELINE_LOG}"); return summary

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--video-dir", type=Path, default=None)
    p.add_argument("--skip-train", action="store_true")
    p.add_argument("--list-indicators", action="store_true")
    p.add_argument("--describe-trees", action="store_true")
    args = p.parse_args(argv)
    if args.list_indicators:
        print(json.dumps(catalog_as_dict(), indent=2, ensure_ascii=False)); return 0
    if args.describe_trees:
        print(json.dumps(describe_trees(), indent=2, ensure_ascii=False)); return 0
    (args.video_dir or VIDEO_DIR).mkdir(parents=True, exist_ok=True)
    run_pipeline(args.video_dir, args.skip_train); return 0

if __name__ == "__main__":
    raise SystemExit(main())
