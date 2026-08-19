"""Apprentissage: hyperparamétrage, analyse F1, gestion d'erreurs."""
from __future__ import annotations
import json, traceback, warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from ml.config import (
    MODELS_DIR, TREE_MODEL, BEST_MODEL, TREE_EXPORT, TRAIN_LOG, METRICS_LOG,
    F1_ANALYSIS_LOG, HYPERPARAM_LOG, SCALER_PATH, CLASSES,
    MIN_SAMPLES_TOTAL, MIN_ACCEPTABLE_F1_MACRO, MIN_GOOD_F1_MACRO,
    RANDOM_STATE, TEST_SIZE, HYPERPARAM_N_ITER, HYPERPARAM_CV, PARAM_GRIDS,
    HYPERPARAM_REFINE, HYPERPARAM_REFINE_ITER,
    N_ESTIMATORS_DEFAULT, MAX_DEPTH_DEFAULT,
)
from ml.indicators import INDICATOR_IDS
from ml.errors import (
    InsufficientDataError, TrainingError, ModelNotFoundError,
    LowQualityModelError, LearningError, PredictionError,
)
warnings.filterwarnings("ignore")

def _load_xy():
    from ml.features import build_feature_table
    X, y, ids = build_feature_table()
    mask = np.array([yi in CLASSES for yi in y]) if len(y) else np.array([], dtype=bool)
    if mask.size and mask.any():
        return X[mask], y[mask], [ids[i] for i, m in enumerate(mask) if m]
    return X, y, list(ids)

def _class_counts(y):
    return {c: int(np.sum(y == c)) for c in CLASSES}

def _oversample_balance(X, y, rng):
    counts = _class_counts(y)
    target = max(counts.values()) if counts else 0
    if target <= 0: return X, y
    Xs, ys = [X], [y]
    for c in CLASSES:
        idx = np.where(y == c)[0]
        if len(idx) == 0: continue
        need = target - len(idx)
        if need <= 0: continue
        choice = rng.choice(idx, size=need, replace=True)
        Xs.append(X[choice] + rng.normal(0, 0.05, size=(need, X.shape[1])))
        ys.append(np.full(need, c))
    return np.vstack(Xs), np.concatenate(ys)

def _safe_split(X, y):
    from sklearn.model_selection import train_test_split
    counts = _class_counts(y)
    can_stratify = all(v >= 2 for v in counts.values() if v > 0) and len(set(y)) > 1
    ts = TEST_SIZE if len(y) >= 8 else max(0.2, 1.0 / max(len(y), 1))
    try:
        return train_test_split(X, y, test_size=min(ts, 0.4), random_state=RANDOM_STATE,
                                stratify=y if can_stratify else None)
    except ValueError:
        return X, X, y, y

def _fit_scaler(X):
    from sklearn.preprocessing import StandardScaler
    import joblib
    scaler = StandardScaler()
    if len(X) == 0: return scaler, X
    Xs = scaler.fit_transform(X)
    SCALER_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)
    return scaler, Xs

