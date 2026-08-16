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

def hyperparam_search(X, y, n_iter=HYPERPARAM_N_ITER):
    from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
    results = {"started_at": datetime.utcnow().isoformat(), "models": {}}
    counts = _class_counts(y)
    min_class = min((v for v in counts.values() if v > 0), default=0)
    n_splits = min(HYPERPARAM_CV, min_class) if min_class >= 2 else 2
    if len(y) < n_splits * 2: n_splits = 2
    best_name, best_est, best_score = None, None, -1.0
    for name, base in _base_estimators().items():
        grid = PARAM_GRIDS.get(name, {})
        if not grid: continue
        print(f"[hyper] Recherche {name} ({n_iter} essais, cv={n_splits})…")
        try:
            cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
            search = RandomizedSearchCV(base, grid, n_iter=min(n_iter, 20), scoring="f1_macro",
                cv=cv, random_state=RANDOM_STATE, n_jobs=-1, refit=True, error_score=0.0)
            search.fit(X, y)
            entry = {"best_score_cv_f1_macro": round(float(search.best_score_), 4),
                     "best_params": search.best_params_, "n_iter": int(n_iter), "cv_splits": n_splits}
            results["models"][name] = entry
            print(f"[hyper]   {name}: cv_f1={entry['best_score_cv_f1_macro']:.3f} params={search.best_params_}")
            if search.best_score_ > best_score:
                best_score = float(search.best_score_)
                best_name, best_est = name, search.best_estimator_
        except Exception as e:
            print(f"[hyper]   {name} ÉCHEC: {e}")
            results["models"][name] = {"error": str(e)}
    results["best_model"] = best_name
    results["best_cv_f1_macro"] = round(best_score, 4) if best_score >= 0 else None
    results["finished_at"] = datetime.utcnow().isoformat()
    return results, best_name, best_est, best_score

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
            report["hyperparam"] = {"best_model": best_name, "best_cv_f1_macro": hyper_info.get("best_cv_f1_macro"),
                                    "log": str(HYPERPARAM_LOG)}
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
