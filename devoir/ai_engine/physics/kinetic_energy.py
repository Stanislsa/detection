"""
Kinetic Energy Calculations

Reference: docs/scientific_engine/05_Dynamics.md
Gottfried Leibniz / Isaac Newton (1686/1687)
"""

from typing import Tuple
import math


class KineticEnergyCalculator:
    """
    Calculates kinetic energy from mass and velocity.
    
    Reference: Gottfried Leibniz (1686) / Isaac Newton (1687)
    """
    
    def __init__(self, mass: float = 70.0):
        """
        Initialize the kinetic energy calculator.
        
        Args:
            mass: Mass in kg (default 70 kg for average human)
        """
        self.mass = mass
    
    def calculate_kinetic_energy(self, velocity: float) -> float:
        """
        Calculate kinetic energy from velocity magnitude.
        
        Formula: Ec = 0.5 * m * v^2
        
        Reference: Gottfried Leibniz (1686)
        
        Args:
            velocity: Velocity in m/s
        
        Returns:
            Kinetic energy in Joules (J)
        """
        return 0.5 * self.mass * velocity**2
    
    def calculate_kinetic_energy_3d(self, velocity: Tuple[float, float, float]) -> float:
        """
        Calculate kinetic energy from 3D velocity vector.
        
        Formula: Ec = 0.5 * m * ||v||^2
        
        Reference: Gottfried Leibniz (1686)
        
        Args:
            velocity: Velocity vector (vx, vy, vz) in m/s
        
        Returns:
            Kinetic energy in Joules (J)
        """
        v_magnitude = math.sqrt(velocity[0]**2 + velocity[1]**2 + velocity[2]**2)
        return 0.5 * self.mass * v_magnitude**2
    
    def calculate_impact_energy(self, impact_velocity: float) -> float:
        """
        Calculate impact energy.
        
        Formula: E = 0.5 * m * v^2
        
        Reference: Gottfried Leibniz (1686)
        
        Args:
            impact_velocity: Impact velocity in m/s
        
        Returns:
            Impact energy in Joules (J)
        """
        return self.calculate_kinetic_energy(impact_velocity)
    
    def detect_high_energy_impact(self, energy: float, threshold: float = 400.0) -> bool:
        """
        Detect if impact energy exceeds threshold.
        
        Reference: G. T. A. Kovac et al. (2001) - DOI: 10.1109/58.945987
        
        Args:
            energy: Impact energy in Joules
            threshold: Energy threshold in Joules (default 400 J)
        
        Returns:
            True if energy exceeds threshold
        """
        return energy > threshold


def calculate_energy_indicator(mass: float, velocity: float, max_energy: float = 500.0) -> float:
    """
    Calculate energy indicator for severity scoring.
    
    Formula: I_energy = (0.5 * m * v^2) / E_max
    
    Reference: G. T. A. Kovac et al. (2001) - DOI: 10.1109/58.945987
    
    Args:
        mass: Mass in kg
        velocity: Velocity in m/s
        max_energy: Maximum energy for normalization (default 500 J)
    
    Returns:
        Energy indicator [0, 1]
    """
    energy = 0.5 * mass * velocity**2
    return max(0.0, min(1.0, energy / max_energy))
