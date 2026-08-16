"""Chemins pipeline, features, modeles."""
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
MODELS_DIR = ROOT / "data" / "models"
TREE_MODEL = MODELS_DIR / "severity_trees.joblib"
TREE_EXPORT = MODELS_DIR / "trees_export"
TRAIN_LOG = MODELS_DIR / "last_train.json"
PIPELINE_LOG = MODELS_DIR / "pipeline_last_run.json"
CLIP_SECONDS = 3.0
MAX_FRAMES_PER_CLIP = 30
TARGET_SIZE = (224, 224)
THRESH_URGENT = 5.0
THRESH_CRITIQUE = 10.0
STILLNESS_THRESH = 3.0
CLASSES = ("normal", "urgent", "critique")
