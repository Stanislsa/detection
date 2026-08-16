"""DecisionTree + RandomForest pour normal/urgent/critique."""
from __future__ import annotations
import json
from datetime import datetime
from typing import Any, Dict, Tuple
import numpy as np
from ml.config import MODELS_DIR, TREE_MODEL, TREE_EXPORT, TRAIN_LOG, CLASSES
from ml.indicators import INDICATOR_IDS
from ml.features import build_feature_table

def _load_xy():
    X, y, _ = build_feature_table()
    mask = np.array([yi in CLASSES for yi in y]) if len(y) else np.array([], dtype=bool)
    return (X[mask], y[mask]) if mask.size and mask.any() else (X, y)

def train_trees(n_estimators=100, max_depth=8, min_samples=3) -> Dict[str, Any]:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    TREE_EXPORT.mkdir(parents=True, exist_ok=True)
    X, y = _load_xy()
    report = {"started_at": datetime.utcnow().isoformat(), "n_samples": int(len(y)),
              "n_features": int(X.shape[1]) if len(X) else 0, "feature_names": INDICATOR_IDS,
              "classes": list(CLASSES), "status": "failed", "trees": {}}
    if len(y) < min_samples:
        report["error"] = f"Pas assez d'echantillons ({len(y)})"
        TRAIN_LOG.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[trees] {report['error']}"); return report
    from sklearn.tree import DecisionTreeClassifier, export_text
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    import joblib
    try:
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25 if len(y)>=8 else 0.2, random_state=42)
    except ValueError:
        X_tr, X_te, y_tr, y_te = X, X, y, y
    dt = DecisionTreeClassifier(max_depth=max_depth, class_weight="balanced", random_state=42)
    dt.fit(X_tr, y_tr)
    dt_acc = float(accuracy_score(y_te, dt.predict(X_te))) if len(X_te) else 0.0
    rules_path = TREE_EXPORT / "tree_decision_rules.txt"
    rules_path.write_text(export_text(dt, feature_names=INDICATOR_IDS, decimals=3), encoding="utf-8")
    rf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth,
                                class_weight="balanced", random_state=42, n_jobs=-1)
    rf.fit(X_tr, y_tr)
    rf_pred = rf.predict(X_te) if len(X_te) else []
    rf_acc = float(accuracy_score(y_te, rf_pred)) if len(X_te) else 0.0
    importances = {n: float(i) for n, i in sorted(zip(INDICATOR_IDS, rf.feature_importances_), key=lambda x: -x[1])}
    (TREE_EXPORT / "importance.json").write_text(json.dumps(importances, indent=2), encoding="utf-8")
    (TREE_EXPORT / "forest_summary.json").write_text(json.dumps({
        "n_estimators": n_estimators, "rf_accuracy": round(rf_acc,4), "dt_accuracy": round(dt_acc,4),
        "top_indicators": list(importances.items())[:10],
        "tree_depths": [int(e.get_depth()) for e in rf.estimators_[:20]],
    }, indent=2), encoding="utf-8")
    for i, est in enumerate(rf.estimators_[:3]):
        (TREE_EXPORT / f"forest_tree_{i}_rules.txt").write_text(
            export_text(est, feature_names=INDICATOR_IDS, decimals=3), encoding="utf-8")
    joblib.dump({"decision_tree": dt, "random_forest": rf, "feature_names": INDICATOR_IDS,
                 "classes": list(CLASSES), "importances": importances,
                 "trained_at": datetime.utcnow().isoformat()}, TREE_MODEL)
    report.update({
        "status": "completed", "model_path": str(TREE_MODEL), "export_dir": str(TREE_EXPORT),
        "trees": {
            "decision_tree": {"type": "DecisionTreeClassifier", "depth": int(dt.get_depth()),
                              "n_leaves": int(dt.get_n_leaves()), "accuracy": round(dt_acc,4),
                              "rules_file": str(rules_path)},
            "random_forest": {"type": "RandomForestClassifier", "n_estimators": n_estimators,
                              "accuracy": round(rf_acc,4), "top_features": list(importances.items())[:5]},
        },
        "classification_report": classification_report(y_te, rf_pred, zero_division=0) if len(y_te) else "",
        "finished_at": datetime.utcnow().isoformat(),
    })
    TRAIN_LOG.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[trees] DT depth={dt.get_depth()} RF n={n_estimators} → {TREE_MODEL}")
    return report

def describe_trees():
    info = {"models": {"decision_tree": "DecisionTreeClassifier", "random_forest": "RandomForestClassifier"},
            "storage": {"joblib": str(TREE_MODEL), "export": str(TREE_EXPORT)},
            "split_criteria": "Gini", "target_classes": list(CLASSES), "features": INDICATOR_IDS}
    if TREE_MODEL.exists():
        try:
            import joblib
            b = joblib.load(TREE_MODEL)
            info["trained"] = {"at": b.get("trained_at"), "importances": b.get("importances"),
                               "rf_n_trees": len(b["random_forest"].estimators_)}
        except Exception as e:
            info["load_error"] = str(e)
    return info
