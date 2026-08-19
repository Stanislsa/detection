"""
Courbes d'apprentissage (learning curves) — SentinelAI.

Affiche l'évolution F1-macro train vs validation selon la taille du jeu d'entraînement.
Utile pour diagnostiquer biais (underfit) vs variance (overfit).

Sorties PNG :
  data/models/plots/learning_curve.png
  data/models/plots/learning_curve_detail.png
  data/models/learning_curve.json
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from ml.config import CLASSES, MODELS_DIR, RANDOM_STATE, HYPERPARAM_CV
from ml.indicators import INDICATOR_IDS

PLOTS_DIR = MODELS_DIR / "plots"
LC_JSON = MODELS_DIR / "learning_curve.json"


def compute_learning_curve(
    pipe: Any,
    X: np.ndarray,
    y: np.ndarray,
    *,
    cv: int = 5,
    train_sizes: Optional[Sequence[float]] = None,
    scoring: str = "f1_macro",
    n_jobs: int = -1,
    random_state: int = RANDOM_STATE,
) -> Dict[str, Any]:
    """
    Calcule les scores train/val pour différentes tailles d'échantillon.
    `pipe` : sklearn Pipeline (ou estimateur compatible).
    """
    from sklearn.model_selection import learning_curve, StratifiedKFold
    from sklearn.base import clone

    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    if train_sizes is None:
        train_sizes = np.linspace(0.2, 1.0, 8)

    counts = {c: int(np.sum(y == c)) for c in CLASSES}
    min_c = min((v for v in counts.values() if v > 0), default=2)
    n_splits = min(int(cv), max(2, min_c))
    if len(y) < n_splits * 2:
        n_splits = 2

    cv_splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    print(f"[lc] learning_curve n={len(y)} cv={n_splits} sizes={list(np.round(train_sizes, 2))}…")
    try:
        sizes_abs, train_scores, val_scores = learning_curve(
            clone(pipe),
            X, y,
            train_sizes=train_sizes,
            cv=cv_splitter,
            scoring=scoring,
            n_jobs=n_jobs,
            shuffle=True,
            random_state=random_state,
            error_score=0.0,
        )
    except Exception as e:
        print(f"[lc] ÉCHEC: {e}")
        return {"status": "failed", "error": str(e)}

    train_mean = train_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    val_mean = val_scores.mean(axis=1)
    val_std = val_scores.std(axis=1)
    gap = train_mean - val_mean

    report = {
        "status": "ok",
        "started_at": datetime.utcnow().isoformat(),
        "scoring": scoring,
        "cv_folds": n_splits,
        "n_samples": int(len(y)),
        "n_features": int(X.shape[1]) if X.ndim == 2 else 0,
        "train_sizes_abs": [int(s) for s in sizes_abs],
        "train_sizes_frac": [round(float(s) / max(len(y), 1), 4) for s in sizes_abs],
        "train_mean": [round(float(x), 4) for x in train_mean],
        "train_std": [round(float(x), 4) for x in train_std],
        "val_mean": [round(float(x), 4) for x in val_mean],
        "val_std": [round(float(x), 4) for x in val_std],
        "gap_mean": [round(float(x), 4) for x in gap],
        "final_train": round(float(train_mean[-1]), 4),
        "final_val": round(float(val_mean[-1]), 4),
        "final_gap": round(float(gap[-1]), 4),
        "diagnosis": _diagnose(float(train_mean[-1]), float(val_mean[-1]), float(gap[-1])),
    }
    try:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        LC_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    return report


def _diagnose(train: float, val: float, gap: float) -> Dict[str, str]:
    if train < 0.55 and val < 0.55:
        level, msg = "underfit", "Scores bas train & val → modèle trop simple ou features insuffisantes."
    elif gap > 0.15:
        level, msg = "overfit", "Écart train/val élevé → overfit. Régulariser, plus de données, ou réduire profondeur."
    elif gap > 0.08:
        level, msg = "mild_overfit", "Léger overfit. Surveiller avec plus de samples."
    elif val >= 0.70:
        level, msg = "good", "Bon compromis biais/variance."
    else:
        level, msg = "improvable", "Val moyenne — enrichir données / features squelette."
    return {"level": level, "message": msg}


def plot_learning_curve(report: Dict[str, Any], title: str = "Courbe d'apprentissage") -> Optional[str]:
    """Trace train vs val ± std."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[lc] matplotlib absent")
        return None
    if report.get("status") != "ok":
        return None

    sizes = report["train_sizes_abs"]
    tr_m, tr_s = np.array(report["train_mean"]), np.array(report["train_std"])
    va_m, va_s = np.array(report["val_mean"]), np.array(report["val_std"])

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.fill_between(sizes, tr_m - tr_s, tr_m + tr_s, alpha=0.15, color="#2563EB")
    ax.fill_between(sizes, va_m - va_s, va_m + va_s, alpha=0.15, color="#DC2626")
    ax.plot(sizes, tr_m, "o-", color="#2563EB", label="Train (F1-macro)", lw=2)
    ax.plot(sizes, va_m, "o-", color="#DC2626", label="Validation CV (F1-macro)", lw=2)
    ax.set_xlabel("Nombre d'échantillons d'entraînement")
    ax.set_ylabel(report.get("scoring", "score"))
    ax.set_title(title)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    diag = (report.get("diagnosis") or {}).get("message", "")
    ax.text(0.02, 0.02, diag, transform=ax.transAxes, fontsize=8, color="#374151",
            verticalalignment="bottom", wrap=True)
    path = PLOTS_DIR / "learning_curve.png"
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[lc] {path}")
    return str(path)


