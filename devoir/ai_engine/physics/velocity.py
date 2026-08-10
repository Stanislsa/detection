"""
Velocity Calculations

Reference: docs/scientific_engine/04_Kinematics.md
Isaac Newton - Philosophiæ Naturalis Principia Mathematica (1687)
"""

from typing import Tuple, List
import numpy as np


class VelocityCalculator:
    """
    Calculates velocity from position data.
    
    Reference: Isaac Newton (1687)
    """
    
    def __init__(self, dt: float = 0.04):
        """
        Initialize the velocity calculator.
        
        Args:
            dt: Time step in seconds (default 0.04 for 25 fps)
        """
        self.dt = dt
    
    def calculate_velocity_3d(self, p1: Tuple[float, float, float],
                              p2: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Calculate 3D velocity between two positions.
        
        Formula: v = (p2 - p1) / dt
        
        Reference: Isaac Newton (1687)
        
        Args:
            p1: Initial position (x, y, z)
            p2: Final position (x, y, z)
        
        Returns:
            Velocity vector (vx, vy, vz) in m/s
        """
        vx = (p2[0] - p1[0]) / self.dt
        vy = (p2[1] - p1[1]) / self.dt
        vz = (p2[2] - p2[2]) / self.dt
        return (vx, vy, vz)
    
    def calculate_vertical_velocity(self, y1: float, y2: float) -> float:
        """
        Calculate vertical velocity.
        
        Formula: vy = (y2 - y1) / dt
        
        Reference: Galileo Galilei (1638)
        
        Args:
            y1: Initial vertical position
            y2: Final vertical position
        
        Returns:
            Vertical velocity in m/s
        """
        return (y2 - y1) / self.dt
    
    def calculate_horizontal_velocity(self, x1: float, z1: float,
                                     x2: float, z2: float) -> float:
        """
        Calculate horizontal velocity magnitude.
        
        Formula: vh = sqrt((vx)^2 + (vz)^2)
        
        Reference: Galileo Galilei (1638)
        
        Args:
            x1, z1: Initial horizontal positions
            x2, z2: Final horizontal positions
        
        Returns:
            Horizontal velocity in m/s
        """
        vx = (x2 - x1) / self.dt
        vz = (z2 - z1) / self.dt
        return np.sqrt(vx**2 + vz**2)
    
    def calculate_resultant_velocity(self, vx: float, vy: float, vz: float) -> float:
        """
        Calculate resultant velocity magnitude.
        
        Formula: v = sqrt(vx^2 + vy^2 + vz^2)
        
        Reference: Isaac Newton (1687)
        
        Args:
            vx, vy, vz: Velocity components
        
        Returns:
            Resultant velocity in m/s
        """
        return np.sqrt(vx**2 + vy**2 + vz**2)
    
    def calculate_velocity_history(self, positions: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """
        Calculate velocity history from position history.
        
        Args:
            positions: List of positions over time
        
        Returns:
            List of velocity vectors
        """
        velocities = []
        for i in range(1, len(positions)):
            v = self.calculate_velocity_3d(positions[i-1], positions[i])
            velocities.append(v)
        return velocities
    
    def detect_high_velocity(self, velocity: float, threshold: float = 2.0) -> bool:
        """
        Detect if velocity exceeds threshold.
        
        Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
        
        Args:
            velocity: Velocity magnitude
            threshold: Velocity threshold in m/s
        
        Returns:
            True if velocity exceeds threshold
        """
        return abs(velocity) > threshold


def compute_center_of_gravity_velocity(cg_positions: List[Tuple[float, float, float]],
                                      times: List[float]) -> Tuple[float, float, float]:
    """
    Calculate center of gravity velocity.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        cg_positions: List of center of gravity positions
        times: List of corresponding times
    
    Returns:
        Velocity vector (vx, vy, vz) in m/s
    """
    if len(cg_positions) < 2 or len(times) < 2:
        return (0.0, 0.0, 0.0)
    
    p1 = cg_positions[0]
    p2 = cg_positions[-1]
    t1 = times[0]
    t2 = times[-1]
    
    dt = t2 - t1
    if dt == 0:
        return (0.0, 0.0, 0.0)
    
    vx = (p2[0] - p1[0]) / dt
    vy = (p2[1] - p1[1]) / dt
    vz = (p2[2] - p1[2]) / dt
    
    return (vx, vy, vz)
