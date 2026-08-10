"""
Core module - Cœur du système de détection.
"""
from .physics_engine import PhysicsEngine, PoseData, PhysicsState
from .fall_detector import FallDetector, FallStatus, FallDetectionResult
from .gravity_scorer import GravityScorer, GravityLevel, GravityResult
from .pose_processor import PoseEstimator
from .decision_tree import DecisionTree

__all__ = [
    'PhysicsEngine', 'PoseData', 'PhysicsState',
    'FallDetector', 'FallStatus', 'FallDetectionResult',
    'GravityScorer', 'GravityLevel', 'GravityResult',
    'PoseEstimator',
    'DecisionTree'
]