def analyze_f1_errors(y_true, y_pred, ids=None, proba=None, model_name=""):
    from sklearn.metrics import (
        f1_score, precision_score, recall_score, accuracy_score,
        confusion_matrix, classification_report,
    )
    labels = list(CLASSES)
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    per_class = {}
    for c in labels:
        tp = int(np.sum((y_true == c) & (y_pred == c)))
        fp = int(np.sum((y_true != c) & (y_pred == c)))
        fn = int(np.sum((y_true == c) & (y_pred != c)))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        per_class[c] = {"f1": round(f1, 4), "precision": round(prec, 4), "recall": round(rec, 4),
                        "support": int(np.sum(y_true == c)), "tp": tp, "fp": fp, "fn": fn}
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    confusions = []
    for i, true_c in enumerate(labels):
        for j, pred_c in enumerate(labels):
            if i == j: continue
            n = int(cm[i, j])
            if n > 0:
                confusions.append({"true": true_c, "predicted": pred_c, "count": n,
                                   "rate": round(n / max(int(cm[i].sum()), 1), 4)})
    confusions.sort(key=lambda x: -x["count"])
    misclassified = []
    for i, (yt, yp) in enumerate(zip(y_true, y_pred)):
        if yt == yp: continue
        entry = {"index": i, "id": ids[i] if ids and i < len(ids) else None,
                 "true": str(yt), "predicted": str(yp)}
        if proba is not None and i < len(proba):
            entry["confidence"] = round(float(np.max(proba[i])), 4)
        misclassified.append(entry)
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0, labels=labels))
    f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0, labels=labels))
    acc = float(accuracy_score(y_true, y_pred))
    diagnostics = []
    if f1_macro < MIN_ACCEPTABLE_F1_MACRO:
        diagnostics.append({"level": "critical",
            "msg": f"F1-macro={f1_macro:.2f} < seuil {MIN_ACCEPTABLE_F1_MACRO}",
            "action": "Ajouter des vidéos variées dans données/vidéo/"})
    elif f1_macro < MIN_GOOD_F1_MACRO:
        diagnostics.append({"level": "warning",
            "msg": f"F1-macro={f1_macro:.2f} acceptable mais perfectible",
            "action": "Enrichir les classes minoritaires"})
    else:
        diagnostics.append({"level": "ok", "msg": f"F1-macro={f1_macro:.2f} — qualité bonne", "action": None})
    for c, s in per_class.items():
        if s["support"] > 0 and s["f1"] < 0.4:
            diagnostics.append({"level": "warning",
                "msg": f"Classe '{c}' F1={s['f1']:.2f} (R={s['recall']:.2f}, P={s['precision']:.2f})",
                "action": f"Plus d'exemples '{c}'"})
        if s["support"] > 0 and s["recall"] < 0.3:
            diagnostics.append({"level": "critical",
                "msg": f"Classe '{c}' quasi non détectée (recall={s['recall']:.2f})",
                "action": f"Augmenter samples '{c}'"})
    if confusions:
        top = confusions[0]
        diagnostics.append({"level": "info",
            "msg": f"Confusion principale: {top['true']} → {top['predicted']} ({top['count']}x)",
            "action": f"Séparer mieux '{top['true']}' et '{top['predicted']}'"})
    return {
        "model": model_name, "n_samples": int(len(y_true)),
        "accuracy": round(acc, 4), "f1_macro": round(f1_macro, 4), "f1_weighted": round(f1_weighted, 4),
        "per_class": per_class, "confusion_matrix": {"labels": labels, "matrix": cm.tolist()},
        "top_confusions": confusions[:10], "misclassified": misclassified[:50],
        "n_misclassified": len(misclassified), "diagnostics": diagnostics,
        "report_text": classification_report(y_true, y_pred, labels=labels, zero_division=0),
    }

def print_f1_analysis(analysis):
    print("\n" + "-" * 56)
    print(f"  ANALYSE F1 — {analysis.get('model', '')}")
    print("-" * 56)
    print(f"  accuracy={analysis['accuracy']:.3f}  f1_macro={analysis['f1_macro']:.3f}  "
          f"erreurs={analysis['n_misclassified']}/{analysis['n_samples']}")
    for c, s in analysis.get("per_class", {}).items():
        print(f"    {c:10s} F1={s['f1']:.3f} P={s['precision']:.3f} R={s['recall']:.3f} n={s['support']}")
    for c in analysis.get("top_confusions", [])[:5]:
        print(f"    confusion: {c['true']} → {c['predicted']}: {c['count']}")
    for d in analysis.get("diagnostics", []):
        icon = {"ok": "✓", "warning": "⚠", "critical": "❌", "info": "ℹ"}.get(d["level"], "•")
        print(f"  {icon} [{d['level']}] {d['msg']}")
        if d.get("action"): print(f"      → {d['action']}")
    print("-" * 56 + "\n")

def _base_estimators():
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier
    return {
        "decision_tree": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        "extra_trees": ExtraTreesClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }

