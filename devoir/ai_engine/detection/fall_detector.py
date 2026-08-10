"""
Fall Detector

Reference: docs/scientific_engine/07_FallDetectionLogic.md
Leiyue Yao et al. - A New Approach to Fall Detection Based on the Human Torso Motion Model (2017)
"""

from typing import Tuple, List, Optional
import time


class FallDetector:
    """
    Detects falls using multi-criteria analysis.
    
    Reference: Leiyue Yao et al. (2017) - DOI: 10.1109/ACCESS.2017.2655042
    """
    
    def __init__(self, threshold_angle: float = 45.0, threshold_speed: float = 2.0,
                 threshold_acceleration: float = 5.0):
        """
        Initialize the fall detector.
        
        Args:
            threshold_angle: Trunk angle threshold in degrees
            threshold_speed: Vertical speed threshold in m/s
            threshold_acceleration: Acceleration threshold in m/s²
        """
        self.threshold_angle = threshold_angle
        self.threshold_speed = threshold_speed
        self.threshold_acceleration = threshold_acceleration
        
        self.history = {
            'trunk_angles': [],
            'vertical_speeds': [],
            'accelerations': [],
            'times': []
        }
    
    def detect_fall(self, trunk_angle: float, vertical_speed: float,
                   acceleration: float, timestamp: float = None) -> dict:
        """
        Detect fall based on current indicators.
        
        Reference: Leiyue Yao et al. (2017) - DOI: 10.1109/ACCESS.2017.2655042
        
        Args:
            trunk_angle: Trunk angle in degrees
            vertical_speed: Vertical speed in m/s
            acceleration: Acceleration in m/s²
            timestamp: Current timestamp
        
        Returns:
            Dictionary with detection results
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Update history
        self.history['trunk_angles'].append(trunk_angle)
        self.history['vertical_speeds'].append(vertical_speed)
        self.history['accelerations'].append(acceleration)
        self.history['times'].append(timestamp)
        
        # Keep only last 100 samples
        max_history = 100
        for key in self.history:
            if len(self.history[key]) > max_history:
                self.history[key] = self.history[key][-max_history:]
        
        # Check individual criteria
        angle_detected = self._check_angle_criterion(trunk_angle)
        speed_detected = self._check_speed_criterion(vertical_speed)
        acceleration_detected = self._check_acceleration_criterion(acceleration)
        
        # Calculate fall score
        fall_score = self._calculate_fall_score(trunk_angle, vertical_speed, acceleration)
        
        # Determine fall status
        is_fall = fall_score >= 0.7
        
        return {
            'is_fall': is_fall,
            'fall_score': fall_score,
            'angle_detected': angle_detected,
            'speed_detected': speed_detected,
            'acceleration_detected': acceleration_detected,
            'timestamp': timestamp
        }
    
    def _check_angle_criterion(self, trunk_angle: float) -> bool:
        """
        Check if trunk angle exceeds threshold.
        
        Reference: Leiyue Yao et al. (2017) - DOI: 10.1109/ACCESS.2017.2655042
        
        Args:
            trunk_angle: Trunk angle in degrees
        
        Returns:
            True if angle criterion is met
        """
        return trunk_angle > self.threshold_angle
    
    def _check_speed_criterion(self, vertical_speed: float) -> bool:
        """
        Check if vertical speed exceeds threshold.
        
        Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
        
        Args:
            vertical_speed: Vertical speed in m/s
        
        Returns:
            True if speed criterion is met
        """
        return abs(vertical_speed) > self.threshold_speed
    
    def _check_acceleration_criterion(self, acceleration: float) -> bool:
        """
        Check if acceleration exceeds threshold.
        
        Reference: N. Noury et al. (2000) - DOI: 10.1109/58.897022
        
        Args:
            acceleration: Acceleration in m/s²
        
        Returns:
            True if acceleration criterion is met
        """
        return abs(acceleration) > self.threshold_acceleration
    
    def _calculate_fall_score(self, trunk_angle: float, vertical_speed: float,
                             acceleration: float) -> float:
        """
        Calculate fall score using weighted fusion.
        
        Formula: S = w1*I_angle + w2*I_speed + w3*I_acceleration
        
        Reference: A. Bourke et al. (2010) - DOI: 10.1016/j.gaitpost.2009.10.004
        
        Args:
            trunk_angle: Trunk angle in degrees
            vertical_speed: Vertical speed in m/s
            acceleration: Acceleration in m/s²
        
        Returns:
            Fall score [0, 1]
        """
        # Normalize indicators
        i_angle = min(1.0, trunk_angle / 90.0)
        i_speed = min(1.0, abs(vertical_speed) / 5.0)
        i_acceleration = min(1.0, abs(acceleration) / 15.0)
        
        # Weights
        w1, w2, w3 = 0.35, 0.40, 0.25
        
        score = w1 * i_angle + w2 * i_speed + w3 * i_acceleration
        return score
    
    def detect_rapid_fall(self, trunk_angle: float, vertical_speed: float) -> bool:
        """
        Detect rapid fall using special rule.
        
        Rule: If vertical_speed > 3.0 m/s AND trunk_angle > 60°, immediate fall detection.
        
        Reference: Leiyue Yao et al. (2017) - DOI: 10.1109/ACCESS.2017.2655042
        
        Args:
            trunk_angle: Trunk angle in degrees
            vertical_speed: Vertical speed in m/s
        
        Returns:
            True if rapid fall detected
        """
        return abs(vertical_speed) > 3.0 and trunk_angle > 60.0
    
    def reset_history(self):
        """Reset detection history."""
        self.history = {
            'trunk_angles': [],
            'vertical_speeds': [],
            'accelerations': [],
            'times': []
        }
