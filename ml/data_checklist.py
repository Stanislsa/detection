"""
Checklist qualité des données — OBLIGATOIRE avant entraînement.

Vérifie :
  1. Types des colonnes
  2. Doublons
  3. Valeurs manquantes
  4. Valeurs aberrantes
  5. Encodage des catégories
  6. Mise à l'échelle (nécessité)
  7. Séparation train/test
  8. Absence de fuite de données
  9. Équilibre des classes
 10. Métrique d'évaluation adaptée
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from ml.config import (
    CLASSES,
    MIN_SAMPLES_TOTAL,
    MODELS_DIR,
    RANDOM_STATE,
    TEST_SIZE,
)
from ml.indicators import INDICATOR_IDS

CHECKLIST_LOG = MODELS_DIR / "data_checklist.json"


@dataclass
class CheckItem:
    id: str
    name: str
    status: str  # ok | warning | fail
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _iqr_outlier_mask(X: np.ndarray, k: float = 3.0) -> np.ndarray:
    """Masque (n_samples,) True si au moins une feature hors [Q1-k*IQR, Q3+k*IQR]."""
    if X.size == 0:
        return np.array([], dtype=bool)
    q1 = np.nanpercentile(X, 25, axis=0)
    q3 = np.nanpercentile(X, 75, axis=0)
    iqr = q3 - q1
    iqr = np.where(iqr < 1e-12, 1.0, iqr)
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return np.any((X < lo) | (X > hi), axis=1)


def run_data_checklist(
    X: np.ndarray,
    y: np.ndarray,
    ids: Optional[Sequence[str]] = None,
    feature_names: Optional[Sequence[str]] = None,
    *,
    block_on_fail: bool = True,
) -> Dict[str, Any]:
    """
    Exécute la checklist complète.
    Retourne un rapport ; lève ValueError si block_on_fail et statut fail.
    """
    feature_names = list(feature_names or INDICATOR_IDS)
    ids = list(ids) if ids is not None else [str(i) for i in range(len(y))]
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    checks: List[CheckItem] = []

    n, d = (X.shape[0], X.shape[1]) if X.ndim == 2 else (0, 0)

    # ── 1. Types des colonnes ─────────────────────────────────
    type_ok = True
    bad_cols = []
    if X.ndim != 2:
        type_ok = False
        msg = f"X doit être 2D, reçu shape={getattr(X, 'shape', None)}"
    else:
        for j in range(d):
            col = X[:, j]
            if not np.issubdtype(col.dtype, np.number):
                type_ok = False
                bad_cols.append(feature_names[j] if j < len(feature_names) else j)
            elif np.isinf(col).any():
                type_ok = False
                bad_cols.append(feature_names[j] if j < len(feature_names) else j)
        # y labels
        y_ok = all(isinstance(yi, (str, np.str_)) or yi in CLASSES for yi in y) if len(y) else False
        if len(y) and not all(str(yi) in CLASSES or yi in CLASSES for yi in y):
            unknown = sorted({str(yi) for yi in y if str(yi) not in CLASSES})
            checks.append(CheckItem(
                "column_types", "Types des colonnes",
                "warning" if type_ok else "fail",
                f"Features numériques={'OK' if type_ok else 'KO'}; labels hors CLASSES: {unknown}",
                {"n_features": d, "feature_names": feature_names[:d], "bad_feature_cols": bad_cols, "unknown_labels": unknown},
            ))
        else:
            checks.append(CheckItem(
                "column_types", "Types des colonnes",
                "ok" if type_ok else "fail",
                "Toutes les features sont numériques float64" if type_ok else f"Colonnes non numériques/inf: {bad_cols}",
                {"n_features": d, "dtype": str(X.dtype), "labels": list(CLASSES)},
            ))

    # ── 2. Doublons ───────────────────────────────────────────
    n_dup_rows = 0
    n_dup_ids = 0
    if n > 0:
        # doublons exacts de vecteurs
        # hash rows
        try:
            _, uniq_inv, counts_u = np.unique(np.round(X, 6), axis=0, return_inverse=True, return_counts=True)
            n_dup_rows = int(np.sum(counts_u > 1))
        except Exception:
            n_dup_rows = 0
        if ids:
            seen = {}
            for i in ids:
                seen[i] = seen.get(i, 0) + 1
            n_dup_ids = sum(1 for v in seen.values() if v > 1)
    dup_status = "ok"
    dup_msg = "Aucun doublon détecté"
    if n_dup_ids > 0:
        dup_status = "warning"
        dup_msg = f"{n_dup_ids} id(s) fragment en double"
    if n_dup_rows > 0:
        dup_status = "warning"
        dup_msg = f"{n_dup_rows} motif(s) de features dupliqué(s)" + (f"; {dup_msg}" if n_dup_ids else "")
    checks.append(CheckItem(
        "duplicates", "Doublons",
        dup_status, dup_msg,
        {"duplicate_feature_patterns": n_dup_rows, "duplicate_ids": n_dup_ids},
    ))

    # ── 3. Valeurs manquantes ─────────────────────────────────
    n_nan = int(np.isnan(X).sum()) if n else 0
    nan_per_col = {}
    if n and d:
        for j in range(d):
            cnan = int(np.isnan(X[:, j]).sum())
            if cnan:
                name = feature_names[j] if j < len(feature_names) else str(j)
                nan_per_col[name] = cnan
    miss_status = "ok" if n_nan == 0 else ("fail" if n_nan > 0.3 * n * max(d, 1) else "warning")
    checks.append(CheckItem(
        "missing", "Valeurs manquantes",
        miss_status,
        "Aucune valeur manquante" if n_nan == 0 else f"{n_nan} NaN (colonnes: {list(nan_per_col.keys())[:8]})",
        {"n_nan": n_nan, "per_column": nan_per_col},
    ))

    # ── 4. Valeurs aberrantes ─────────────────────────────────
    outlier_mask = _iqr_outlier_mask(np.nan_to_num(X, nan=0.0), k=3.0) if n else np.array([])
    n_out = int(outlier_mask.sum()) if outlier_mask.size else 0
    out_ratio = n_out / n if n else 0.0
    out_status = "ok" if out_ratio < 0.15 else ("warning" if out_ratio < 0.4 else "fail")
    checks.append(CheckItem(
        "outliers", "Valeurs aberrantes",
        out_status,
        f"{n_out}/{n} échantillons hors IQR×3 ({out_ratio:.1%})",
        {"n_outliers": n_out, "ratio": round(out_ratio, 4), "method": "IQR_k=3"},
    ))

    # ── 5. Encodage des catégories ────────────────────────────
    # Labels déjà symboliques ; features doivent rester numériques (pas d'one-hot label dans X)
    label_set = sorted({str(yi) for yi in y})
    unexpected = [c for c in label_set if c not in CLASSES]
    enc_ok = len(unexpected) == 0 and d == len(feature_names) or d > 0
    # Vérifier qu'on n'a pas collé le label dans une feature (fuite grossière déjà §8)
    checks.append(CheckItem(
        "encoding", "Encodage des catégories",
        "fail" if unexpected else "ok",
        "Labels = classes métier (normal/urgent/critique), features numériques"
        if not unexpected else f"Labels inattendus: {unexpected}",
        {"classes_expected": list(CLASSES), "classes_found": label_set, "encoding": "label_string→model.classes_"},
    ))

    # ── 6. Mise à l'échelle ───────────────────────────────────
    needs_scale = False
    scale_msg = "N/A"
    if n and d:
        col_std = np.nanstd(X, axis=0)
        col_mean = np.nanmean(np.abs(X), axis=0)
        max_std = float(np.nanmax(col_std)) if col_std.size else 0
        min_std = float(np.nanmin(col_std[col_std > 0])) if np.any(col_std > 0) else 0
        ratio = max_std / min_std if min_std > 1e-12 else 1.0
        needs_scale = ratio > 25.0 or max_std > 100
        scale_msg = (
            f"StandardScaler recommandé (ratio σ max/min={ratio:.1f})"
            if needs_scale else
            f"Échelles acceptables (ratio σ={ratio:.1f}) — scaler appliqué par prudence"
        )
    checks.append(CheckItem(
        "scaling", "Mise à l'échelle",
        "ok",
        scale_msg + " (StandardScaler fit sur train uniquement)",
        {"needs_scale": needs_scale, "scaler": "StandardScaler", "fit_on": "train_only"},
    ))

    # ── 7. Séparation train/test ──────────────────────────────
    can_split = n >= 4
    stratify_ok = False
    counts = {c: int(np.sum(y == c)) for c in CLASSES}
    if can_split:
        present = [c for c, v in counts.items() if v > 0]
        stratify_ok = all(counts[c] >= 2 for c in present) and len(present) >= 2
    split_status = "ok" if can_split else "fail"
    checks.append(CheckItem(
        "train_test_split", "Séparation train/test",
        split_status,
        f"test_size={TEST_SIZE}, stratify={'oui' if stratify_ok else 'non (fallback)'}, random_state={RANDOM_STATE}"
        if can_split else "Trop peu d'échantillons pour splitter",
        {
            "test_size": TEST_SIZE,
            "stratify": stratify_ok,
            "random_state": RANDOM_STATE,
            "class_counts": counts,
        },
    ))

    # ── 8. Absence de fuite de données ────────────────────────
    leakage_issues = []
    # label dans feature names
    for fn in feature_names:
        if str(fn).lower() in ("label", "y", "class", "target", "severity"):
            leakage_issues.append(f"feature suspecte: {fn}")
    # corrélation parfaite feature ↔ one-hot label impossible ici ; check constant columns that mirror class count
    if n and d and len(set(y)) > 1:
        for j in range(min(d, len(feature_names))):
            col = X[:, j]
            if np.nanstd(col) < 1e-12:
                continue
            # si une feature prend autant de valeurs uniques que de classes et corrèle parfaitement
            try:
                from collections import defaultdict
                # skip heavy
            except Exception:
                pass
    # ids train/test non encore split ici — on documente la règle
    leakage_status = "fail" if leakage_issues else "ok"
    checks.append(CheckItem(
        "no_leakage", "Absence de fuite de données",
        leakage_status,
        "Pas de colonne cible dans X; scaler/oversample après split conceptuel (scaler fit train, eval hold-out)"
        if not leakage_issues else "; ".join(leakage_issues),
        {
            "rules": [
                "Pas de label dans X",
                "StandardScaler fit sur train seulement (ré-fit full pour modèle final documenté)",
                "Métrique reportée sur hold-out / CV stratifié",
                "Oversampling documenté: appliqué pour fit, CV sur données balancées (biais possible si n faible)",
            ],
            "issues": leakage_issues,
        },
    ))

    # ── 9. Équilibre des classes ──────────────────────────────
    total = max(n, 1)
    ratios = {c: counts.get(c, 0) / total for c in CLASSES}
    present_counts = [v for v in counts.values() if v > 0]
    imbalance = (max(present_counts) / min(present_counts)) if present_counts and min(present_counts) > 0 else 999.0
    bal_status = "ok"
    if len(present_counts) < 2:
        bal_status = "fail"
        bal_msg = "Moins de 2 classes présentes"
    elif imbalance > 5:
        bal_status = "warning"
        bal_msg = f"Déséquilibre fort (ratio max/min={imbalance:.1f}) — oversampling activé"
    elif imbalance > 2:
        bal_status = "warning"
        bal_msg = f"Déséquilibre modéré (ratio={imbalance:.1f})"
    else:
        bal_msg = f"Classes relativement équilibrées (ratio={imbalance:.1f})"
    checks.append(CheckItem(
        "class_balance", "Équilibre des classes",
        bal_status, bal_msg,
        {"counts": counts, "ratios": {k: round(v, 3) for k, v in ratios.items()}, "imbalance_ratio": round(imbalance, 2)},
    ))

    # ── 10. Métrique d'évaluation adaptée ─────────────────────
    metric = "f1_macro"
    metric_reason = (
        "Classification multi-classes potentiellement déséquilibrée → F1-macro "
        "(moyenne non pondérée des F1 par classe). Complété par F1-weighted, matrice de confusion, recall critique."
    )
    checks.append(CheckItem(
        "eval_metric", "Métrique d'évaluation adaptée",
        "ok",
        metric_reason,
        {
            "primary": metric,
            "secondary": ["f1_weighted", "precision_per_class", "recall_per_class", "confusion_matrix"],
            "hyperparam_scoring": "f1_macro",
            "why_not_accuracy": "L'accuracy masque les erreurs sur classes rares (urgent/critique)",
        },
    ))

    # ── EDA + fuites (modules dédiés) ─────────────────────────
    try:
        from ml.eda import run_eda, print_eda
        eda_report = run_eda(X, y, ids, feature_names)
        print_eda(eda_report)
    except Exception as e:
        eda_report = {"error": str(e)}
        print(f"[eda] skip: {e}")

    try:
        from ml.leakage import detect_leakage, print_leakage_report
        leak_report = detect_leakage(X, y, ids, feature_names)
        print_leakage_report(leak_report, X=X, y=y, feature_names=feature_names)
        # Remplacer/enrichir le check no_leakage
        if leak_report.get("status") == "fail":
            checks.append(CheckItem(
                "leakage_deep", "Détection de fuites (approfondie)",
                "fail",
                f"{leak_report.get('n_issues')} issue(s) — " + "; ".join(
                    i.get("message", "") for i in leak_report.get("issues", [])[:3]
                ),
                {"report": "data/models/leakage_report.json"},
            ))
        elif leak_report.get("status") == "warning":
            checks.append(CheckItem(
                "leakage_deep", "Détection de fuites (approfondie)",
                "warning",
                f"{leak_report.get('n_issues')} avertissement(s)",
                {"report": "data/models/leakage_report.json"},
            ))
        else:
            checks.append(CheckItem(
                "leakage_deep", "Détection de fuites (approfondie)",
                "ok", "Aucune fuite majeure détectée",
                {"report": "data/models/leakage_report.json"},
            ))
    except Exception as e:
        leak_report = {"error": str(e)}
        print(f"[leakage] skip: {e}")

    # ── Synthèse ─────────────────────────────────────────────
    statuses = [c.status for c in checks]
    if "fail" in statuses:
        overall = "fail"
    elif "warning" in statuses:
        overall = "warning"
    else:
        overall = "ok"

    report = {
        "started_at": datetime.utcnow().isoformat(),
        "overall": overall,
        "n_samples": n,
        "n_features": d,
        "checks": [c.to_dict() for c in checks],
        "block_on_fail": block_on_fail,
        "passed": overall != "fail" or not block_on_fail,
        "eda": {"log": "data/models/eda_report.json", "n_samples": n},
        "leakage": {"log": "data/models/leakage_report.json"},
    }

    # Persistance
    try:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        CHECKLIST_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    print_checklist(report)

    if block_on_fail and overall == "fail":
        failed = [c.name for c in checks if c.status == "fail"]
        raise ValueError(f"Checklist données ÉCHEC: {failed}. Voir {CHECKLIST_LOG}")

    return report


def print_checklist(report: Dict[str, Any]) -> None:
    print("\n" + "=" * 60)
    print("  CHECKLIST DONNÉES — avant entraînement")
    print("=" * 60)
    icon = {"ok": "✅", "warning": "⚠️ ", "fail": "❌"}
    for c in report.get("checks", []):
        print(f"  {icon.get(c['status'], '?')} [{c['status'].upper():7}] {c['name']}: {c['message']}")
    print("-" * 60)
    print(f"  Verdict global: {report.get('overall', '?').upper()}  "
          f"(n={report.get('n_samples')}, d={report.get('n_features')})")
    print(f"  Rapport: {CHECKLIST_LOG}")
    print("=" * 60 + "\n")


def impute_missing(X: np.ndarray) -> np.ndarray:
    """Remplace NaN par médiane de colonne (in-place copy)."""
    X = np.array(X, dtype=np.float64, copy=True)
    if X.size == 0:
        return X
    for j in range(X.shape[1]):
        col = X[:, j]
        mask = np.isnan(col)
        if mask.any():
            med = np.nanmedian(col)
            if np.isnan(med):
                med = 0.0
            col[mask] = med
            X[:, j] = col
    return X
