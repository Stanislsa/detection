"""
Acceleration Calculations

Reference: docs/scientific_engine/04_Kinematics.md
Isaac Newton - Philosophiæ Naturalis Principia Mathematica (1687)
"""

from typing import Tuple, List
import numpy as np


class AccelerationCalculator:
    """
    Calculates acceleration from velocity data.
    
    Reference: Isaac Newton (1687)
    """
    
    def __init__(self, dt: float = 0.04):
        """
        Initialize the acceleration calculator.
        
        Args:
            dt: Time step in seconds (default 0.04 for 25 fps)
        """
        self.dt = dt
    
    def calculate_acceleration_3d(self, v1: Tuple[float, float, float],
                                  v2: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Calculate 3D acceleration between two velocities.
        
        Formula: a = (v2 - v1) / dt
        
        Reference: Isaac Newton (1687)
        
        Args:
            v1: Initial velocity (vx, vy, vz)
            v2: Final velocity (vx, vy, vz)
        
        Returns:
            Acceleration vector (ax, ay, az) in m/s²
        """
        ax = (v2[0] - v1[0]) / self.dt
        ay = (v2[1] - v1[1]) / self.dt
        az = (v2[2] - v1[2]) / self.dt
        return (ax, ay, az)
    
    def calculate_vertical_acceleration(self, vy1: float, vy2: float) -> float:
        """
        Calculate vertical acceleration.
        
        Formula: ay = (vy2 - vy1) / dt
        
        Reference: Galileo Galilei (1638)
        
        Args:
            vy1: Initial vertical velocity
            vy2: Final vertical velocity
        
        Returns:
            Vertical acceleration in m/s²
        """
        return (vy2 - vy1) / self.dt
    
    def calculate_resultant_acceleration(self, ax: float, ay: float, az: float) -> float:
        """
        Calculate resultant acceleration magnitude.
        
        Formula: a = sqrt(ax^2 + ay^2 + az^2)
        
        Reference: Isaac Newton (1687)
        
        Args:
            ax, ay, az: Acceleration components
        
        Returns:
            Resultant acceleration in m/s²
        """
        return np.sqrt(ax**2 + ay**2 + az**2)
    
    def calculate_acceleration_history(self, velocities: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """
        Calculate acceleration history from velocity history.
        
        Args:
            velocities: List of velocities over time
        
        Returns:
            List of acceleration vectors
        """
        accelerations = []
        for i in range(1, len(velocities)):
            a = self.calculate_acceleration_3d(velocities[i-1], velocities[i])
            accelerations.append(a)
        return accelerations
    
    def detect_high_acceleration(self, acceleration: float, threshold: float = 5.0) -> bool:
        """
        Detect if acceleration exceeds threshold.
        
        Reference: N. Noury et al. (2000) - DOI: 10.1109/58.897022
        
        Args:
            acceleration: Acceleration magnitude
            threshold: Acceleration threshold in m/s²
        
        Returns:
            True if acceleration exceeds threshold
        """
        return abs(acceleration) > threshold


def compute_center_of_gravity_acceleration(cg_velocities: List[Tuple[float, float, float]],
                                           times: List[float]) -> Tuple[float, float, float]:
    """
    Calculate center of gravity acceleration.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        cg_velocities: List of center of gravity velocities
        times: List of corresponding times
    
    Returns:
        Acceleration vector (ax, ay, az) in m/s²
    """
    if len(cg_velocities) < 2 or len(times) < 2:
        return (0.0, 0.0, 0.0)
    
    v1 = cg_velocities[0]
    v2 = cg_velocities[-1]
    t1 = times[0]
    t2 = times[-1]
    
    dt = t2 - t1
    if dt == 0:
        return (0.0, 0.0, 0.0)
    
    ax = (v2[0] - v1[0]) / dt
    ay = (v2[1] - v1[1]) / dt
    az = (v2[2] - v1[2]) / dt
    
    return (ax, ay, az)
