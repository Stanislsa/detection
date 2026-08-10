"""
Severity Engine

Reference: docs/scientific_engine/09_SeverityModel.md
M. E. Tinetti et al. - A multifactorial intervention to reduce the risk of falling (1994)
"""

from typing import Tuple, Optional


class SeverityEngine:
    """
    Evaluates fall severity using multi-criteria analysis.
    
    Reference: M. E. Tinetti et al. (1994) - DOI: 10.1056/NEJM199401273300401
    """
    
    def __init__(self, weights: Tuple[float, float, float, float, float, float] = None):
        """
        Initialize the severity engine.
        
        Args:
            weights: Weights for (angle, speed, acceleration, floor_time, immobility, energy)
        """
        if weights is None:
            weights = (0.20, 0.25, 0.20, 0.15, 0.10, 0.10)
        
        self.weights = weights
    
    def calculate_severity(self, trunk_angle: float, vertical_speed: float,
                          acceleration: float, floor_time: float,
                          immobility_time: float, mass: float = 70.0) -> dict:
        """
        Calculate fall severity score.
        
        Reference: A. Bourke et al. (2010) - DOI: 10.1016/j.gaitpost.2009.10.004
        
        Args:
            trunk_angle: Trunk angle in degrees
            vertical_speed: Vertical speed in m/s
            acceleration: Acceleration in m/s²
            floor_time: Time on floor in seconds
            immobility_time: Immobility time in seconds
            mass: Mass in kg (default 70)
        
        Returns:
            Dictionary with severity results
        """
        # Calculate indicators
        i_angle = self._angle_indicator(trunk_angle)
        i_speed = self._speed_indicator(vertical_speed)
        i_acceleration = self._acceleration_indicator(acceleration)
        i_floor_time = self._floor_time_indicator(floor_time)
        i_immobility = self._immobility_indicator(immobility_time)
        i_energy = self._energy_indicator(vertical_speed, mass)
        
        # Calculate severity score
        severity_score = self._calculate_severity_score(
            i_angle, i_speed, i_acceleration,
            i_floor_time, i_immobility, i_energy
        )
        
        # Determine severity class
        severity_class = self._classify_severity(severity_score)
        
        return {
            'severity_score': severity_score,
            'severity_class': severity_class,
            'indicators': {
                'angle': i_angle,
                'speed': i_speed,
                'acceleration': i_acceleration,
                'floor_time': i_floor_time,
                'immobility': i_immobility,
                'energy': i_energy
            }
        }
    
    def _angle_indicator(self, trunk_angle: float) -> float:
        """
        Calculate angle indicator for severity scoring.
        
        Formula: I_angle = theta / 90
        
        Reference: Leiyue Yao et al. (2017) - DOI: 10.1109/ACCESS.2017.2655042
        
        Args:
            trunk_angle: Trunk angle in degrees
        
        Returns:
            Angle indicator [0, 1]
        """
        return min(1.0, trunk_angle / 90.0)
    
    def _speed_indicator(self, vertical_speed: float) -> float:
        """
        Calculate speed indicator for severity scoring.
        
        Formula: I_speed = |v| / 5.0
        
        Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
        
        Args:
            vertical_speed: Vertical speed in m/s
        
        Returns:
            Speed indicator [0, 1]
        """
        return min(1.0, abs(vertical_speed) / 5.0)
    
    def _acceleration_indicator(self, acceleration: float) -> float:
        """
        Calculate acceleration indicator for severity scoring.
        
        Formula: I_acceleration = |a| / 15.0
        
        Reference: N. Noury et al. (2000) - DOI: 10.1109/58.897022
        
        Args:
            acceleration: Acceleration in m/s²
        
        Returns:
            Acceleration indicator [0, 1]
        """
        return min(1.0, abs(acceleration) / 15.0)
    
    def _floor_time_indicator(self, floor_time: float) -> float:
        """
        Calculate floor time indicator for severity scoring.
        
        Formula: I_floor_time = t / 300
        
        Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
        
        Args:
            floor_time: Time on floor in seconds
        
        Returns:
            Floor time indicator [0, 1]
        """
        return min(1.0, floor_time / 300.0)
    
    def _immobility_indicator(self, immobility_time: float) -> float:
        """
        Calculate immobility indicator for severity scoring.
        
        Formula: I_immobility = t / 300
        
        Reference: S. R. Lord et al. (2001) - DOI: 10.1093/ageing/30.1.21
        
        Args:
            immobility_time: Immobility time in seconds
        
        Returns:
            Immobility indicator [0, 1]
        """
        return min(1.0, immobility_time / 300.0)
    
    def _energy_indicator(self, velocity: float, mass: float) -> float:
        """
        Calculate energy indicator for severity scoring.
        
        Formula: I_energy = (0.5 * m * v^2) / 500
        
        Reference: G. T. A. Kovac et al. (2001) - DOI: 10.1109/58.945987
        
        Args:
            velocity: Velocity in m/s
            mass: Mass in kg
        
        Returns:
            Energy indicator [0, 1]
        """
        energy = 0.5 * mass * velocity**2
        return min(1.0, energy / 500.0)
    
    def _calculate_severity_score(self, angle: float, speed: float, acceleration: float,
                                floor_time: float, immobility: float, energy: float) -> float:
        """
        Calculate severity score using weighted fusion.
        
        Formula: S = w1*I1 + w2*I2 + w3*I3 + w4*I4 + w5*I5 + w6*I6
        
        Reference: A. Bourke et al. (2010) - DOI: 10.1016/j.gaitpost.2009.10.004
        
        Args:
            angle, speed, acceleration, floor_time, immobility, energy: Indicators [0, 1]
        
        Returns:
            Severity score [0, 1]
        """
        w1, w2, w3, w4, w5, w6 = self.weights
        
        score = (w1 * angle + w2 * speed + w3 * acceleration +
                w4 * floor_time + w5 * immobility + w6 * energy)
        
        return max(0.0, min(1.0, score))
    
    def _classify_severity(self, score: float) -> str:
        """
        Classify severity based on score.
        
        Reference: M. E. Tinetti et al. (1994) - DOI: 10.1056/NEJM199401273300401
        
        Args:
            score: Severity score [0, 1]
        
        Returns:
            Severity class
        """
        if score < 0.3:
            return 'LEGÈRE'
        elif score < 0.6:
            return 'MODÉRÉE'
        elif score < 0.8:
            return 'SÉVÈRE'
        else:
            return 'CRITIQUE'
    
    def adjust_for_risk_factors(self, base_score: float, age: float = 65,
                               mobility_level: str = 'AUTONOME',
                               falls_per_year: int = 0) -> float:
        """
        Adjust severity score for patient risk factors.
        
        Formula: S_adjusted = S_base * F_age * F_mobility * F_history
        
        Reference: S. R. Lord et al. (2001) - DOI: 10.1093/ageing/30.1.21
        
        Args:
            base_score: Base severity score [0, 1]
            age: Age in years
            mobility_level: Mobility level
            falls_per_year: Falls per year
        
        Returns:
            Adjusted severity score [0, 1]
        """
        f_age = 1.0 + 0.01 * max(0.0, age - 65)
        
        mobility_factors = {
            'AUTONOME': 1.0,
            'CANNE': 1.1,
            'DEAMBULATEUR': 1.2,
            'FAUTEUIL': 1.3
        }
        f_mobility = mobility_factors.get(mobility_level.upper(), 1.0)
        
        f_history = 1.0 + 0.1 * falls_per_year
        
        adjusted = base_score * f_age * f_mobility * f_history
        return max(0.0, min(1.0, adjusted))
    
    def dynamic_update(self, base_score: float, time_elapsed: float,
                      max_time: float = 300.0, alpha: float = 0.3) -> float:
        """
        Update severity score based on time elapsed.
        
        Formula: S(t) = S(t0) + alpha * (t / t_max)
        
        Reference: J. Fleming et al. (2008) - DOI: 10.1191/0269215508pm920oa
        
        Args:
            base_score: Initial severity score [0, 1]
            time_elapsed: Time elapsed since fall in seconds
            max_time: Maximum time for full increase
            alpha: Maximum increase factor
        
        Returns:
            Updated severity score [0, 1]
        """
        increase = alpha * (time_elapsed / max_time)
        updated = base_score + increase
        return max(0.0, min(1.0, updated))
