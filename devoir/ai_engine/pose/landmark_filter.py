"""
Landmark Filter

Reference: docs/scientific_engine/07_FallDetectionLogic.md
Google Research - MediaPipe Pose (2020) - DOI: 10.1145/3383090
"""

from typing import List, Tuple, Optional
import numpy as np


class LandmarkFilter:
    """
    Filters and validates MediaPipe landmarks.
    
    Reference: Google Research - MediaPipe Pose (2020)
    DOI: 10.1145/3383090
    """
    
    def __init__(self, min_visibility: float = 0.5):
        """
        Initialize the landmark filter.
        
        Args:
            min_visibility: Minimum visibility threshold for valid landmarks
        """
        self.min_visibility = min_visibility
    
    def filter_by_visibility(self, landmarks: List[dict]) -> List[dict]:
        """
        Filter landmarks by visibility threshold.
        
        Args:
            landmarks: List of landmark dictionaries
        
        Returns:
            Filtered list of landmarks
        """
        return [lm for lm in landmarks if lm['visibility'] >= self.min_visibility]
    
    def filter_by_confidence(self, landmarks: List[dict], min_confidence: float = 0.5) -> List[dict]:
        """
        Filter landmarks by confidence threshold.
        
        Args:
            landmarks: List of landmark dictionaries
            min_confidence: Minimum confidence threshold
        
        Returns:
            Filtered list of landmarks
        """
        return [lm for lm in landmarks if lm['visibility'] >= min_confidence]
    
    def smooth_landmarks(self, landmarks_history: List[List[Tuple[float, float, float]]], 
                        alpha: float = 0.3) -> List[Tuple[float, float, float]]:
        """
        Apply exponential moving average smoothing to landmarks.
        
        Formula: smoothed = alpha * current + (1 - alpha) * previous
        
        Args:
            landmarks_history: History of landmark positions
            alpha: Smoothing factor (0-1)
        
        Returns:
            Smoothed landmark positions
        """
        if len(landmarks_history) == 0:
            return []
        
        if len(landmarks_history) == 1:
            return landmarks_history[0]
        
        smoothed = []
        n_landmarks = len(landmarks_history[0])
        
        for i in range(n_landmarks):
            # Apply exponential moving average
            smoothed_x = landmarks_history[-1][i][0] * alpha + landmarks_history[-2][i][0] * (1 - alpha)
            smoothed_y = landmarks_history[-1][i][1] * alpha + landmarks_history[-2][i][1] * (1 - alpha)
            smoothed_z = landmarks_history[-1][i][2] * alpha + landmarks_history[-2][i][2] * (1 - alpha)
            smoothed.append((smoothed_x, smoothed_y, smoothed_z))
        
        return smoothed
    
    def interpolate_missing_landmarks(self, landmarks: List[Optional[Tuple[float, float, float]]],
                                    previous_landmarks: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """
        Interpolate missing landmarks using previous frame data.
        
        Args:
            landmarks: Current frame landmarks (may contain None)
            previous_landmarks: Previous frame landmarks
        
        Returns:
            Interpolated landmarks
        """
        interpolated = []
        
        for i, landmark in enumerate(landmarks):
            if landmark is None and i < len(previous_landmarks):
                # Use previous landmark
                interpolated.append(previous_landmarks[i])
            elif landmark is not None:
                interpolated.append(landmark)
            else:
                # Use (0, 0, 0) as fallback
                interpolated.append((0.0, 0.0, 0.0))
        
        return interpolated
    
    def validate_landmarks(self, landmarks: List[Tuple[float, float, float]]) -> bool:
        """
        Validate that landmarks are within expected ranges.
        
        Args:
            landmarks: List of landmark coordinates
        
        Returns:
            True if landmarks are valid, False otherwise
        """
        for landmark in landmarks:
            x, y, z = landmark
            
            # Check if coordinates are within valid ranges [0, 1]
            if not (0 <= x <= 1 and 0 <= y <= 1):
                return False
            
            # Check for NaN or infinite values
            if not all(isinstance(v, (int, float)) for v in landmark):
                return False
            
            if any(np.isnan(v) or np.isinf(v) for v in landmark):
                return False
        
        return True
    
    def get_key_landmarks(self, landmarks: List[Tuple[float, float, float]]) -> dict:
        """
        Extract key landmarks for fall detection.
        
        Args:
            landmarks: List of 33 landmark coordinates
        
        Returns:
            Dictionary of key landmarks
        """
        return {
            'nose': landmarks[0],
            'left_shoulder': landmarks[11],
            'right_shoulder': landmarks[12],
            'left_elbow': landmarks[13],
            'right_elbow': landmarks[14],
            'left_wrist': landmarks[15],
            'right_wrist': landmarks[16],
            'left_hip': landmarks[23],
            'right_hip': landmarks[24],
            'left_knee': landmarks[25],
            'right_knee': landmarks[26],
            'left_ankle': landmarks[27],
            'right_ankle': landmarks[28]
        }
