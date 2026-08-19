"""
Détection de fuites de données (data leakage) — SentinelAI ML.

Contrôles :
  - colonnes cibles / quasi-cibles dans X
  - corrélation excessive feature ↔ label
  - features constantes par classe (séparation parfaite suspecte)
  - doublons train/test (même id ou même vecteur)
  - scaler / oversampling mal placés (règles documentées)
  - features dérivées du label (noms suspects)
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from ml.config import CLASSES, MODELS_DIR, RANDOM_STATE, TEST_SIZE
from ml.indicators import INDICATOR_IDS

LEAKAGE_LOG = MODELS_DIR / "leakage_report.json"

SUSPICIOUS_NAMES = {
    "label", "y", "class", "target", "severity", "ground_truth",
    "is_fall", "fall_detected", "outcome", "result", "prediction",
}


def _label_codes(y: np.ndarray) -> np.ndarray:
    mapping = {c: i for i, c in enumerate(CLASSES)}
    return np.array([mapping.get(str(yi), -1) for yi in y], dtype=np.float64)


def _point_biserial_like(col: np.ndarray, y_code: np.ndarray) -> float:
    """Corrélation de Pearson entre feature continue et label encodé."""
    mask = np.isfinite(col) & np.isfinite(y_code) & (y_code >= 0)
    if mask.sum() < 5:
        return 0.0
    a, b = col[mask], y_code[mask]
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def detect_leakage(
    X: np.ndarray,
    y: np.ndarray,
    ids: Optional[Sequence[str]] = None,
    feature_names: Optional[Sequence[str]] = None,
    *,
    corr_threshold: float = 0.98,
    perfect_sep_threshold: float = 0.999,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> Dict[str, Any]:
    """
    Analyse complète de fuites potentielles.

    Returns
    -------
    dict avec status (ok|warning|fail), issues[], metrics, recommendations
    """
    feature_names = list(feature_names or INDICATOR_IDS)
    ids = list(ids) if ids is not None else [str(i) for i in range(len(y))]
    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    n, d = X.shape if X.ndim == 2 else (0, 0)
    y_code = _label_codes(y)

    issues: List[Dict[str, Any]] = []
    metrics: Dict[str, Any] = {"n_samples": n, "n_features": d}

    # 1) Noms de features suspects
    for j, name in enumerate(feature_names[:d]):
        low = str(name).lower().strip()
        if low in SUSPICIOUS_NAMES or any(s in low for s in ("label", "target", "ground_truth")):
            issues.append({
                "severity": "high",
                "type": "suspicious_feature_name",
                "feature": name,
                "message": f"Nom de feature suspect (possible cible): '{name}'",
            })

    # 2) Corrélation feature ↔ label
    high_corr = []
    for j in range(d):
        name = feature_names[j] if j < len(feature_names) else f"f{j}"
        r = abs(_point_biserial_like(X[:, j], y_code))
        if r >= corr_threshold:
            high_corr.append({"feature": name, "abs_corr_with_label": round(r, 4)})
            issues.append({
                "severity": "high",
                "type": "high_label_correlation",
                "feature": name,
                "message": f"Corrélation |r|={r:.3f} avec le label (≥ {corr_threshold})",
                "abs_corr": round(r, 4),
            })
        elif r >= 0.90:
            issues.append({
                "severity": "medium",
                "type": "elevated_label_correlation",
                "feature": name,
                "message": f"Corrélation élevée |r|={r:.3f} avec le label",
                "abs_corr": round(r, 4),
            })
    metrics["high_corr_features"] = high_corr

    # 3) Séparation quasi-parfaite (une feature isole les classes)
    for j in range(d):
        name = feature_names[j] if j < len(feature_names) else f"f{j}"
        col = X[:, j]
        if np.nanstd(col) < 1e-12:
            continue
        # pureté: pour chaque valeur unique (binnée), une seule classe ?
        try:
            bins = np.digitize(col, np.nanpercentile(col, [20, 40, 60, 80]))
            pure = 0
            total_bins = 0
            for b in np.unique(bins):
                mask = bins == b
                if mask.sum() < 2:
                    continue
                total_bins += 1
                if len(set(y[mask].tolist())) == 1:
                    pure += 1
            if total_bins > 0 and pure / total_bins >= perfect_sep_threshold:
                issues.append({
                    "severity": "medium",
                    "type": "near_perfect_class_separation",
                    "feature": name,
                    "message": f"Feature '{name}' sépare presque parfaitement les classes (bins purs={pure}/{total_bins})",
                })
        except Exception:
            pass

    # 4) Colonnes constantes (peu utiles, parfois artefact de fuite)
    constant_cols = []
    for j in range(d):
        if np.nanstd(X[:, j]) < 1e-12:
            name = feature_names[j] if j < len(feature_names) else f"f{j}"
            constant_cols.append(name)
    if constant_cols:
        issues.append({
            "severity": "low",
            "type": "constant_features",
            "features": constant_cols,
            "message": f"{len(constant_cols)} feature(s) constante(s): {constant_cols[:8]}",
        })
    metrics["constant_features"] = constant_cols

    # 5) Fuite train/test par id ou vecteur identique
    split_leak = {"duplicate_ids_across_split": 0, "identical_vectors_across_split": 0}
    if n >= 4:
        from sklearn.model_selection import train_test_split
        counts = {c: int(np.sum(y == c)) for c in CLASSES}
        present = [c for c, v in counts.items() if v > 0]
        strat = all(counts[c] >= 2 for c in present) and len(present) >= 2
        idx = np.arange(n)
        try:
            i_tr, i_te = train_test_split(
                idx, test_size=min(test_size, 0.4), random_state=random_state,
                stratify=y if strat else None,
            )
        except ValueError:
            i_tr, i_te = train_test_split(idx, test_size=min(test_size, 0.4), random_state=random_state)

        ids_tr = {ids[i] for i in i_tr}
        ids_te = {ids[i] for i in i_te}
        inter = ids_tr & ids_te
        split_leak["duplicate_ids_across_split"] = len(inter)
        if inter:
            issues.append({
                "severity": "high",
                "type": "id_overlap_train_test",
                "message": f"{len(inter)} id(s) présents dans train ET test",
                "ids_sample": list(inter)[:10],
            })

        # vecteurs identiques entre train et test
        Xt = np.round(X[i_tr], 6)
        Xe = np.round(X[i_te], 6)
        # hash rows
        def _row_keys(a):
            return {tuple(row) for row in a}
        try:
            overlap_vec = _row_keys(Xt) & _row_keys(Xe)
            split_leak["identical_vectors_across_split"] = len(overlap_vec)
            if overlap_vec:
                issues.append({
                    "severity": "high",
                    "type": "vector_overlap_train_test",
                    "message": f"{len(overlap_vec)} vecteur(s) de features identiques dans train et test",
                })
        except Exception:
            pass
        metrics["split_sizes"] = {"train": int(len(i_tr)), "test": int(len(i_te))}

    metrics["split_leak"] = split_leak

    # 6) Règles process (scaler / oversample)
    process_rules = [
        "StandardScaler doit être fit sur le train uniquement (pas sur train+test avant split).",
        "Oversampling / SMOTE uniquement sur le train (jamais sur le test).",
        "Hyperparam CV : idealement Pipeline(scaler, model) dans chaque fold.",
        "Ne pas utiliser d'information du test pour le triage bootstrap des labels.",
    ]
    metrics["process_rules"] = process_rules

    # Verdict
    sevs = [i["severity"] for i in issues]
    if "high" in sevs:
        status = "fail"
    elif "medium" in sevs:
        status = "warning"
    elif issues:
        status = "warning"
    else:
        status = "ok"

    recommendations = []
    if any(i["type"] == "high_label_correlation" for i in issues):
        recommendations.append("Retirer ou revoir les features trop corrélées au label (possible fuite).")
    if any(i["type"] in ("id_overlap_train_test", "vector_overlap_train_test") for i in issues):
        recommendations.append("Dédoublonner les fragments avant split ; group split par vidéo source si possible.")
    if any(i["type"] == "suspicious_feature_name" for i in issues):
        recommendations.append("Supprimer les colonnes cibles du matrice X.")
    if not recommendations and status == "ok":
        recommendations.append("Aucune fuite majeure détectée — maintenir Pipeline scaler+model en CV.")

    report = {
        "started_at": datetime.utcnow().isoformat(),
        "status": status,
        "n_issues": len(issues),
        "issues": issues,
        "metrics": metrics,
        "recommendations": recommendations,
        "corr_threshold": corr_threshold,
    }
    try:
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        LEAKAGE_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass
    return report


def print_leakage_report(report: Dict[str, Any], X=None, y=None, feature_names=None) -> None:
    print("\n" + "-" * 60)
    print("  DÉTECTION DE FUITES (data leakage)")
    print("-" * 60)
    print(f"  Statut: {report.get('status', '?').upper()}  |  issues={report.get('n_issues', 0)}")
    for i in report.get("issues", [])[:12]:
        print(f"  [{i.get('severity', '?'):6}] {i.get('message')}")
    for r in report.get("recommendations", []):
        print(f"  → {r}")
    print(f"  Rapport: {LEAKAGE_LOG}")
    print("-" * 60 + "\n")
    if X is not None and y is not None:
        try:
            from ml.visualize_leakage import visualize_all
            visualize_all(X, y, report, feature_names=feature_names)
        except Exception as e:
            print(f"[viz] skip: {e}")
