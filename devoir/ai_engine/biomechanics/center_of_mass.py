"""
Center of Mass Calculations

Reference: docs/scientific_engine/06_Biomechanics.md
Claude Perrault - Cours de physique (1670)
"""

from typing import Tuple, List


class CenterOfMassCalculator:
    """
    Calculates center of mass (center of gravity) from body landmarks.
    
    Reference: Claude Perrault (1670)
    """
    
    def __init__(self):
        """Initialize the center of mass calculator."""
        # Anthropometric weights for body segments (Winter, 1990)
        self.weights = {
            'head': 0.08,
            'torso': 0.43,
            'arms': 0.10,
            'legs': 0.39
        }
    
    def calculate_center_of_gravity(self, points: List[Tuple[float, float, float]],
                                   weights: List[float] = None) -> Tuple[float, float, float]:
        """
        Calculate center of gravity from body landmarks.
        
        Formula: CG = (sum(wi * Pi)) / sum(wi)
        
        Reference: Claude Perrault (1670)
        
        Args:
            points: List of (x, y, z) coordinates for body landmarks
            weights: Optional weights for each point (default: equal weights)
        
        Returns:
            Center of gravity coordinates (x, y, z)
        """
        if weights is None:
            weights = [1.0] * len(points)
        
        if len(points) == 0:
            return (0.0, 0.0, 0.0)
        
        total_weight = sum(weights)
        if total_weight == 0:
            return (0.0, 0.0, 0.0)
        
        cx = sum(w * p[0] for w, p in zip(weights, points)) / total_weight
        cy = sum(w * p[1] for w, p in zip(weights, points)) / total_weight
        cz = sum(w * p[2] for w, p in zip(weights, points)) / total_weight
        
        return (cx, cy, cz)
    
    def calculate_weighted_center_of_gravity(self, landmarks: dict) -> Tuple[float, float, float]:
        """
        Calculate weighted center of gravity using anthropometric weights.
        
        Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
        
        Args:
            landmarks: Dictionary of key landmarks
        
        Returns:
            Weighted center of gravity coordinates (x, y, z)
        """
        points = []
        weights = []
        
        # Head (nose)
        if 'nose' in landmarks:
            points.append(landmarks['nose'])
            weights.append(self.weights['head'])
        
        # Torso (shoulders and hips)
        if 'left_shoulder' in landmarks and 'right_shoulder' in landmarks:
            shoulder_center = (
                (landmarks['left_shoulder'][0] + landmarks['right_shoulder'][0]) / 2,
                (landmarks['left_shoulder'][1] + landmarks['right_shoulder'][1]) / 2,
                (landmarks['left_shoulder'][2] + landmarks['right_shoulder'][2]) / 2
            )
            points.append(shoulder_center)
            weights.append(self.weights['torso'] * 0.5)
        
        if 'left_hip' in landmarks and 'right_hip' in landmarks:
            hip_center = (
                (landmarks['left_hip'][0] + landmarks['right_hip'][0]) / 2,
                (landmarks['left_hip'][1] + landmarks['right_hip'][1]) / 2,
                (landmarks['left_hip'][2] + landmarks['right_hip'][2]) / 2
            )
            points.append(hip_center)
            weights.append(self.weights['torso'] * 0.5)
        
        # Arms (wrists)
        if 'left_wrist' in landmarks:
            points.append(landmarks['left_wrist'])
            weights.append(self.weights['arms'] * 0.5)
        
        if 'right_wrist' in landmarks:
            points.append(landmarks['right_wrist'])
            weights.append(self.weights['arms'] * 0.5)
        
        # Legs (ankles)
        if 'left_ankle' in landmarks:
            points.append(landmarks['left_ankle'])
            weights.append(self.weights['legs'] * 0.5)
        
        if 'right_ankle' in landmarks:
            points.append(landmarks['right_ankle'])
            weights.append(self.weights['legs'] * 0.5)
        
        return self.calculate_center_of_gravity(points, weights)
    
    def calculate_center_of_gravity_height(self, cg: Tuple[float, float, float],
                                         total_height: float = None) -> float:
        """
        Calculate the height of the center of gravity.
        
        Reference: Claude Perrault (1670)
        
        Args:
            cg: Center of gravity coordinates (x, y, z)
            total_height: Total body height in meters (optional)
        
        Returns:
            Height of center of gravity in meters (or percentage if total_height provided)
        """
        height = cg[1]
        
        if total_height is not None and total_height > 0:
            return (height / total_height) * 100
        
        return height
    
    def detect_low_center_of_gravity(self, cg_height: float, threshold: float = 0.5) -> bool:
        """
        Detect if center of gravity is unusually low.
        
        Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
        
        Args:
            cg_height: Center of gravity height (normalized 0-1)
            threshold: Height threshold (default 0.5)
        
        Returns:
            True if center of gravity is below threshold
        """
        return cg_height < threshold
