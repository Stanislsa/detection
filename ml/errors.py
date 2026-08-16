"""Exceptions et gestion d'erreurs du pipeline d'apprentissage."""
from __future__ import annotations
from typing import Any, Dict

class LearningError(Exception):
    def __init__(self, message: str, *, code: str = "LEARNING_ERROR", details: Any = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details
    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"error": {"code": self.code, "message": self.message}}
        if self.details is not None:
            d["error"]["details"] = self.details
        return d

class InsufficientDataError(LearningError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, code="INSUFFICIENT_DATA", details=details)

class FeatureExtractionError(LearningError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, code="FEATURE_EXTRACTION", details=details)

class TrainingError(LearningError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, code="TRAINING_FAILED", details=details)

class ModelNotFoundError(LearningError):
    def __init__(self, message: str = "Modèle non trouvé — lancez python start_train.py"):
        super().__init__(message, code="MODEL_NOT_FOUND")

class LowQualityModelError(LearningError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, code="LOW_QUALITY_MODEL", details=details)

class PredictionError(LearningError):
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, code="PREDICTION_FAILED", details=details)

def safe_call(fn, *args, default=None, label: str = "op", **kwargs):
    try:
        return fn(*args, **kwargs), None
    except LearningError as e:
        print(f"[error] {label}: [{e.code}] {e.message}")
        return default, e.to_dict()
    except Exception as e:
        print(f"[error] {label}: {type(e).__name__}: {e}")
        return default, {"error": {"code": "UNEXPECTED", "message": str(e), "type": type(e).__name__}}
