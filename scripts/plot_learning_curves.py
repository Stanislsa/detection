#!/usr/bin/env python3
"""Trace les courbes d'apprentissage (F1 train vs val)."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from ml.config import CLASSES
from ml.features import build_feature_table
from ml.learning_curves import run_learning_curves
from ml.pipeline_optimize import load_pipeline_saved, make_full_pipeline
from ml.imbalance import balance_dataset

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", type=int, default=5)
    ap.add_argument("--from-saved", action="store_true", help="Utiliser le pipeline sauvé")
    args = ap.parse_args()

    X, y, ids = build_feature_table()
    mask = np.array([yi in CLASSES for yi in y]) if len(y) else np.array([], dtype=bool)
    if mask.size and mask.any():
        X, y = X[mask], y[mask]
    if len(y) < 6:
        print("Pas assez d'échantillons — lancez d'abord l'extraction de features.")
        return 1

    X, y, _ = balance_dataset(X, y, strategy="auto")
    pipe = None
    if args.from_saved:
        try:
            pipe, _ = load_pipeline_saved()
            print("Pipeline chargé depuis disk")
        except Exception as e:
            print("load failed:", e)
    if pipe is None:
        pipe = make_full_pipeline("extra_trees", scaler="standard")

    report = run_learning_curves(X, y, pipe=pipe, cv=args.cv)
    print("final_val", report.get("final_val"), "gap", report.get("final_gap"))
    print("plots", report.get("plots"))
    return 0 if report.get("status") == "ok" else 1

if __name__ == "__main__":
    raise SystemExit(main())
