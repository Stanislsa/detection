"""
Scoring Functions for Fall Severity

Reference: docs/scientific_engine/09_SeverityModel.md
M. E. Tinetti et al. (1995) - DOI: 10.1056/NEJM199401273300401
"""

from typing import Tuple


def severity_score(angle: float, speed: float, acceleration: float,
                 floor_time: float, immobility: float, energy: float,
                 weights: Tuple[float, float, float, float, float, float] = None) -> float:
    """
    Calculate fall severity score using weighted fusion.
    
    Formula: S = w1*I_angle + w2*I_speed + w3*I_acceleration + w4*I_floor_time + w5*I_immobility + w6*I_energy
    
    Reference: A. Bourke et al. (2010) - DOI: 10.1016/j.gaitpost.2009.10.004
    
    Args:
        angle: Trunk angle indicator [0, 1]
        speed: Vertical speed indicator [0, 1]
        acceleration: Acceleration indicator [0, 1]
        floor_time: Time on floor indicator [0, 1]
        immobility: Immobility indicator [0, 1]
        energy: Kinetic energy indicator [0, 1]
        weights: Optional tuple of (w1, w2, w3, w4, w5, w6)
    
    Returns:
        Severity score [0, 1]
    """
    if weights is None:
        weights = (0.20, 0.25, 0.20, 0.15, 0.10, 0.10)
    
    w1, w2, w3, w4, w5, w6 = weights
    
    score = (w1 * angle + w2 * speed + w3 * acceleration + 
             w4 * floor_time + w5 * immobility + w6 * energy)
    
    return max(0.0, min(1.0, score))


def angle_indicator(trunk_angle: float, max_angle: float = 90.0) -> float:
    """
    Calculate angle indicator for severity scoring.
    
    Formula: I_angle = theta / theta_max
    
    Reference: Leiyue Yao et al. (2017) - DOI: 10.1109/ACCESS.2017.2655042
    
    Args:
        trunk_angle: Trunk angle in degrees
        max_angle: Maximum angle for normalization (default 90)
    
    Returns:
        Angle indicator [0, 1]
    """
    return max(0.0, min(1.0, trunk_angle / max_angle))


def speed_indicator(vertical_speed: float, max_speed: float = 5.0) -> float:
    """
    Calculate speed indicator for severity scoring.
    
    Formula: I_speed = |v| / v_max
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        vertical_speed: Vertical speed in m/s (negative for downward)
        max_speed: Maximum speed for normalization (default 5.0)
    
    Returns:
        Speed indicator [0, 1]
    """
    return max(0.0, min(1.0, abs(vertical_speed) / max_speed))


def acceleration_indicator(acceleration: float, max_acceleration: float = 15.0) -> float:
    """
    Calculate acceleration indicator for severity scoring.
    
    Formula: I_acceleration = |a| / a_max
    
    Reference: N. Noury et al. (2000) - DOI: 10.1109/58.897022
    
    Args:
        acceleration: Acceleration in m/s²
        max_acceleration: Maximum acceleration for normalization (default 15.0)
    
    Returns:
        Acceleration indicator [0, 1]
    """
    return max(0.0, min(1.0, abs(acceleration) / max_acceleration))


def floor_time_indicator(floor_time: float, max_time: float = 300.0) -> float:
    """
    Calculate floor time indicator for severity scoring.
    
    Formula: I_floor_time = t / t_max
    
    Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
    
    Args:
        floor_time: Time on floor in seconds
        max_time: Maximum time for normalization (default 300)
    
    Returns:
        Floor time indicator [0, 1]
    """
    return max(0.0, min(1.0, floor_time / max_time))


def immobility_indicator(immobility_time: float, max_time: float = 300.0) -> float:
    """
    Calculate immobility indicator for severity scoring.
    
    Formula: I_immobility = t / t_max
    
    Reference: S. R. Lord et al. (2001) - DOI: 10.1093/ageing/30.1.21
    
    Args:
        immobility_time: Immobility time in seconds
        max_time: Maximum time for normalization (default 300)
    
    Returns:
        Immobility indicator [0, 1]
    """
    return max(0.0, min(1.0, immobility_time / max_time))


