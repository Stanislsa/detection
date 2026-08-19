"""
Gestion des données déséquilibrées — classes normal / urgent / critique.

Stratégies :
  - class_weight (délégué au modèle)
  - random oversampling avec jitter
  - random undersampling de la majorité
  - SMOTE (si imblearn disponible)
  - combinaison auto selon ratio d'imbalance
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import numpy as np

from ml.config import CLASSES, MODELS_DIR, RANDOM_STATE

IMBALANCE_LOG = MODELS_DIR / "imbalance_report.json"


def class_counts(y: np.ndarray) -> Dict[str, int]:
    y = np.asarray(y)
    return {c: int(np.sum(y == c)) for c in CLASSES}


def imbalance_ratio(y: np.ndarray) -> float:
    counts = [v for v in class_counts(y).values() if v > 0]
    if not counts or min(counts) == 0:
        return float("inf")
    return float(max(counts) / min(counts))


def compute_class_weights(y: np.ndarray) -> Dict[str, float]:
    """Poids inversement proportionnels à la fréquence (somme = n_classes)."""
    y = np.asarray(y)
    n = len(y)
    k = len(CLASSES)
    weights = {}
    for c in CLASSES:
        cnt = int(np.sum(y == c))
        weights[c] = float(n / (k * cnt)) if cnt > 0 else 0.0
    return weights


def oversample_jitter(
    X: np.ndarray,
    y: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    noise_scale: float = 0.05,
    target: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Oversampling avec bruit gaussien léger sur les features."""
    rng = rng or np.random.default_rng(RANDOM_STATE)
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    counts = class_counts(y)
    present = [c for c, v in counts.items() if v > 0]
    if not present:
        return X, y
    target = int(target or max(counts[c] for c in present))
    Xs, ys = [X], [y]
    for c in present:
        idx = np.where(y == c)[0]
        need = target - len(idx)
        if need <= 0:
            continue
        choice = rng.choice(idx, size=need, replace=True)
        noise = rng.normal(0, noise_scale, size=(need, X.shape[1]))
        # scale noise by feature std
        std = np.std(X, axis=0)
        std = np.where(std < 1e-8, 1.0, std)
        Xs.append(X[choice] + noise * std)
        ys.append(np.full(need, c))
    return np.vstack(Xs), np.concatenate(ys)


def undersample_majority(
    X: np.ndarray,
    y: np.ndarray,
    rng: Optional[np.random.Generator] = None,
    target: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Réduit la classe majoritaire au niveau de la 2e plus grande (ou target)."""
    rng = rng or np.random.default_rng(RANDOM_STATE)
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    counts = class_counts(y)
    present = sorted([c for c, v in counts.items() if v > 0], key=lambda c: -counts[c])
    if len(present) < 2:
        return X, y
    if target is None:
        target = counts[present[1]]  # 2e classe
    keep_idx = []
    for c in present:
        idx = np.where(y == c)[0]
        if len(idx) > target and c == present[0]:
            keep_idx.append(rng.choice(idx, size=target, replace=False))
        else:
            keep_idx.append(idx)
    keep = np.concatenate(keep_idx)
    rng.shuffle(keep)
    return X[keep], y[keep]


def smote_balance(
    X: np.ndarray,
    y: np.ndarray,
    random_state: int = RANDOM_STATE,
) -> Tuple[np.ndarray, np.ndarray, str]:
    """SMOTE si imblearn dispo, sinon oversample_jitter."""
    try:
        from imblearn.over_sampling import SMOTE
        counts = class_counts(y)
        min_c = min(v for v in counts.values() if v > 0)
        k = max(1, min(5, min_c - 1))
        if min_c < 2:
            X2, y2 = oversample_jitter(X, y)
            return X2, y2, "oversample_jitter_fallback_min_class<2"
        sm = SMOTE(random_state=random_state, k_neighbors=k)
        X2, y2 = sm.fit_resample(X, y)
        return np.asarray(X2), np.asarray(y2), "smote"
    except Exception as e:
        X2, y2 = oversample_jitter(X, y)
        return X2, y2, f"oversample_jitter_fallback ({e})"


def balance_dataset(
    X: np.ndarray,
    y: np.ndarray,
    strategy: str = "auto",
    rng: Optional[np.random.Generator] = None,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Rééquilibre selon strategy:
      auto | oversample | undersample | smote | none | class_weight_only
    """
    rng = rng or np.random.default_rng(RANDOM_STATE)
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    before = class_counts(y)
    ratio = imbalance_ratio(y)

    if strategy == "auto":
        if ratio <= 1.5:
            strategy = "none"
        elif ratio <= 4:
            strategy = "smote"
        elif ratio <= 10:
            strategy = "oversample"
        else:
            strategy = "oversample"  # SMOTE fragile si extrême

    method_used = strategy
    if strategy == "none" or strategy == "class_weight_only":
        X2, y2 = X, y
        method_used = strategy
    elif strategy == "undersample":
        X2, y2 = undersample_majority(X, y, rng)
        method_used = "undersample"
    elif strategy == "smote":
        X2, y2, method_used = smote_balance(X, y)
    else:
        X2, y2 = oversample_jitter(X, y, rng)
        method_used = "oversample_jitter"

    after = class_counts(y2)
    report = {
        "started_at": datetime.utcnow().isoformat(),
        "strategy_requested": strategy,
        "method_used": method_used,
        "imbalance_ratio_before": round(ratio, 3),
        "imbalance_ratio_after": round(imbalance_ratio(y2), 3),
        "counts_before": before,
        "counts_after": after,
        "n_before": int(len(y)),
        "n_after": int(len(y2)),
        "class_weights": compute_class_weights(y),
        "note": "class_weight=balanced reste activé dans les arbres même après resampling",
    }
    try:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        IMBALANCE_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    print(
        f"[imbalance] {method_used}: {before} → {after} "
        f"(ratio {report['imbalance_ratio_before']} → {report['imbalance_ratio_after']})"
    )
    return X2, y2, report
