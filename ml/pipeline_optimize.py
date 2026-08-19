"""
Optimisation d'hyperparamètres + exploration de pipelines de données + sauvegarde.

Explore plusieurs chaînes de prétraitement :
  - StandardScaler | RobustScaler | MinMaxScaler
  - SimpleImputer (médiane)
  - PCA optionnelle
  - Classifieurs arbres / boosting

Puis RandomizedSearchCV sur le Pipeline complet (anti-fuite).

Sauvegarde versionnée :
  data/models/pipelines/{timestamp}_pipeline.joblib
  data/models/pipelines/{timestamp}_meta.json
  data/models/sklearn_pipeline.joblib  (latest)
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from ml.config import (
    CLASSES,
    HYPERPARAM_CV,
    HYPERPARAM_N_ITER,
    MODELS_DIR,
    PARAM_GRIDS,
    RANDOM_STATE,
    TREE_MODEL,
    BEST_MODEL,
    SCALER_PATH,
    HYPERPARAM_LOG,
    F1_ANALYSIS_LOG,
)
from ml.indicators import INDICATOR_IDS

PIPELINES_DIR = MODELS_DIR / "pipelines"
LATEST_PIPELINE = MODELS_DIR / "sklearn_pipeline.joblib"
LATEST_META = MODELS_DIR / "sklearn_pipeline_meta.json"
SEARCH_LOG = MODELS_DIR / "pipeline_search.json"


# ── Construction des pipelines de données ─────────────────────

def make_preprocessor(scaler: str = "standard", with_pca: bool = False, pca_dim: int = 20) -> Any:
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
    from sklearn.decomposition import PCA

    scalers = {
        "standard": StandardScaler(),
        "robust": RobustScaler(),
        "minmax": MinMaxScaler(),
        "none": "passthrough",
    }
    if scaler not in scalers:
        raise ValueError(f"scaler={scaler} invalide")

    steps = [("imputer", SimpleImputer(strategy="median"))]
    if scalers[scaler] != "passthrough":
        steps.append(("scaler", scalers[scaler]))
    else:
        steps.append(("scaler", "passthrough"))
    if with_pca:
        steps.append(("pca", PCA(n_components=pca_dim, random_state=RANDOM_STATE)))
    return Pipeline(steps)


def make_full_pipeline(
    model_name: str = "extra_trees",
    scaler: str = "standard",
    with_pca: bool = False,
    pca_dim: int = 20,
    **clf_params,
) -> Any:
    from sklearn.pipeline import Pipeline
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import (
        RandomForestClassifier,
        ExtraTreesClassifier,
        GradientBoostingClassifier,
    )

    clfs = {
        "decision_tree": DecisionTreeClassifier(random_state=RANDOM_STATE, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            random_state=RANDOM_STATE, n_jobs=-1, class_weight="balanced"
        ),
        "extra_trees": ExtraTreesClassifier(
            random_state=RANDOM_STATE, n_jobs=-1, class_weight="balanced"
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }
    if model_name not in clfs:
        raise ValueError(f"model={model_name}")
    clf = clfs[model_name]
    if clf_params:
        # only valid params
        valid = clf.get_params()
        clf.set_params(**{k: v for k, v in clf_params.items() if k in valid})

    pre = make_preprocessor(scaler=scaler, with_pca=with_pca, pca_dim=pca_dim)
    return Pipeline([
        ("pre", pre),
        ("clf", clf),
    ])


def data_pipeline_variants(n_features: int = 36) -> List[Dict[str, Any]]:
    """Catalogue de pipelines de données à explorer."""
    pca_dim = max(5, min(20, n_features // 2))
    return [
        {"name": "standard", "scaler": "standard", "with_pca": False, "pca_dim": pca_dim},
        {"name": "robust", "scaler": "robust", "with_pca": False, "pca_dim": pca_dim},
        {"name": "minmax", "scaler": "minmax", "with_pca": False, "pca_dim": pca_dim},
        {"name": "standard_pca", "scaler": "standard", "with_pca": True, "pca_dim": pca_dim},
        {"name": "robust_pca", "scaler": "robust", "with_pca": True, "pca_dim": pca_dim},
    ]


def _clf_param_distributions(model_name: str) -> Dict[str, List]:
    raw = dict(PARAM_GRIDS.get(model_name, {}))
    # enrichissements ciblés
    if model_name in ("random_forest", "extra_trees"):
        raw.setdefault("n_estimators", [100, 150, 200, 300])
        raw.setdefault("max_depth", [6, 10, 14, None])
        raw.setdefault("min_samples_leaf", [1, 2, 4])
    if model_name == "gradient_boosting":
        raw.setdefault("learning_rate", [0.03, 0.05, 0.1, 0.15])
        raw.setdefault("n_estimators", [80, 120, 180])
        raw.setdefault("max_depth", [2, 3, 4])
    return {f"clf__{k}": v for k, v in raw.items()}


def explore_and_optimize(
    X: np.ndarray,
    y: np.ndarray,
    *,
    models: Optional[List[str]] = None,
    n_iter: int = HYPERPARAM_N_ITER,
    cv_folds: int = HYPERPARAM_CV,
    max_variants: int = 5,
    random_state: int = RANDOM_STATE,
) -> Tuple[Any, Dict[str, Any]]:
    """
    Explore pipelines de données × modèles × hyperparams.
    Retourne (best_pipeline, report).
    """
    from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
    from sklearn.metrics import make_scorer, f1_score

    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    n_features = X.shape[1] if X.ndim == 2 else 0
    models = models or ["random_forest", "extra_trees", "gradient_boosting", "decision_tree"]
    variants = data_pipeline_variants(n_features)[:max_variants]

    counts = {c: int(np.sum(y == c)) for c in CLASSES}
    min_c = min((v for v in counts.values() if v > 0), default=2)
    n_splits = min(int(cv_folds), max(2, min_c))
    if len(y) < n_splits * 2:
        n_splits = 2

    scorer = make_scorer(f1_score, average="macro", zero_division=0)
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    report: Dict[str, Any] = {
        "started_at": datetime.utcnow().isoformat(),
        "n_samples": int(len(y)),
        "n_features": n_features,
        "cv_folds": n_splits,
        "trials": [],
        "scoring": "f1_macro",
    }

    best_pipe, best_score, best_meta = None, -1.0, {}
    effective_iter = min(int(n_iter), 12 if len(y) < 30 else int(n_iter))

    for var in variants:
        for model_name in models:
            pipe = make_full_pipeline(
                model_name=model_name,
                scaler=var["scaler"],
                with_pca=var["with_pca"],
                pca_dim=var["pca_dim"],
            )
            grid = _clf_param_distributions(model_name)
            # hyperparams préprocesseur (pca dim)
            if var["with_pca"]:
                grid["pre__pca__n_components"] = sorted({
                    max(2, var["pca_dim"] - 5),
                    var["pca_dim"],
                    min(n_features, var["pca_dim"] + 5),
                })

            n_try = min(effective_iter, 30)
            label = f"{var['name']}+{model_name}"
            print(f"[opt] {label} (iter={n_try}, cv={n_splits})…")
            try:
                search = RandomizedSearchCV(
                    pipe,
                    param_distributions=grid,
                    n_iter=n_try,
                    scoring=scorer,
                    cv=cv,
                    random_state=random_state,
                    n_jobs=-1,
                    refit=True,
                    error_score=0.0,
                    return_train_score=True,
                )
                search.fit(X, y)
                score = float(search.best_score_)
                gap = float(
                    search.cv_results_["mean_train_score"][search.best_index_] - score
                )
                trial = {
                    "data_pipeline": var["name"],
                    "model": model_name,
                    "cv_f1_macro": round(score, 4),
                    "overfit_gap": round(gap, 4),
                    "best_params": search.best_params_,
                    "scaler": var["scaler"],
                    "pca": var["with_pca"],
                }
                report["trials"].append(trial)
                print(f"[opt]   → f1={score:.3f} gap={gap:.3f}")
                if score > best_score:
                    best_score = score
                    best_pipe = search.best_estimator_
                    best_meta = trial
            except Exception as e:
                print(f"[opt]   ÉCHEC {label}: {e}")
                report["trials"].append({
                    "data_pipeline": var["name"],
                    "model": model_name,
                    "error": str(e),
                })

    report["trials"].sort(key=lambda t: t.get("cv_f1_macro") or -1, reverse=True)
    report["best"] = best_meta
    report["best_cv_f1_macro"] = round(best_score, 4) if best_score >= 0 else None
    report["finished_at"] = datetime.utcnow().isoformat()

    if best_pipe is None:
        best_pipe = make_full_pipeline("extra_trees", scaler="standard")
        best_pipe.fit(X, y)
        best_meta = {"model": "extra_trees", "data_pipeline": "standard", "fallback": True}
        report["best"] = best_meta

    # importance
    try:
        clf = best_pipe.named_steps["clf"]
        if hasattr(clf, "feature_importances_"):
            imp = clf.feature_importances_
            # si PCA, importances sur composantes
            names = (
                INDICATOR_IDS if len(imp) == len(INDICATOR_IDS)
                else [f"comp_{i}" for i in range(len(imp))]
            )
            pairs = sorted(zip(names, imp), key=lambda x: -x[1])[:15]
            report["top_features"] = [
                {"feature": n, "importance": round(float(v), 4)} for n, v in pairs
            ]
    except Exception:
        pass

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    SEARCH_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    HYPERPARAM_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"[opt] Meilleur: {best_meta.get('data_pipeline')}+{best_meta.get('model')} "
          f"f1={report.get('best_cv_f1_macro')}")
    return best_pipe, report


# ── Sauvegarde / chargement ───────────────────────────────────

def save_pipeline_versioned(
    pipe: Any,
    meta: Optional[Dict[str, Any]] = None,
    *,
    tag: Optional[str] = None,
) -> Dict[str, str]:
    """
    Sauvegarde versionnée + latest.

    Retourne chemins {versioned, latest, meta, scaler}.
    """
    import joblib

    PIPELINES_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    tag = tag or (meta or {}).get("model") or "pipe"
    stem = f"{ts}_{tag}"

    payload = {
        "pipeline": pipe,
        "feature_names": list(INDICATOR_IDS),
        "classes": list(CLASSES),
        "saved_at": datetime.utcnow().isoformat(),
        "meta": meta or {},
        "version": stem,
    }

    versioned = PIPELINES_DIR / f"{stem}.joblib"
    meta_path = PIPELINES_DIR / f"{stem}_meta.json"

    joblib.dump(payload, versioned)
    joblib.dump(payload, LATEST_PIPELINE)
    joblib.dump(payload, TREE_MODEL)
    joblib.dump(payload, BEST_MODEL)

    # scaler isolé si accessible
    scaler_path = str(SCALER_PATH)
    try:
        pre = pipe.named_steps.get("pre")
        if pre is not None and hasattr(pre, "named_steps"):
            sc = pre.named_steps.get("scaler")
            if sc is not None and sc != "passthrough":
                joblib.dump(sc, SCALER_PATH)
        elif "scaler" in getattr(pipe, "named_steps", {}):
            joblib.dump(pipe.named_steps["scaler"], SCALER_PATH)
    except Exception:
        scaler_path = ""

    meta_out = {
        "version": stem,
        "path": str(versioned),
        "latest": str(LATEST_PIPELINE),
        "steps": [s[0] for s in pipe.steps],
        "clf": type(pipe.named_steps["clf"]).__name__,
        "saved_at": payload["saved_at"],
        "meta": meta or {},
    }
    # détail pre steps
    try:
        pre = pipe.named_steps["pre"]
        meta_out["pre_steps"] = [s[0] for s in pre.steps]
    except Exception:
        pass

    meta_path.write_text(json.dumps(meta_out, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    LATEST_META.write_text(json.dumps(meta_out, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    # index des versions
    index_path = PIPELINES_DIR / "index.json"
    index = []
    if index_path.exists():
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            index = []
    index.append(meta_out)
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    paths = {
        "versioned": str(versioned),
        "latest": str(LATEST_PIPELINE),
        "meta": str(meta_path),
        "scaler": scaler_path,
        "index": str(index_path),
    }
    print(f"[save] Pipeline → {versioned}")
    print(f"[save] Latest   → {LATEST_PIPELINE}")
    return paths


def load_pipeline_saved(path: Optional[Path] = None) -> Tuple[Any, Dict[str, Any]]:
    """Charge pipeline (+ meta). path=None → latest."""
    import joblib
    path = Path(path) if path else LATEST_PIPELINE
    payload = joblib.load(path)
    if isinstance(payload, dict) and "pipeline" in payload:
        return payload["pipeline"], payload
    return payload, {"pipeline": payload}


def list_saved_pipelines() -> List[Dict[str, Any]]:
    index_path = PIPELINES_DIR / "index.json"
    if not index_path.exists():
        return []
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except Exception:
        return []


def run_optimized_training(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: Optional[np.ndarray] = None,
    y_val: Optional[np.ndarray] = None,
    X_test: Optional[np.ndarray] = None,
    y_test: Optional[np.ndarray] = None,
    n_iter: int = HYPERPARAM_N_ITER,
) -> Dict[str, Any]:
    """Optimisation complète + eval + sauvegarde versionnée."""
    from ml.sklearn_pipeline import evaluate_pipeline
    from ml.trees import analyze_f1_errors, print_f1_analysis

    pipe, search_report = explore_and_optimize(X_train, y_train, n_iter=n_iter)

    results: Dict[str, Any] = {
        "status": "completed",
        "search": {
            "best": search_report.get("best"),
            "best_cv_f1_macro": search_report.get("best_cv_f1_macro"),
            "n_trials": len(search_report.get("trials") or []),
            "log": str(SEARCH_LOG),
        },
        "metrics": {},
    }

    if X_val is not None and y_val is not None and len(y_val):
        results["metrics"]["val"] = evaluate_pipeline(pipe, X_val, y_val, split_name="val")
        print("[opt] VAL ", results["metrics"]["val"])
    if X_test is not None and y_test is not None and len(y_test):
        results["metrics"]["test"] = evaluate_pipeline(pipe, X_test, y_test, split_name="test")
        print("[opt] TEST", results["metrics"]["test"])
        pred = pipe.predict(X_test)
        analysis = analyze_f1_errors(y_test, pred, model_name=str((search_report.get("best") or {}).get("model")))
        print_f1_analysis(analysis)
        F1_ANALYSIS_LOG.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")

    # refit train+val
    if X_val is not None and len(y_val):
        pipe.fit(np.vstack([X_train, X_val]), np.concatenate([y_train, y_val]))

    tag = f"{(search_report.get('best') or {}).get('data_pipeline', 'pipe')}_" \
          f"{(search_report.get('best') or {}).get('model', 'clf')}"
    paths = save_pipeline_versioned(pipe, meta=results, tag=tag)
    results["saved"] = paths

    # Courbes d'apprentissage
    try:
        from ml.learning_curves import run_learning_curves
        lc = run_learning_curves(X_train, y_train, pipe=pipe)
        results["learning_curve"] = {
            "final_val": lc.get("final_val"),
            "final_gap": lc.get("final_gap"),
            "diagnosis": lc.get("diagnosis"),
            "plots": lc.get("plots"),
            "log": "data/models/learning_curve.json",
        }
    except Exception as e:
        print(f"[opt] learning curves skip: {e}")
        results["learning_curve"] = {"error": str(e)}

    return results
