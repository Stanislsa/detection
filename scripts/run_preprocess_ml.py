#!/usr/bin/env python3
"""Prétraitement ordonné + modèle ML.

  1 Données brutes
  2 Exploration (EDA + fuites)
  3 Nettoyage
  4 Manquants / aberrants
  5-6 Split train/val/test puis encodage + normalisation
  7 Rééquilibrage train
  8 Modèle ML
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ml.preprocess import PreprocessPipeline, run_full_pipeline

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-hyper", action="store_true")
    ap.add_argument("--preprocess-only", action="store_true")
    args = ap.parse_args()
    if args.preprocess_only:
        pipe = PreprocessPipeline()
        bundles = pipe.run()
        print({k: v.n for k, v in bundles.items() if hasattr(v, "n")})
        return 0
    r = run_full_pipeline(skip_hyper=args.skip_hyper)
    print(r)
    return 0 if r.get("status") == "completed" else 1

if __name__ == "__main__":
    raise SystemExit(main())
