"""
Scikit-learn Pipeline — prétraitement + classifieur (anti-fuite).

Chaque fold de CV applique :
  StandardScaler.fit(train_fold) → transform → estimateur

Usage :
  from ml.sklearn_pipeline import build_pipeline, fit_search_pipeline, evaluate_pipeline
  pipe = build_pipeline("random_forest")
  search = fit_search_pipeline(X_train, y_train)
  metrics = evaluate_pipeline(search.best_estimator_, X_test, y_test)
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

from ml.config import (
    CLASSES,
    HYPERPARAM_CV,
    HYPERPARAM_N_ITER,
    HYPERPARAM_REFINE,
    HYPERPARAM_REFINE_ITER,
    MODELS_DIR,
    PARAM_GRIDS,
    RANDOM_STATE,
    TREE_MODEL,
    BEST_MODEL,
    SCALER_PATH,
    F1_ANALYSIS_LOG,
    HYPERPARAM_LOG,
)
from ml.indicators import INDICATOR_IDS

PIPELINE_MODEL = MODELS_DIR / "sklearn_pipeline.joblib"
PIPELINE_META = MODELS_DIR / "sklearn_pipeline_meta.json"


def _estimators() -> Dict[str, Any]:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import (
        RandomForestClassifier,
        ExtraTreesClassifier,
        GradientBoostingClassifier,
    )
    return {
        "decision_tree": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(
            random_state=RANDOM_STATE, n_jobs=-1, class_weight="balanced"
        ),
        "extra_trees": ExtraTreesClassifier(
            random_state=RANDOM_STATE, n_jobs=-1, class_weight="balanced"
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }


def build_pipeline(model_name: str = "extra_trees", **model_params) -> Any:
    """
    Pipeline(steps=[('scaler', StandardScaler()), ('clf', Estimator)]).
    """
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    estimators = _estimators()
    if model_name not in estimators:
        raise ValueError(f"Modèle inconnu: {model_name}. Choisir parmi {list(estimators)}")
    clf = estimators[model_name]
    if model_params:
        clf.set_params(**model_params)
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", clf),
        ]
    )


def _param_grid_for_pipeline(model_name: str) -> Dict[str, List]:
    """Préfixe les hyperparamètres avec 'clf__' pour RandomizedSearchCV."""
    raw = PARAM_GRIDS.get(model_name, {})
    return {f"clf__{k}": v for k, v in raw.items()}


def fit_search_pipeline(
    X: np.ndarray,
    y: np.ndarray,
    *,
    models: Optional[List[str]] = None,
    n_iter: int = HYPERPARAM_N_ITER,
    cv_folds: int = HYPERPARAM_CV,
    random_state: int = RANDOM_STATE,
    refine: bool = HYPERPARAM_REFINE,
) -> Tuple[Any, Dict[str, Any]]:
    """
    Recherche multi-modèles avec Pipeline sklearn.
    Retourne (best_pipeline, report).
    """
    from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
    from sklearn.metrics import make_scorer, f1_score

    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    models = models or list(_estimators().keys())

    counts = {c: int(np.sum(y == c)) for c in CLASSES}
    min_c = min((v for v in counts.values() if v > 0), default=2)
    n_splits = min(int(cv_folds), max(2, min_c))
    if len(y) < n_splits * 2:
        n_splits = 2

    scorer = make_scorer(f1_score, average="macro", zero_division=0)
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    report: Dict[str, Any] = {
        "started_at": datetime.utcnow().isoformat(),
        "models": {},
        "cv_folds": n_splits,
        "scoring": "f1_macro",
        "pipeline_steps": ["scaler", "clf"],
    }
    best_pipe, best_name, best_score = None, None, -1.0
    ranking = []

    for name in models:
        pipe = build_pipeline(name)
        grid = _param_grid_for_pipeline(name)
        if not grid:
            continue
        max_combos = 1
        for v in grid.values():
            max_combos *= max(len(v), 1)
        n_try = min(int(n_iter), max_combos, 40)
        if len(y) < 20:
            n_try = min(n_try, 10)
        print(f"[skpipe] RandomizedSearch {name} (n_iter={n_try}, cv={n_splits})…")
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
            entry = {
                "best_cv_f1_macro": round(score, 4),
                "best_params": search.best_params_,
                "n_iter": n_try,
                "overfit_gap": round(
                    float(
                        search.cv_results_["mean_train_score"][search.best_index_]
                        - score
                    ),
                    4,
                ),
            }
            report["models"][name] = entry
            ranking.append((score, name, search.best_estimator_))
            print(f"[skpipe]   {name}: cv_f1={score:.3f} params={search.best_params_}")
            if score > best_score:
                best_score, best_name, best_pipe = score, name, search.best_estimator_
        except Exception as e:
            print(f"[skpipe]   {name} ÉCHEC: {e}")
            report["models"][name] = {"error": str(e)}

    ranking.sort(key=lambda x: -x[0])
    report["ranking"] = [{"model": n, "cv_f1_macro": round(s, 4)} for s, n, _ in ranking]

    # Raffinement local
    if refine and best_pipe is not None and best_name is not None:
        try:
            from ml.trees import _refine_grid
            raw_params = {
                k.replace("clf__", ""): v
                for k, v in best_pipe.named_steps["clf"].get_params().items()
                if k in (PARAM_GRIDS.get(best_name) or {})
                or k in ("n_estimators", "max_depth", "min_samples_leaf", "learning_rate", "subsample", "max_features", "criterion", "class_weight", "bootstrap", "min_samples_split")
            }
            # simpler: use best_params from report
            bp = {
                k.replace("clf__", ""): v
                for k, v in (report["models"][best_name].get("best_params") or {}).items()
            }
            fine = _refine_grid(best_name, bp)
            if fine:
                fine_pipe = {f"clf__{k}": v for k, v in fine.items()}
                search2 = RandomizedSearchCV(
                    build_pipeline(best_name),
                    param_distributions=fine_pipe,
                    n_iter=min(int(HYPERPARAM_REFINE_ITER), 20),
                    scoring=scorer,
                    cv=cv,
                    random_state=random_state + 7,
                    n_jobs=-1,
                    refit=True,
                    error_score=0.0,
                )
                search2.fit(X, y)
                report["refine"] = {
                    "model": best_name,
                    "best_cv_f1_macro": round(float(search2.best_score_), 4),
                    "best_params": search2.best_params_,
                    "improved": bool(search2.best_score_ > best_score + 1e-4),
                }
                print(f"[skpipe] refine {best_name}: {search2.best_score_:.3f} (avant {best_score:.3f})")
                if search2.best_score_ > best_score:
                    best_score = float(search2.best_score_)
                    best_pipe = search2.best_estimator_
        except Exception as e:
            report["refine"] = {"error": str(e)}
            print(f"[skpipe] refine skip: {e}")

    report["best_model"] = best_name
    report["best_cv_f1_macro"] = round(best_score, 4) if best_score >= 0 else None
    report["finished_at"] = datetime.utcnow().isoformat()

    # Feature importance si disponible
    if best_pipe is not None:
        clf = best_pipe.named_steps.get("clf")
        if clf is not None and hasattr(clf, "feature_importances_"):
            imp = clf.feature_importances_
            names = INDICATOR_IDS if len(INDICATOR_IDS) == len(imp) else [f"f{i}" for i in range(len(imp))]
            pairs = sorted(zip(names, imp), key=lambda x: -x[1])[:15]
            report["top_features"] = [
                {"feature": n, "importance": round(float(v), 4)} for n, v in pairs
            ]

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    HYPERPARAM_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    if best_pipe is None:
        best_pipe = build_pipeline("extra_trees")
        best_pipe.fit(X, y)
        best_name = "extra_trees_fallback"
        report["best_model"] = best_name

    return best_pipe, report


def evaluate_pipeline(
    pipe: Any,
    X: np.ndarray,
    y: np.ndarray,
    *,
    split_name: str = "test",
) -> Dict[str, Any]:
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        classification_report,
        confusion_matrix,
    )

    X = np.asarray(X, dtype=np.float64)
    y = np.asarray(y)
    if len(y) == 0:
        return {"split": split_name, "n": 0}
    pred = pipe.predict(X)
    labels = list(CLASSES)
    metrics = {
        "split": split_name,
        "n": int(len(y)),
        "accuracy": round(float(accuracy_score(y, pred)), 4),
        "f1_macro": round(float(f1_score(y, pred, average="macro", zero_division=0, labels=labels)), 4),
        "f1_weighted": round(float(f1_score(y, pred, average="weighted", zero_division=0, labels=labels)), 4),
        "confusion_matrix": {
            "labels": labels,
            "matrix": confusion_matrix(y, pred, labels=labels).tolist(),
        },
        "report_text": classification_report(y, pred, labels=labels, zero_division=0),
    }
    return metrics


def save_pipeline(pipe: Any, meta: Optional[Dict[str, Any]] = None) -> Path:
    import joblib

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "pipeline": pipe,
        "feature_names": list(INDICATOR_IDS),
        "classes": list(CLASSES),
        "saved_at": datetime.utcnow().isoformat(),
        "meta": meta or {},
    }
    joblib.dump(payload, PIPELINE_MODEL)
    joblib.dump(payload, TREE_MODEL)
    joblib.dump(payload, BEST_MODEL)
    # scaler seul (compat)
    try:
        joblib.dump(pipe.named_steps["scaler"], SCALER_PATH)
    except Exception:
        pass
    meta_out = {
        "path": str(PIPELINE_MODEL),
        "steps": [s[0] for s in pipe.steps],
        "clf": type(pipe.named_steps.get("clf")).__name__,
        **(meta or {}),
    }
    PIPELINE_META.write_text(json.dumps(meta_out, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"[skpipe] Sauvé → {PIPELINE_MODEL}")
    return PIPELINE_MODEL


def load_pipeline(path: Optional[Path] = None) -> Any:
    import joblib
    path = path or PIPELINE_MODEL
    payload = joblib.load(path)
    if isinstance(payload, dict) and "pipeline" in payload:
        return payload["pipeline"]
    return payload  # raw Pipeline


def predict_with_pipeline(
    pipe: Any,
    X: np.ndarray,
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """Retourne (labels, proba ou None)."""
    X = np.asarray(X, dtype=np.float64)
    labels = pipe.predict(X)
    proba = pipe.predict_proba(X) if hasattr(pipe, "predict_proba") else None
    return labels, proba


def run_sklearn_pipeline_training(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: Optional[np.ndarray] = None,
    y_val: Optional[np.ndarray] = None,
    X_test: Optional[np.ndarray] = None,
    y_test: Optional[np.ndarray] = None,
    skip_hyper: bool = False,
) -> Dict[str, Any]:
    """
    Entraînement complet via sklearn Pipeline.
    """
    from ml.trees import analyze_f1_errors, print_f1_analysis

    if skip_hyper:
        pipe = build_pipeline("extra_trees")
        pipe.fit(X_train, y_train)
        hyper = {"skipped": True, "best_model": "extra_trees"}
    else:
        pipe, hyper = fit_search_pipeline(X_train, y_train)

    results: Dict[str, Any] = {
        "status": "completed",
        "hyperparam": {
            "best_model": hyper.get("best_model"),
            "best_cv_f1_macro": hyper.get("best_cv_f1_macro"),
            "ranking": hyper.get("ranking"),
        },
        "metrics": {},
    }

    if X_val is not None and y_val is not None and len(y_val):
        results["metrics"]["val"] = evaluate_pipeline(pipe, X_val, y_val, split_name="val")
        print(f"[skpipe] VAL  {results['metrics']['val']}")
    if X_test is not None and y_test is not None and len(y_test):
        results["metrics"]["test"] = evaluate_pipeline(pipe, X_test, y_test, split_name="test")
        print(f"[skpipe] TEST {results['metrics']['test']}")
        pred = pipe.predict(X_test)
        analysis = analyze_f1_errors(y_test, pred, model_name=str(hyper.get("best_model")))
        print_f1_analysis(analysis)
        F1_ANALYSIS_LOG.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
        results["f1_analysis"] = {
            "f1_macro": analysis.get("f1_macro"),
            "n_misclassified": analysis.get("n_misclassified"),
        }

    # Refit train+val pour modèle final
    if X_val is not None and len(y_val):
        X_fit = np.vstack([X_train, X_val])
        y_fit = np.concatenate([y_train, y_val])
        # Reconstruire pipeline avec meilleurs params pour refit clean
        pipe.fit(X_fit, y_fit)

    save_pipeline(pipe, meta=results)
    results["model_path"] = str(PIPELINE_MODEL)
    return results