def hyperparam_search(X, y, n_iter=HYPERPARAM_N_ITER, refine: bool = None):
    """
    Recherche d'hyperparamètres multi-modèles optimisée (F1-macro).

    1) RandomizedSearchCV large sur 4 familles d'arbres
    2) Passe de raffinement locale autour du meilleur (optionnel)
    3) Export top essais + importance features
    """
    from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier

    if refine is None:
        refine = bool(HYPERPARAM_REFINE)

    results = {
        "started_at": datetime.utcnow().isoformat(),
        "models": {},
        "n_samples": int(len(y)),
        "n_features": int(X.shape[1]) if hasattr(X, "shape") else 0,
        "scoring": "f1_macro",
    }
    counts = _class_counts(y)
    min_class = min((v for v in counts.values() if v > 0), default=0)
    n_splits = min(int(HYPERPARAM_CV), max(2, min_class))
    if len(y) < n_splits * 2:
        n_splits = 2
    # Si très peu de données, limiter les essais
    effective_iter = int(n_iter)
    if len(y) < 20:
        effective_iter = min(effective_iter, 10)
        n_splits = min(n_splits, 3)

    bases = {
        "decision_tree": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        "extra_trees": ExtraTreesClassifier(random_state=RANDOM_STATE, n_jobs=-1),
        "gradient_boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }

    best_name, best_est, best_score = None, None, -1.0
    ranking = []

    for name, base in bases.items():
        grid = PARAM_GRIDS.get(name, {})
        if not grid:
            continue
        # n_iter limité par le produit cartésien approximatif
        max_combos = 1
        for v in grid.values():
            max_combos *= max(len(v), 1)
        n_try = min(effective_iter, max_combos, 40)
        print(f"[hyper] Recherche {name} ({n_try} essais, cv={n_splits})…")
        try:
            cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
            search = RandomizedSearchCV(
                base, grid,
                n_iter=n_try,
                scoring="f1_macro",
                cv=cv,
                random_state=RANDOM_STATE,
                n_jobs=-1,
                refit=True,
                error_score=0.0,
                return_train_score=True,
            )
            search.fit(X, y)
            cv_res = search.cv_results_
            # Top 5 essais
            order = np.argsort(cv_res["mean_test_score"])[::-1][:5]
            top = []
            for i in order:
                top.append({
                    "rank": int(cv_res["rank_test_score"][i]),
                    "mean_f1_macro": round(float(cv_res["mean_test_score"][i]), 4),
                    "std_f1_macro": round(float(cv_res["std_test_score"][i]), 4),
                    "mean_train_f1": round(float(cv_res["mean_train_score"][i]), 4),
                    "params": {k: (None if v is None else (int(v) if isinstance(v, (np.integer,)) else
                              float(v) if isinstance(v, (float, np.floating)) else v))
                               for k, v in cv_res["params"][i].items()},
                })
            entry = {
                "best_score_cv_f1_macro": round(float(search.best_score_), 4),
                "best_params": search.best_params_,
                "n_iter": n_try,
                "cv_splits": n_splits,
                "top_trials": top,
                "overfit_gap": round(
                    float(cv_res["mean_train_score"][search.best_index_] - search.best_score_), 4
                ),
            }
            results["models"][name] = entry
            ranking.append((float(search.best_score_), name, search.best_estimator_, entry))
            print(
                f"[hyper]   {name}: cv_f1={entry['best_score_cv_f1_macro']:.3f} "
                f"gap_train={entry['overfit_gap']:.3f} params={search.best_params_}"
            )
            if search.best_score_ > best_score:
                best_score = float(search.best_score_)
                best_name, best_est = name, search.best_estimator_
        except Exception as e:
            print(f"[hyper]   {name} ÉCHEC: {e}")
            results["models"][name] = {"error": str(e)}

    ranking.sort(key=lambda x: x[0], reverse=True)
    results["ranking"] = [
        {"model": n, "cv_f1_macro": round(s, 4)} for s, n, _, _ in ranking
    ]

    # --- Passe de raffinement autour du meilleur ---
    if refine and best_est is not None and best_name is not None:
        print(f"[hyper] Raffinement autour de {best_name}…")
        try:
            fine_grid = _refine_grid(best_name, getattr(best_est, "get_params")())
            if fine_grid:
                base = bases[best_name]
                cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE + 1)
                n_ref = min(int(HYPERPARAM_REFINE_ITER), 20)
                search2 = RandomizedSearchCV(
                    base, fine_grid, n_iter=n_ref, scoring="f1_macro",
                    cv=cv, random_state=RANDOM_STATE + 7, n_jobs=-1, refit=True, error_score=0.0,
                )
                search2.fit(X, y)
                results["refine"] = {
                    "model": best_name,
                    "best_score_cv_f1_macro": round(float(search2.best_score_), 4),
                    "best_params": search2.best_params_,
                    "improved": bool(search2.best_score_ > best_score + 1e-4),
                }
                print(
                    f"[hyper]   refine: cv_f1={search2.best_score_:.3f} "
                    f"(avant {best_score:.3f}) params={search2.best_params_}"
                )
                if search2.best_score_ > best_score:
                    best_score = float(search2.best_score_)
                    best_est = search2.best_estimator_
                    results["models"][best_name]["best_score_cv_f1_macro"] = round(best_score, 4)
                    results["models"][best_name]["best_params"] = search2.best_params_
                    results["models"][best_name]["refined"] = True
        except Exception as e:
            print(f"[hyper]   refine ÉCHEC: {e}")
            results["refine"] = {"error": str(e)}

    # Importance des features du meilleur modèle
    if best_est is not None and hasattr(best_est, "feature_importances_"):
        imp = best_est.feature_importances_
        names = INDICATOR_IDS if len(INDICATOR_IDS) == len(imp) else [f"f{i}" for i in range(len(imp))]
        pairs = sorted(zip(names, imp), key=lambda x: -x[1])[:15]
        results["top_features"] = [
            {"feature": n, "importance": round(float(v), 4)} for n, v in pairs
        ]
        sk_imp = sum(float(v) for n, v in zip(names, imp) if str(n).startswith("sk_"))
        results["skeleton_importance_share"] = round(sk_imp / max(float(np.sum(imp)), 1e-9), 4)
        print(f"[hyper] Share importance squelette sk_* = {results['skeleton_importance_share']:.2%}")
        print("[hyper] Top features:", ", ".join(f"{n}={v:.3f}" for n, v in pairs[:8]))

    results["best_model"] = best_name
    results["best_cv_f1_macro"] = round(best_score, 4) if best_score >= 0 else None
    results["finished_at"] = datetime.utcnow().isoformat()
    return results, best_name, best_est, best_score