def energy_indicator(mass: float, velocity: float, max_energy: float = 500.0) -> float:
    """
    Calculate kinetic energy indicator for severity scoring.
    
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


def age_risk_factor(age: float) -> float:
    """
    Calculate age risk factor for severity adjustment.
    
    Formula: F_age = 1 + 0.01 * max(0, age - 65)
    
    Reference: S. R. Lord et al. (2001) - DOI: 10.1093/ageing/30.1.21
    
    Args:
        age: Age in years
    
    Returns:
        Age risk factor (>= 1.0)
    """
    return 1.0 + 0.01 * max(0.0, age - 65)


def mobility_risk_factor(mobility_level: str) -> float:
    """
    Calculate mobility risk factor for severity adjustment.
    
    Reference: M. J. O'Brien, D. N. Bohannon (2007) - DOI: 10.1007/s00147-007-0214-4
    
    Args:
        mobility_level: One of 'AUTONOME', 'CANNE', 'DEAMBULATEUR', 'FAUTEUIL'
    
    Returns:
        Mobility risk factor
    """
    factors = {
        'AUTONOME': 1.0,
        'CANNE': 1.1,
        'DEAMBULATEUR': 1.2,
        'FAUTEUIL': 1.3
    }
    return factors.get(mobility_level.upper(), 1.0)


def history_risk_factor(falls_per_year: int) -> float:
    """
    Calculate fall history risk factor for severity adjustment.
    
    Formula: F_history = 1 + 0.1 * falls_per_year
    
    Reference: R. G. Cumming et al. (2003) - DOI: 10.1001/archinte.163.16.1936
    
    Args:
        falls_per_year: Number of falls in the past year
    
    Returns:
        History risk factor (>= 1.0)
    """
    return 1.0 + 0.1 * falls_per_year


def adjusted_severity_score(base_score: float, age: float = 65,
                           mobility_level: str = 'AUTONOME',
                           falls_per_year: int = 0) -> float:
    """
    Calculate adjusted severity score considering patient risk factors.
    
    Formula: S_adjusted = S_base * F_age * F_mobility * F_history
    
    Reference: S. R. Lord et al. (2001) - DOI: 10.1093/ageing/30.1.21
    
    Args:
        base_score: Base severity score [0, 1]
        age: Age in years (default 65)
        mobility_level: Mobility level (default 'AUTONOME')
        falls_per_year: Falls per year (default 0)
    
    Returns:
        Adjusted severity score [0, 1]
    """
    f_age = age_risk_factor(age)
    f_mobility = mobility_risk_factor(mobility_level)
    f_history = history_risk_factor(falls_per_year)
    
    adjusted = base_score * f_age * f_mobility * f_history
    return max(0.0, min(1.0, adjusted))


def severity_class(score: float) -> str:
    """
    Classify severity score into severity class.
    
    Reference: M. E. Tinetti et al. (1994) - DOI: 10.1056/NEJM199401273300401
    
    Args:
        score: Severity score [0, 1]
    
    Returns:
        Severity class: 'LEGÈRE', 'MODÉRÉE', 'SÉVÈRE', 'CRITIQUE'
    """
    if score < 0.3:
        return 'LEGÈRE'
    elif score < 0.6:
        return 'MODÉRÉE'
    elif score < 0.8:
        return 'SÉVÈRE'
    else:
        return 'CRITIQUE'


def dynamic_severity_update(base_score: float, time_elapsed: float,
                           max_time: float = 300.0, alpha: float = 0.3) -> float:
    """
    Update severity score based on time elapsed since fall.
    
    Formula: S(t) = S(t0) + alpha * (t / t_max)
    
    Reference: J. Fleming et al. (2008) - DOI: 10.1191/0269215508pm920oa
    
    Args:
        base_score: Initial severity score [0, 1]
        time_elapsed: Time elapsed since fall in seconds
        max_time: Maximum time for full increase (default 300)
        alpha: Maximum increase factor (default 0.3)
    
    Returns:
        Updated severity score [0, 1]
    """
    increase = alpha * (time_elapsed / max_time)
    updated = base_score + increase
    return max(0.0, min(1.0, updated))
