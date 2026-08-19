"""
Analyse exploratoire des données (EDA) — features image + squelette.

Produits :
  - stats descriptives par feature
  - distribution des classes
  - corrélations
  - top features discriminantes (ANOVA F / effet taille)
  - rapport JSON + résumé console
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from ml.config import CLASSES, MODELS_DIR
from ml.indicators import INDICATOR_IDS

EDA_LOG = MODELS_DIR / "eda_report.json"


def _safe_stats(col: np.ndarray) -> Dict[str, float]:
    col = col[np.isfinite(col)]
    if col.size == 0:
        return {"count": 0, "mean": 0.0, "std": 0.0, "min": 0.0, "p25": 0.0, "p50": 0.0, "p75": 0.0, "max": 0.0}
    return {
        "count": int(col.size),
        "mean": round(float(np.mean(col)), 6),
        "std": round(float(np.std(col)), 6),
        "min": round(float(np.min(col)), 6),
        "p25": round(float(np.percentile(col, 25)), 6),
        "p50": round(float(np.percentile(col, 50)), 6),
        "p75": round(float(np.percentile(col, 75)), 6),
        "max": round(float(np.max(col)), 6),
    }


def _anova_f_scores(X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> List[Dict[str, Any]]:
    """Score F one-way ANOVA par feature (discrimination multi-classes)."""
    scores = []
    classes = [c for c in CLASSES if np.any(y == c)]
    if len(classes) < 2:
        return scores
    for j in range(X.shape[1]):
        name = feature_names[j] if j < len(feature_names) else f"f{j}"
        groups = [X[y == c, j] for c in classes]
        groups = [g[np.isfinite(g)] for g in groups]
        groups = [g for g in groups if len(g) > 0]
        if len(groups) < 2:
            scores.append({"feature": name, "f_score": 0.0})
            continue
        all_v = np.concatenate(groups)
        grand = np.mean(all_v)
        ss_between = sum(len(g) * (np.mean(g) - grand) ** 2 for g in groups)
        ss_within = sum(np.sum((g - np.mean(g)) ** 2) for g in groups)
        df_b = len(groups) - 1
        df_w = len(all_v) - len(groups)
        if df_w <= 0 or ss_within <= 1e-12:
            f = 0.0
        else:
            f = (ss_between / df_b) / (ss_within / df_w)
        scores.append({"feature": name, "f_score": round(float(f), 4)})
    scores.sort(key=lambda x: -x["f_score"])
    return scores


def run_eda(
    X: np.ndarray,
    y: np.ndarray,
    ids: Optional[Sequence[str]] = None,
    feature_names: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    feature_names = list(feature_names or INDICATOR_IDS)
    ids = list(ids) if ids is not None else []
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    n, d = X.shape if X.ndim == 2 else (0, 0)

    # Classes
    class_counts = {c: int(np.sum(y == c)) for c in CLASSES}
    class_ratios = {c: round(class_counts[c] / max(n, 1), 4) for c in CLASSES}

    # Stats par feature
    per_feature = {}
    for j in range(d):
        name = feature_names[j] if j < len(feature_names) else f"f{j}"
        per_feature[name] = _safe_stats(X[:, j])

    # Stats par classe (moyennes)
    means_by_class: Dict[str, Dict[str, float]] = {}
    for c in CLASSES:
        mask = y == c
        if not np.any(mask):
            continue
        means_by_class[c] = {}
        for j in range(min(d, len(feature_names))):
            means_by_class[c][feature_names[j]] = round(float(np.nanmean(X[mask, j])), 6)

    # Corrélation inter-features (échantillon max 30 features pour taille)
    corr_summary = {}
    if n > 3 and d > 1:
        max_f = min(d, 30)
        sub = np.nan_to_num(X[:, :max_f], nan=0.0)
        with np.errstate(invalid="ignore"):
            cm = np.corrcoef(sub, rowvar=False)
        # paires les plus corrélées
        pairs = []
        for i in range(max_f):
            for j in range(i + 1, max_f):
                v = cm[i, j]
                if np.isfinite(v) and abs(v) >= 0.85:
                    pairs.append({
                        "f1": feature_names[i],
                        "f2": feature_names[j],
                        "corr": round(float(v), 4),
                    })
        pairs.sort(key=lambda x: -abs(x["corr"]))
        corr_summary = {"high_pairs": pairs[:15], "n_features_analyzed": max_f}

    # Discrimination
    f_scores = _anova_f_scores(X, y, feature_names) if n and d else []
    top_disc = f_scores[:12]

    # Familles skeleton vs image
    sk_idx = [j for j, nme in enumerate(feature_names[:d]) if str(nme).startswith("sk_")]
    img_idx = [j for j in range(d) if j not in sk_idx]
    family = {
        "n_skeleton_features": len(sk_idx),
        "n_image_features": len(img_idx),
        "skeleton_nan_rate": round(float(np.mean(~np.isfinite(X[:, sk_idx]))) if sk_idx else 0.0, 4),
        "image_nan_rate": round(float(np.mean(~np.isfinite(X[:, img_idx]))) if img_idx else 0.0, 4),
    }

    report = {
        "started_at": datetime.utcnow().isoformat(),
        "n_samples": n,
        "n_features": d,
        "feature_names": feature_names[:d],
        "class_counts": class_counts,
        "class_ratios": class_ratios,
        "per_feature_stats": per_feature,
        "means_by_class": means_by_class,
        "correlation": corr_summary,
        "top_discriminative_features": top_disc,
        "feature_families": family,
        "insights": _insights(class_counts, top_disc, family, n),
    }
    try:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        EDA_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    return report


def _insights(counts, top_disc, family, n) -> List[str]:
    tips = []
    if n < 30:
        tips.append("Peu d'échantillons (<30) : F1 instable — ajouter des vidéos labellisées.")
    present = [c for c, v in counts.items() if v > 0]
    if len(present) < 3:
        tips.append(f"Classes absentes ou vides: {[c for c, v in counts.items() if v == 0]}")
    if counts.get("critique", 0) < 3:
        tips.append("Classe 'critique' sous-représentée — risque de mauvais recall sur chutes graves.")
    if top_disc:
        top = top_disc[0]
        tips.append(f"Feature la plus discriminante: {top['feature']} (F={top['f_score']})")
    sk_top = [t for t in top_disc if str(t["feature"]).startswith("sk_")]
    if sk_top:
        tips.append(f"Squelette utile: {sk_top[0]['feature']} dans le top discriminatif.")
    elif family.get("n_skeleton_features", 0) > 0:
        tips.append("Features squelette présentes mais peu discriminantes — vérifier MediaPipe / qualité pose.")
    return tips


def print_eda(report: Dict[str, Any]) -> None:
    print("\n" + "-" * 60)
    print("  EDA — analyse exploratoire")
    print("-" * 60)
    print(f"  n={report.get('n_samples')}  d={report.get('n_features')}")
    print(f"  Classes: {report.get('class_counts')}")
    fam = report.get("feature_families") or {}
    print(f"  Features image={fam.get('n_image_features')}  squelette={fam.get('n_skeleton_features')}")
    print("  Top discriminatives:")
    for t in (report.get("top_discriminative_features") or [])[:8]:
        print(f"    - {t['feature']}: F={t['f_score']}")
    for tip in report.get("insights") or []:
        print(f"  • {tip}")
    print(f"  Rapport: {EDA_LOG}")
    print("-" * 60 + "\n")
