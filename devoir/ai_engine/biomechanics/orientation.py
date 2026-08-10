"""
Body Orientation Analysis

Reference: docs/scientific_engine/06_Biomechanics.md
Leonhard Euler - Nova methodus motum corporum rigidorum determinandi (1775)
"""

from typing import Tuple
import math


class OrientationAnalyzer:
    """
    Analyzes body orientation using Euler angles.
    
    Reference: Leonhard Euler (1775)
    """
    
    def __init__(self):
        """Initialize the orientation analyzer."""
        pass
    
    def calculate_postural_orientation(self, shoulder_left: Tuple[float, float, float],
                                       shoulder_right: Tuple[float, float, float],
                                       hip_left: Tuple[float, float, float],
                                       hip_right: Tuple[float, float, float],
                                       degrees: bool = True) -> Tuple[float, float, float]:
        """
        Calculate postural orientation using Euler angles (roll, pitch, yaw).
        
        Reference: Leonhard Euler (1775)
        
        Args:
            shoulder_left: Left shoulder position
            shoulder_right: Right shoulder position
            hip_left: Left hip position
            hip_right: Right hip position
            degrees: If True, return in degrees
        
        Returns:
            Euler angles (roll, pitch, yaw)
        """
        # Calculate shoulder center
        shoulder_center = (
            (shoulder_left[0] + shoulder_right[0]) / 2,
            (shoulder_left[1] + shoulder_right[1]) / 2,
            (shoulder_left[2] + shoulder_right[2]) / 2
        )
        
        # Calculate hip center
        hip_center = (
            (hip_left[0] + hip_right[0]) / 2,
            (hip_left[1] + hip_right[1]) / 2,
            (hip_left[2] + hip_right[2]) / 2
        )
        
        # Trunk vector (from hip to shoulder)
        trunk_vector = (
            shoulder_center[0] - hip_center[0],
            shoulder_center[1] - hip_center[1],
            shoulder_center[2] - hip_center[2]
        )
        
        # Normalize trunk vector
        trunk_norm = math.sqrt(trunk_vector[0]**2 + trunk_vector[1]**2 + trunk_vector[2]**2)
        if trunk_norm == 0:
            return (0.0, 0.0, 0.0)
        
        trunk_normalized = (
            trunk_vector[0] / trunk_norm,
            trunk_vector[1] / trunk_norm,
            trunk_vector[2] / trunk_norm
        )
        
        # Pitch: angle with vertical
        pitch = math.acos(max(-1.0, min(1.0, trunk_normalized[1])))
        
        # Roll: angle of shoulder line with horizontal
        shoulder_vector = (
            shoulder_right[0] - shoulder_left[0],
            shoulder_right[1] - shoulder_left[1],
            shoulder_right[2] - shoulder_left[2]
        )
        roll = math.atan2(shoulder_vector[1], shoulder_vector[0])
        
        # Yaw: angle in horizontal plane
        yaw = math.atan2(trunk_normalized[0], trunk_normalized[2])
        
        if degrees:
            pitch = math.degrees(pitch)
            roll = math.degrees(roll)
            yaw = math.degrees(yaw)
        
        return (roll, pitch, yaw)
    
    def detect_orientation_change(self, current_orientation: Tuple[float, float, float],
                                 previous_orientation: Tuple[float, float, float],
                                 threshold: float = 30.0) -> bool:
        """
        Detect significant change in body orientation.
        
        Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
        
        Args:
            current_orientation: Current (roll, pitch, yaw) in degrees
            previous_orientation: Previous (roll, pitch, yaw) in degrees
            threshold: Angle threshold in degrees
        
        Returns:
            True if orientation change exceeds threshold
        """
        delta_roll = abs(current_orientation[0] - previous_orientation[0])
        delta_pitch = abs(current_orientation[1] - previous_orientation[1])
        delta_yaw = abs(current_orientation[2] - previous_orientation[2])
        
        return delta_roll > threshold or delta_pitch > threshold or delta_yaw > threshold
    
    def calculate_angular_velocity(self, current_orientation: Tuple[float, float, float],
                                  previous_orientation: Tuple[float, float, float],
                                  dt: float) -> Tuple[float, float, float]:
        """
        Calculate angular velocity from orientation change.
        
        Formula: omega = (theta2 - theta1) / dt
        
        Reference: Leonhard Euler (1765)
        
        Args:
            current_orientation: Current (roll, pitch, yaw) in radians
            previous_orientation: Previous (roll, pitch, yaw) in radians
            dt: Time step in seconds
        
        Returns:
            Angular velocity (omega_roll, omega_pitch, omega_yaw) in rad/s
        """
        omega_roll = (current_orientation[0] - previous_orientation[0]) / dt
        omega_pitch = (current_orientation[1] - previous_orientation[1]) / dt
        omega_yaw = (current_orientation[2] - previous_orientation[2]) / dt
        
        return (omega_roll, omega_pitch, omega_yaw)
    
    def detect_rapid_rotation(self, angular_velocity: Tuple[float, float, float],
                            threshold: float = 2.0) -> bool:
        """
        Detect rapid body rotation.
        
        Reference: N. Noury et al. (2000) - DOI: 10.1109/58.897022
        
        Args:
            angular_velocity: Angular velocity (omega_roll, omega_pitch, omega_yaw) in rad/s
            threshold: Angular velocity threshold in rad/s
        
        Returns:
            True if angular velocity exceeds threshold
        """
        omega_magnitude = math.sqrt(
            angular_velocity[0]**2 +
            angular_velocity[1]**2 +
            angular_velocity[2]**2
        )
        return omega_magnitude > threshold