def _refine_grid(model_name: str, best_params: dict) -> dict:
    """Construit une grille locale autour des meilleurs paramètres."""
    grid = {}
    bp = dict(best_params or {})

    def _ints(center, deltas, lo=1, hi=500):
        vals = set()
        if center is None:
            return [None, 8, 12, 16]
        for d in deltas:
            v = int(center) + int(d)
            if lo <= v <= hi:
                vals.add(v)
        vals.add(int(center))
        return sorted(vals)

    if "n_estimators" in bp and bp["n_estimators"] is not None:
        grid["n_estimators"] = _ints(bp["n_estimators"], [-60, -30, -10, 0, 10, 30, 60], 30, 400)
    if "max_depth" in bp:
        if bp["max_depth"] is None:
            grid["max_depth"] = [None, 10, 14, 18]
        else:
            grid["max_depth"] = _ints(bp["max_depth"], [-3, -1, 0, 1, 3], 2, 30) + [None]
    if "min_samples_leaf" in bp and bp["min_samples_leaf"] is not None:
        grid["min_samples_leaf"] = _ints(bp["min_samples_leaf"], [-2, -1, 0, 1, 2], 1, 20)
    if "min_samples_split" in bp and bp["min_samples_split"] is not None:
        grid["min_samples_split"] = _ints(bp["min_samples_split"], [-2, 0, 2], 2, 20)
    if "learning_rate" in bp and bp["learning_rate"] is not None:
        lr = float(bp["learning_rate"])
        grid["learning_rate"] = sorted({round(lr * f, 4) for f in (0.6, 0.8, 1.0, 1.2, 1.5) if 0.01 <= lr * f <= 0.5})
    if "subsample" in bp and bp["subsample"] is not None:
        s = float(bp["subsample"])
        grid["subsample"] = sorted({round(min(1.0, max(0.5, s + d)), 2) for d in (-0.15, -0.05, 0, 0.05, 0.1)})
    if "max_features" in bp:
        grid["max_features"] = list({bp["max_features"], "sqrt", "log2", 0.5, None})
    if "criterion" in bp:
        grid["criterion"] = ["gini", "entropy"]
    if "class_weight" in bp:
        grid["class_weight"] = ["balanced", "balanced_subsample"] if model_name == "random_forest" else ["balanced"]
    if "bootstrap" in bp:
        grid["bootstrap"] = [True, False]
    # Filtrer clés vides
    return {k: v for k, v in grid.items() if v}


