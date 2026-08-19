"""
Prétraitement ML — pipeline ordonné (données brutes → modèle).

Ordre strict (anti-fuite) :
  1. Données brutes (features extraites des clips)
  2. Exploration initiale (EDA)
  3. Nettoyage
  4. Valeurs manquantes / aberrantes
  5. Encodage + normalisation + transformations  ← fit sur TRAIN uniquement
  6. Séparation train / validation / test
  7. Rééquilibrage (train seulement)
  8. Modèle de Machine Learning

Usage :
  from ml.preprocess import PreprocessPipeline
  pipe = PreprocessPipeline()
  bundles = pipe.run()          # charge features + full pipeline
  model_report = pipe.train()   # entraînement sur bundles['train']
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from ml.config import (
    CLASSES,
    MODELS_DIR,
    RANDOM_STATE,
    TEST_SIZE,
    SCALER_PATH,
)
from ml.indicators import INDICATOR_IDS

PREPROCESS_LOG = MODELS_DIR / "preprocess_pipeline.json"


@dataclass
class DataBundle:
    """Jeux X, y, ids après split."""
    X: np.ndarray
    y: np.ndarray
    ids: List[str]
    name: str = ""

    @property
    def n(self) -> int:
        return int(len(self.y))


class PreprocessPipeline:
    """
    Chaîne de prétraitement complète avant ML.
    """

    def __init__(
        self,
        test_size: float = TEST_SIZE,
        val_size: float = 0.15,
        random_state: int = RANDOM_STATE,
        outlier_k: float = 3.0,
        imbalance_strategy: str = "auto",
        block_on_leakage: bool = True,
    ):
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        self.outlier_k = outlier_k
        self.imbalance_strategy = imbalance_strategy
        self.block_on_leakage = block_on_leakage
        self.feature_names: List[str] = list(INDICATOR_IDS)
        self.scaler = None
        self.report: Dict[str, Any] = {"steps": [], "started_at": datetime.utcnow().isoformat()}
        self.bundles: Dict[str, DataBundle] = {}
        self._X_raw = None
        self._y_raw = None
        self._ids_raw: List[str] = []

    # ── 1. Données brutes ─────────────────────────────────────
    def load_raw(self) -> "PreprocessPipeline":
        from ml.features import build_feature_table
        from ml.config import CLASSES as CL

        X, y, ids = build_feature_table()
        mask = np.array([yi in CL for yi in y]) if len(y) else np.array([], dtype=bool)
        if mask.size and mask.any():
            X, y = X[mask], y[mask]
            ids = [ids[i] for i, m in enumerate(mask) if m]
        self._X_raw = np.asarray(X, dtype=np.float64)
        self._y_raw = np.asarray(y)
        self._ids_raw = list(ids)
        self.feature_names = list(INDICATOR_IDS)[: self._X_raw.shape[1]] if self._X_raw.ndim == 2 else list(INDICATOR_IDS)
        self._log("1_raw", {
            "n": int(len(self._y_raw)),
            "d": int(self._X_raw.shape[1]) if self._X_raw.ndim == 2 else 0,
            "classes": {c: int(np.sum(self._y_raw == c)) for c in CLASSES},
        })
        print(f"[preprocess:1] Données brutes n={len(self._y_raw)} d={self._X_raw.shape[1] if len(self._y_raw) else 0}")
        return self

    # ── 2. Exploration initiale ───────────────────────────────
    def explore(self) -> "PreprocessPipeline":
        from ml.eda import run_eda, print_eda
        from ml.leakage import detect_leakage, print_leakage_report

        eda = run_eda(self._X_raw, self._y_raw, self._ids_raw, self.feature_names)
        print_eda(eda)
        leak = detect_leakage(self._X_raw, self._y_raw, self._ids_raw, self.feature_names)
        print_leakage_report(leak, X=self._X_raw, y=self._y_raw, feature_names=self.feature_names)
        try:
            from ml.visualize_leakage import visualize_all
            visualize_all(self._X_raw, self._y_raw, leak, feature_names=self.feature_names)
        except Exception as e:
            print(f"[preprocess:2] viz skip: {e}")
        self.report["eda"] = {"log": "data/models/eda_report.json", "insights": eda.get("insights")}
        self.report["leakage"] = {"status": leak.get("status"), "n_issues": leak.get("n_issues")}
        if self.block_on_leakage and leak.get("status") == "fail":
            raise ValueError(f"Fuites détectées — arrêt prétraitement: {leak.get('issues', [])[:3]}")
        self._log("2_explore", {"eda_ok": True, "leakage": leak.get("status")})
        print("[preprocess:2] Exploration initiale (EDA + fuites) OK")
        return self

    # ── 3. Nettoyage ──────────────────────────────────────────
    def clean(self) -> "PreprocessPipeline":
        X, y, ids = self._X_raw, self._y_raw, self._ids_raw
        n0 = len(y)
        # supprimer lignes entièrement NaN
        if len(y) and X.ndim == 2:
            row_ok = ~np.all(~np.isfinite(X), axis=1)
            X, y = X[row_ok], y[row_ok]
            ids = [ids[i] for i, ok in enumerate(row_ok) if ok]
        # labels valides uniquement
        mask = np.array([str(yi) in CLASSES for yi in y])
        X, y = X[mask], y[mask]
        ids = [ids[i] for i, ok in enumerate(mask) if ok]
        # aligner dimensions features
        d = min(X.shape[1], len(self.feature_names)) if X.ndim == 2 and len(y) else 0
        if d and X.shape[1] != d:
            X = X[:, :d]
        self._X_raw, self._y_raw, self._ids_raw = X, y, ids
        self._log("3_clean", {"n_before": n0, "n_after": int(len(y)), "dropped": int(n0 - len(y))})
        print(f"[preprocess:3] Nettoyage → n={len(y)} (drop={n0 - len(y)})")
        return self

    # ── 4. Manquants / aberrants ──────────────────────────────
    def handle_missing_outliers(self) -> "PreprocessPipeline":
        from ml.data_checklist import impute_missing

        X = impute_missing(self._X_raw)
        # winsorize léger (clip IQR×k) — pas de suppression agressive
        n_out = 0
        if len(X):
            q1 = np.percentile(X, 25, axis=0)
            q3 = np.percentile(X, 75, axis=0)
            iqr = np.where(q3 - q1 < 1e-12, 1.0, q3 - q1)
            lo, hi = q1 - self.outlier_k * iqr, q3 + self.outlier_k * iqr
            n_out = int(np.any((X < lo) | (X > hi), axis=1).sum())
            X = np.clip(X, lo, hi)
        self._X_raw = X
        self._log("4_missing_outliers", {
            "imputed": True,
            "outliers_winsorized_rows": n_out,
            "method": f"median_impute + IQR_clip_k={self.outlier_k}",
        })
        print(f"[preprocess:4] NaN imputés (médiane), outliers winsorisés (lignes touchées≈{n_out})")
        return self

    # ── 5 + 6. Split PUIS encode / scale / transform ──────────
    def split_encode_scale(self) -> "PreprocessPipeline":
        """
        IMPORTANT : split d'abord, puis fit scaler sur train uniquement.
        """
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler, LabelEncoder

        X, y, ids = self._X_raw, self._y_raw, np.array(self._ids_raw)
        if len(y) < 4:
            raise ValueError(f"Trop peu d'échantillons pour split ({len(y)})")

        counts = {c: int(np.sum(y == c)) for c in CLASSES}
        present = [c for c, v in counts.items() if v > 0]
        stratify = y if (len(present) >= 2 and all(counts[c] >= 2 for c in present)) else None

        # 6a. train+val  vs  test
        idx = np.arange(len(y))
        i_tv, i_te = train_test_split(
            idx, test_size=self.test_size, random_state=self.random_state, stratify=stratify,
        )
        # 6b. train vs val
        y_tv = y[i_tv]
        counts_tv = {c: int(np.sum(y_tv == c)) for c in CLASSES}
        present_tv = [c for c, v in counts_tv.items() if v > 0]
        strat_tv = y_tv if (len(present_tv) >= 2 and all(counts_tv[c] >= 2 for c in present_tv)) else None
        relative_val = self.val_size / max(1e-6, (1.0 - self.test_size))
        relative_val = min(0.4, max(0.1, relative_val))
        try:
            i_tr, i_va = train_test_split(
                i_tv, test_size=relative_val, random_state=self.random_state, stratify=strat_tv,
            )
        except ValueError:
            i_tr, i_va = train_test_split(
                i_tv, test_size=relative_val, random_state=self.random_state,
            )

        X_tr, y_tr = X[i_tr], y[i_tr]
        X_va, y_va = X[i_va], y[i_va]
        X_te, y_te = X[i_te], y[i_te]
        ids_tr = [str(ids[i]) for i in i_tr]
        ids_va = [str(ids[i]) for i in i_va]
        ids_te = [str(ids[i]) for i in i_te]

        # 5. Encodage labels (fit sur train)
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(list(CLASSES))
        # on garde y en string pour sklearn trees (classes_), mais documente l'encodage
        y_codes_map = {c: i for i, c in enumerate(self.label_encoder.classes_)}

        # 5. Normalisation — fit TRAIN only
        self.scaler = StandardScaler()
        X_tr_s = self.scaler.fit_transform(X_tr)
        X_va_s = self.scaler.transform(X_va)
        X_te_s = self.scaler.transform(X_te)
        try:
            import joblib
            SCALER_PATH.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.scaler, SCALER_PATH)
        except Exception:
            pass

        self.bundles = {
            "train": DataBundle(X_tr_s, y_tr, ids_tr, "train"),
            "val": DataBundle(X_va_s, y_va, ids_va, "val"),
            "test": DataBundle(X_te_s, y_te, ids_te, "test"),
            "train_raw_unscaled": DataBundle(X_tr, y_tr, ids_tr, "train_raw"),
            "val_raw_unscaled": DataBundle(X_va, y_va, ids_va, "val_raw"),
            "test_raw_unscaled": DataBundle(X_te, y_te, ids_te, "test_raw"),
        }
        self._log("5_6_split_scale", {
            "test_size": self.test_size,
            "val_size": self.val_size,
            "n_train": len(y_tr),
            "n_val": len(y_va),
            "n_test": len(y_te),
            "stratify": stratify is not None,
            "scaler": "StandardScaler fit on train only",
            "label_encoding": y_codes_map,
            "feature_transform": "z-score",
        })
        print(
            f"[preprocess:5-6] Split train/val/test = {len(y_tr)}/{len(y_va)}/{len(y_te)} "
            f"| StandardScaler fit=train"
        )
        return self

    # ── 7. Rééquilibrage (train only) ─────────────────────────
    def balance_train(self) -> "PreprocessPipeline":
        from ml.imbalance import balance_dataset
        from ml.visualize_leakage import plot_class_balance

        tr = self.bundles["train"]
        X_bal, y_bal, imb = balance_dataset(
            tr.X, tr.y, strategy=self.imbalance_strategy,
            rng=np.random.default_rng(self.random_state),
        )
        try:
            plot_class_balance(tr.y, y_bal)
        except Exception:
            pass
        self.bundles["train"] = DataBundle(X_bal, y_bal, tr.ids, "train_balanced")
        self.report["imbalance"] = imb
        self._log("7_balance_train", {"method": imb.get("method_used"), "n_after": len(y_bal)})
        print(f"[preprocess:7] Rééquilibrage train → n={len(y_bal)}")
        return self

    # ── Orchestrateur ─────────────────────────────────────────
    def run(self) -> Dict[str, DataBundle]:
        (
            self.load_raw()
            .explore()
            .clean()
            .handle_missing_outliers()
            .split_encode_scale()
            .balance_train()
        )
        self.report["finished_at"] = datetime.utcnow().isoformat()
        self.report["status"] = "ready_for_ml"
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        PREPROCESS_LOG.write_text(json.dumps(self.report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        print(f"[preprocess] Prêt pour le modèle — log {PREPROCESS_LOG}")
        return self.bundles

    def train_model(self, skip_hyper: bool = False) -> Dict[str, Any]:
        """Étape 8 — sklearn Pipeline (scaler + clf) anti-fuite en CV."""
        from ml.pipeline_optimize import run_optimized_training

        if "train" not in self.bundles:
            self.run()

        tr = self.bundles["train"]
        va = self.bundles.get("val")
        te = self.bundles.get("test")
        print(f"[ml:8] sklearn Pipeline | train={tr.n} val={getattr(va, 'n', 0)} test={getattr(te, 'n', 0)}")

        # Note: train est déjà scalé dans split_encode_scale.
        # Pour le Pipeline sklearn (scaler interne), on préfère les features non scalées.
        tr_raw = self.bundles.get("train_raw_unscaled")
        va_raw = self.bundles.get("val_raw_unscaled")
        te_raw = self.bundles.get("test_raw_unscaled")
        if tr_raw is not None and tr_raw.n > 0:
            from ml.imbalance import balance_dataset
            X_tr, y_tr, imb = balance_dataset(
                tr_raw.X, tr_raw.y, strategy=self.imbalance_strategy,
                rng=np.random.default_rng(self.random_state),
            )
            self.report["imbalance_for_skpipe"] = imb
        else:
            X_tr, y_tr = tr.X, tr.y

        X_va = va_raw.X if va_raw and va_raw.n else (va.X if va and va.n else None)
        y_va = va_raw.y if va_raw and va_raw.n else (va.y if va and va.n else None)
        X_te = te_raw.X if te_raw and te_raw.n else (te.X if te and te.n else None)
        y_te = te_raw.y if te_raw and te_raw.n else (te.y if te and te.n else None)

        if skip_hyper:
            from ml.pipeline_optimize import make_full_pipeline, save_pipeline_versioned
            from ml.sklearn_pipeline import evaluate_pipeline
            pipe = make_full_pipeline("extra_trees", scaler="standard")
            pipe.fit(X_tr, y_tr)
            result = {"status": "completed", "search": {"skipped": True}}
            if X_val is not None and y_val is not None and len(y_val):
                result.setdefault("metrics", {})["val"] = evaluate_pipeline(pipe, X_va, y_va, "val")
            if X_te is not None and y_te is not None and len(y_te):
                result.setdefault("metrics", {})["test"] = evaluate_pipeline(pipe, X_te, y_te, "test")
            result["saved"] = save_pipeline_versioned(pipe, meta=result, tag="extra_trees_default")
        else:
            result = run_optimized_training(
                X_tr, y_tr,
                X_val=X_va, y_val=y_va,
                X_test=X_te, y_test=y_te,
            )
        self.report["ml"] = result
        PREPROCESS_LOG.write_text(
            json.dumps(self.report, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
        )
        return result

    def _log(self, step: str, data: Dict[str, Any]) -> None:
        self.report["steps"].append({"step": step, "at": datetime.utcnow().isoformat(), **data})


def run_full_pipeline(skip_hyper: bool = False) -> Dict[str, Any]:
    """Point d'entrée unique : prétraitement ordonné + modèle."""
    pipe = PreprocessPipeline()
    pipe.run()
    return pipe.train_model(skip_hyper=skip_hyper)
