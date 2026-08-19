#!/usr/bin/env python3
"""Explore pipelines de données + optimise hyperparams + sauvegarde versionnée."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.preprocess import PreprocessPipeline
from ml.pipeline_optimize import (
    explore_and_optimize, save_pipeline_versioned, list_saved_pipelines, load_pipeline_saved
)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-iter", type=int, default=16)
    ap.add_argument("--list", action="store_true", help="Lister pipelines sauvés")
    ap.add_argument("--preprocess-only", action="store_true")
    args = ap.parse_args()

    if args.list:
        for p in list_saved_pipelines():
            print(p.get("version"), p.get("clf"), p.get("path"))
        return 0

    pipe_prep = PreprocessPipeline()
    bundles = pipe_prep.run()
    if args.preprocess_only:
        print({k: b.n for k, b in bundles.items() if hasattr(b, "n")})
        return 0

    tr = bundles["train_raw_unscaled"]
    from ml.imbalance import balance_dataset
    import numpy as np
    X, y, _ = balance_dataset(tr.X, tr.y, strategy="auto", rng=np.random.default_rng(42))
    best, report = explore_and_optimize(X, y, n_iter=args.n_iter)
    paths = save_pipeline_versioned(best, meta={"search": report.get("best")}, tag="optimized")
    print("Best:", report.get("best"))
    print("Saved:", paths)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
