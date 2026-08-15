"""
AI/ML module - Unified detection engines with scientific analysis.
"""

from .base import BaseDetector, BaseClassifier
from .yolo import YOLODetector, YOLOPersonDetector
from .mediapipe import MediaPipePoseDetector, MediaPipeFallDetector
from .openvino import OpenVINODetector
from .classifier import ImageClassifier, SceneClassifier
from .scientific import ScientificEngine, BiomechanicsEngine, PhysicsEngine, DecisionEngine
from .manager import AIManager, ai_manager

__all__ = [
    # Base classes
    "BaseDetector",
    "BaseClassifier",
    # Detectors
    "YOLODetector",
    "YOLOPersonDetector",
    "MediaPipePoseDetector",
    "MediaPipeFallDetector",
    "OpenVINODetector",
    # Classifiers
    "ImageClassifier",
    "SceneClassifier",
    # Scientific engines
    "ScientificEngine",
    "BiomechanicsEngine",
    "PhysicsEngine",
    "DecisionEngine",
    # Manager
    "AIManager",
    "ai_manager"
]