def train_trees(n_estimators=N_ESTIMATORS_DEFAULT, max_depth=MAX_DEPTH_DEFAULT,
                min_samples=MIN_SAMPLES_TOTAL, n_iter=HYPERPARAM_N_ITER, skip_hyper=False):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    TREE_EXPORT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(RANDOM_STATE)
    report: Dict[str, Any] = {"started_at": datetime.utcnow().isoformat(), "status": "failed",
                              "quality": "rejected", "errors": []}
    try:
        X_raw, y, ids = _load_xy()
    except Exception as e:
        err = TrainingError(f"Chargement features: {e}")
        report["errors"].append(err.to_dict()); print(f"[trees] ❌ {err.message}")
        TRAIN_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report
    counts = _class_counts(y)
    report.update({"n_samples": int(len(y)), "n_features": int(X_raw.shape[1]) if len(X_raw) else 0,
                   "feature_names": INDICATOR_IDS, "classes": list(CLASSES), "class_counts": counts})
    print(f"[trees] Échantillons={len(y)} classes={counts}")

    # ── Checklist qualité données (obligatoire) ──
    try:
        from ml.data_checklist import run_data_checklist, impute_missing
        checklist = run_data_checklist(X_raw, y, ids, feature_names=INDICATOR_IDS, block_on_fail=True)
        report["data_checklist"] = {
            "overall": checklist.get("overall"),
            "passed": checklist.get("passed"),
            "log": "data/models/data_checklist.json",
            "checks": [
                {"id": c["id"], "status": c["status"], "name": c["name"]}
                for c in checklist.get("checks", [])
            ],
        }
        X_raw = impute_missing(X_raw)
    except ValueError as e:
        report["status"] = "blocked_checklist"
        report["errors"].append({"error": {"code": "DATA_CHECKLIST_FAILED", "message": str(e)}})
        print(f"[trees] ❌ Checklist: {e}")
        TRAIN_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report
    except Exception as e:
        print(f"[trees] ⚠ Checklist partielle: {e}")
        report["data_checklist"] = {"overall": "warning", "error": str(e)}

    try:
        if len(y) < min_samples:
            raise InsufficientDataError(f"Pas assez d'échantillons ({len(y)} < {min_samples})",
                                        details={"n": len(y), "counts": counts})
        if sum(1 for v in counts.values() if v > 0) < 2:
            raise InsufficientDataError("Au moins 2 classes requises", details={"counts": counts})
    except LearningError as e:
        report["errors"].append(e.to_dict()); print(f"[trees] ❌ [{e.code}] {e.message}")
        TRAIN_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report
    try:
        scaler, X = _fit_scaler(X_raw)
        try:
            from ml.imbalance import balance_dataset
            X_bal, y_bal, imb_report = balance_dataset(X, y, strategy="auto", rng=rng)
            report["imbalance"] = imb_report
            try:
                from ml.visualize_leakage import plot_class_balance
                plot_class_balance(y, y_bal)
            except Exception:
                pass
        except Exception as e:
            print(f"[trees] imbalance module fallback: {e}")
            X_bal, y_bal = _oversample_balance(X, y, rng)
        print(f"[trees] Balance → {len(y_bal)} {_class_counts(y_bal)}")
    except Exception as e:
        err = TrainingError(f"Préprocessing: {e}")
        report["errors"].append(err.to_dict())
        TRAIN_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report
    best_name, best_model, best_cv = None, None, -1.0
    if not skip_hyper:
        try:
            hyper_info, best_name, best_model, best_cv = hyperparam_search(X_bal, y_bal, n_iter=n_iter)
            HYPERPARAM_LOG.write_text(json.dumps(hyper_info, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
            report["hyperparam"] = {
                "best_model": best_name,
                "best_cv_f1_macro": hyper_info.get("best_cv_f1_macro"),
                "ranking": hyper_info.get("ranking"),
                "refine": hyper_info.get("refine"),
                "top_features": hyper_info.get("top_features"),
                "skeleton_importance_share": hyper_info.get("skeleton_importance_share"),
                "log": str(HYPERPARAM_LOG),
            }
        except Exception as e:
            print(f"[trees] ⚠ Hyperparam échoué: {e}")
            report["errors"].append({"error": {"code": "HYPERPARAM_FAILED", "message": str(e)}})
            skip_hyper = True
    if skip_hyper or best_model is None:
        from sklearn.ensemble import ExtraTreesClassifier
        best_name = "extra_trees_default"
        best_model = ExtraTreesClassifier(n_estimators=n_estimators, max_depth=max_depth, min_samples_leaf=2,
            class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1)
        best_model.fit(X_bal, y_bal)
        best_cv = 0.0
    X_tr, X_te, y_tr, y_te = _safe_split(X_bal, y_bal)
    try:
        best_model.fit(X_tr, y_tr)
        y_pred = best_model.predict(X_te) if len(X_te) else best_model.predict(X_tr)
        y_true = y_te if len(X_te) else y_tr
        proba = None
        if hasattr(best_model, "predict_proba"):
            raw_p = best_model.predict_proba(X_te if len(X_te) else X_tr)
            model_classes = list(getattr(best_model, "classes_", CLASSES))
            aligned = np.zeros((len(y_true), len(CLASSES)))
            for i, c in enumerate(model_classes):
                if c in CLASSES: aligned[:, list(CLASSES).index(c)] = raw_p[:, i]
            proba = aligned
        analysis = analyze_f1_errors(y_true, y_pred, proba=proba, model_name=best_name or "")
        print_f1_analysis(analysis)
        F1_ANALYSIS_LOG.write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8")
        report["f1_analysis"] = {"f1_macro": analysis["f1_macro"], "f1_weighted": analysis["f1_weighted"],
            "per_class": analysis["per_class"], "n_misclassified": analysis["n_misclassified"],
            "diagnostics": analysis["diagnostics"], "log": str(F1_ANALYSIS_LOG)}
    except Exception as e:
        err = TrainingError(f"Évaluation F1: {e}")
        report["errors"].append(err.to_dict())
        analysis = {"f1_macro": 0.0, "diagnostics": []}
    try:
        best_model.fit(X_bal, y_bal)
    except Exception as e:
        err = TrainingError(f"Refit: {e}")
        report["errors"].append(err.to_dict())
        TRAIN_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report
    try:
        from sklearn.tree import DecisionTreeClassifier, export_text
        dt = DecisionTreeClassifier(max_depth=max_depth, min_samples_leaf=2, class_weight="balanced",
                                    random_state=RANDOM_STATE)
        dt.fit(X_bal, y_bal)
        (TREE_EXPORT / "tree_decision_rules.txt").write_text(
            export_text(dt, feature_names=INDICATOR_IDS, decimals=3), encoding="utf-8")
    except Exception:
        dt = None
    importances = {}
    if hasattr(best_model, "feature_importances_"):
        importances = {n: float(i) for n, i in
                       sorted(zip(INDICATOR_IDS, best_model.feature_importances_), key=lambda x: -x[1])}
        (TREE_EXPORT / "importance.json").write_text(json.dumps(importances, indent=2), encoding="utf-8")
    import joblib
    bundle = {"model": best_model, "model_name": best_name, "decision_tree": dt,
              "random_forest": best_model if best_name and "forest" in str(best_name) else None,
              "scaler": scaler, "feature_names": INDICATOR_IDS, "classes": list(CLASSES),
              "importances": importances, "metrics": report.get("f1_analysis"),
              "hyperparam": report.get("hyperparam"), "trained_at": datetime.utcnow().isoformat(),
              "n_train_balanced": int(len(y_bal)), "class_counts_original": counts}
    if bundle["random_forest"] is None:
        from sklearn.ensemble import RandomForestClassifier
        rf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, min_samples_leaf=2,
            class_weight="balanced_subsample", random_state=RANDOM_STATE, n_jobs=-1)
        rf.fit(X_bal, y_bal)
        bundle["random_forest"] = rf
    try:
        joblib.dump(bundle, TREE_MODEL)
        joblib.dump(bundle, BEST_MODEL)
    except Exception as e:
        err = TrainingError(f"Sauvegarde: {e}")
        report["errors"].append(err.to_dict())
        TRAIN_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report
    f1 = float(analysis.get("f1_macro", 0.0))
    quality = "good" if f1 >= MIN_GOOD_F1_MACRO else ("acceptable" if f1 >= MIN_ACCEPTABLE_F1_MACRO else "weak")
    if quality == "weak":
        report["errors"].append(LowQualityModelError(
            f"F1-macro={f1:.2f} sous le seuil", details={"f1_macro": f1}).to_dict())
    report.update({"status": "completed", "quality": quality, "best_model": best_name,
        "best_cv_f1_macro": round(best_cv, 4) if best_cv else None, "model_path": str(TREE_MODEL),
        "top_features": list(importances.items())[:8], "finished_at": datetime.utcnow().isoformat()})
    TRAIN_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    METRICS_LOG.write_text(json.dumps({"best_model": best_name, "quality": quality,
        "f1_analysis": report.get("f1_analysis"), "hyperparam": report.get("hyperparam"),
        "class_counts": counts, "errors": report.get("errors")}, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8")
    print(f"[trees] best={best_name} quality={quality} f1_macro={f1:.3f} → {TREE_MODEL}")
    return report

def predict_proba_vec(feature_vec):
    import joblib
    if not TREE_MODEL.exists():
        raise ModelNotFoundError()
    try:
        bundle = joblib.load(TREE_MODEL)
        vec = np.asarray(feature_vec, dtype=np.float64).reshape(1, -1)
        if bundle.get("scaler") is not None:
            vec = bundle["scaler"].transform(vec)
        model = bundle.get("model") or bundle.get("random_forest")
        classes = list(bundle.get("classes") or CLASSES)
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(vec)[0]
            model_classes = list(getattr(model, "classes_", classes))
            full = np.zeros(len(classes))
            for i, c in enumerate(model_classes):
                if c in classes: full[classes.index(c)] = proba[i]
            idx = int(np.argmax(full))
            return classes[idx], float(full[idx]), full
        return str(model.predict(vec)[0]), 1.0, np.ones(len(classes)) / len(classes)
    except ModelNotFoundError:
        raise
    except Exception as e:
        raise PredictionError(str(e)) from e

def describe_trees():
    info = {"strategy": "RandomizedSearchCV F1-macro DT/RF/ExtraTrees/GB",
            "f1_analysis": str(F1_ANALYSIS_LOG), "hyperparam_log": str(HYPERPARAM_LOG),
            "quality_gates": {"acceptable": MIN_ACCEPTABLE_F1_MACRO, "good": MIN_GOOD_F1_MACRO},
            "target_classes": list(CLASSES), "features": INDICATOR_IDS}
    if TREE_MODEL.exists():
        try:
            import joblib
            b = joblib.load(TREE_MODEL)
            info["trained"] = {"model_name": b.get("model_name"), "at": b.get("trained_at"),
                               "metrics": b.get("metrics")}
        except Exception as e:
            info["load_error"] = str(e)
    return info


# --- Compat: déléguer à sklearn Pipeline ---
def train_with_sklearn_pipeline(X, y, skip_hyper=False):
    from ml.sklearn_pipeline import fit_search_pipeline, save_pipeline, evaluate_pipeline
    if skip_hyper:
        from ml.sklearn_pipeline import build_pipeline
        pipe = build_pipeline("extra_trees")
        pipe.fit(X, y)
        hyper = {"best_model": "extra_trees", "best_cv_f1_macro": None}
    else:
        pipe, hyper = fit_search_pipeline(X, y)
    save_pipeline(pipe, meta=hyper)
    return pipe, hyper
