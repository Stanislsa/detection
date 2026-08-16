"""Configuration apprentissage — hyperparams + chemins + garde-fous."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEO_DIR = ROOT / "données" / "vidéo"
VIDEO_DIR_ALT = ROOT / "donnees" / "video"
FRAGMENTS_DIR = ROOT / "data" / "fragments"
RAW_DIR = FRAGMENTS_DIR / "raw"
CLASS_DIRS = {
    "normal": FRAGMENTS_DIR / "normal",
    "urgent": FRAGMENTS_DIR / "urgent",
    "critique": FRAGMENTS_DIR / "critique",
}
METADATA_FILE = FRAGMENTS_DIR / "index.json"
FEATURES_DIR = ROOT / "data" / "features"
FEATURES_RAW = FEATURES_DIR / "raw"
FEATURES_PROCESSED = FEATURES_DIR / "processed"
FEATURES_BY_CLASS = FEATURES_DIR / "by_class"
FEATURES_TABLE = FEATURES_PROCESSED / "features_table.csv"
FEATURES_MATRIX = FEATURES_PROCESSED / "X.npy"
LABELS_VECTOR = FEATURES_PROCESSED / "y.npy"
FEATURES_META = FEATURES_PROCESSED / "features_meta.json"
SCALER_PATH = FEATURES_PROCESSED / "scaler.joblib"
MODELS_DIR = ROOT / "data" / "models"
TREE_MODEL = MODELS_DIR / "severity_trees.joblib"
BEST_MODEL = MODELS_DIR / "best_model.joblib"
TREE_EXPORT = MODELS_DIR / "trees_export"
TRAIN_LOG = MODELS_DIR / "last_train.json"
PIPELINE_LOG = MODELS_DIR / "pipeline_last_run.json"
METRICS_LOG = MODELS_DIR / "metrics.json"
F1_ANALYSIS_LOG = MODELS_DIR / "f1_error_analysis.json"
HYPERPARAM_LOG = MODELS_DIR / "hyperparam_search.json"
CLIP_SECONDS = 2.5
MAX_FRAMES_PER_CLIP = 24
TARGET_SIZE = (160, 160)
THRESH_URGENT = 5.0
THRESH_CRITIQUE = 12.0
STILLNESS_THRESH = 2.5
CLASSES = ("normal", "urgent", "critique")
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}
MIN_SAMPLES_TOTAL = 6
MIN_SAMPLES_PER_CLASS = 1
MIN_ACCEPTABLE_F1_MACRO = 0.35
MIN_GOOD_F1_MACRO = 0.70
CV_FOLDS = 3
RANDOM_STATE = 42
TEST_SIZE = 0.25
HYPERPARAM_N_ITER = 12
HYPERPARAM_CV = 3
N_ESTIMATORS_DEFAULT = 150
MAX_DEPTH_DEFAULT = 10
PARAM_GRIDS = {
    "decision_tree": {
        "max_depth": [3, 5, 8, 12, None],
        "min_samples_leaf": [1, 2, 4],
        "min_samples_split": [2, 5],
        "criterion": ["gini", "entropy"],
        "class_weight": ["balanced"],
    },
    "random_forest": {
        "n_estimators": [50, 100, 150, 200],
        "max_depth": [5, 8, 12, None],
        "min_samples_leaf": [1, 2, 4],
        "max_features": ["sqrt", "log2", None],
        "class_weight": ["balanced", "balanced_subsample"],
    },
    "extra_trees": {
        "n_estimators": [50, 100, 150, 200],
        "max_depth": [5, 8, 12, None],
        "min_samples_leaf": [1, 2, 4],
        "max_features": ["sqrt", "log2"],
        "class_weight": ["balanced"],
    },
    "gradient_boosting": {
        "n_estimators": [50, 80, 100],
        "max_depth": [2, 3, 5],
        "learning_rate": [0.05, 0.08, 0.1, 0.15],
        "subsample": [0.8, 1.0],
        "min_samples_leaf": [1, 2],
    },
}