def plot_learning_curve_detail(report: Dict[str, Any]) -> Optional[str]:
    """Courbe principale + gap train-val."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None
    if report.get("status") != "ok":
        return None

    sizes = report["train_sizes_abs"]
    tr_m = np.array(report["train_mean"])
    va_m = np.array(report["val_mean"])
    gap = np.array(report["gap_mean"])

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    axes[0].plot(sizes, tr_m, "o-", color="#2563EB", label="Train")
    axes[0].plot(sizes, va_m, "o-", color="#DC2626", label="Val CV")
    axes[0].set_title("F1-macro vs taille train")
    axes[0].set_xlabel("n train")
    axes[0].set_ylabel("F1-macro")
    axes[0].set_ylim(0, 1.05)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].bar(range(len(sizes)), gap, color=["#DC2626" if g > 0.12 else "#F59E0B" if g > 0.08 else "#10B981" for g in gap])
    axes[1].set_xticks(range(len(sizes)))
    axes[1].set_xticklabels([str(s) for s in sizes], rotation=45)
    axes[1].axhline(0.12, color="#DC2626", ls="--", lw=1, label="seuil overfit")
    axes[1].set_title("Écart train − val (overfit)")
    axes[1].set_ylabel("gap")
    axes[1].legend(fontsize=8)
    axes[1].grid(axis="y", alpha=0.3)

    diag = report.get("diagnosis") or {}
    fig.suptitle(
        f"Learning curves — {diag.get('level', '?').upper()} | "
        f"final val={report.get('final_val')} gap={report.get('final_gap')}",
        fontsize=11,
    )
    path = PLOTS_DIR / "learning_curve_detail.png"
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[lc] {path}")
    return str(path)


def run_learning_curves(
    X: np.ndarray,
    y: np.ndarray,
    pipe: Optional[Any] = None,
    *,
    cv: int = 5,
) -> Dict[str, Any]:
    """Calcule + trace les courbes d'apprentissage."""
    if pipe is None:
        try:
            from ml.pipeline_optimize import make_full_pipeline
            pipe = make_full_pipeline("extra_trees", scaler="standard")
        except Exception:
            from ml.sklearn_pipeline import build_pipeline
            pipe = build_pipeline("extra_trees")

    report = compute_learning_curve(pipe, X, y, cv=cv)
    paths = {}
    if report.get("status") == "ok":
        paths["curve"] = plot_learning_curve(report)
        paths["detail"] = plot_learning_curve_detail(report)
        print(f"[lc] Diagnostic: {report['diagnosis']['level']} — {report['diagnosis']['message']}")
    report["plots"] = paths
    return report
