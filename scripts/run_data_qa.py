#!/usr/bin/env python3
"""QA données : checklist + EDA + fuites (sans entraîner)."""
from __future__ import annotations
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ml.features import build_feature_table
from ml.indicators import INDICATOR_IDS
from ml.config import CLASSES
from ml.data_checklist import run_data_checklist, impute_missing
from ml.eda import run_eda, print_eda
from ml.leakage import detect_leakage, print_leakage_report
import numpy as np

def main():
    X, y, ids = build_feature_table()
    mask = np.array([yi in CLASSES for yi in y]) if len(y) else np.array([], dtype=bool)
    if mask.size and mask.any():
        X, y = X[mask], y[mask]
        ids = [ids[i] for i, m in enumerate(mask) if m]
    print(f"QA sur n={len(y)} d={X.shape[1] if len(X) else 0}")
    if len(y) == 0:
        print("Aucune feature — lancez d'abord fragmentation + extract features.")
        return 1
    try:
        run_data_checklist(X, y, ids, feature_names=INDICATOR_IDS, block_on_fail=False)
    except Exception as e:
        print("checklist:", e)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
