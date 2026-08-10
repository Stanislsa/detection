"""
Angle Calculations

Reference: docs/scientific_engine/03_Trigonometry.md
Hipparchus of Nicaea (~190 BC)
"""

import math
from typing import Tuple


def sin(angle: float, degrees: bool = False) -> float:
    """
    Calculate the sine of an angle.
    
    Formula: sin(theta)
    
    Reference: Hipparchus of Nicaea (~190 BC)
    
    Args:
        angle: Angle value
        degrees: If True, angle is in degrees; if False, in radians
    
    Returns:
        Sine of the angle
    """
    if degrees:
        angle = math.radians(angle)
    return math.sin(angle)


def cos(angle: float, degrees: bool = False) -> float:
    """
    Calculate the cosine of an angle.
    
    Formula: cos(theta)
    
    Reference: Hipparchus of Nicaea (~190 BC)
    
    Args:
        angle: Angle value
        degrees: If True, angle is in degrees; if False, in radians
    
    Returns:
        Cosine of the angle
    """
    if degrees:
        angle = math.radians(angle)
    return math.cos(angle)


def tan(angle: float, degrees: bool = False) -> float:
    """
    Calculate the tangent of an angle.
    
    Formula: tan(theta) = sin(theta) / cos(theta)
    
    Reference: Hipparchus of Nicaea (~190 BC)
    
    Args:
        angle: Angle value
        degrees: If True, angle is in degrees; if False, in radians
    
    Returns:
        Tangent of the angle
    """
    if degrees:
        angle = math.radians(angle)
    return math.tan(angle)


def arcsin(value: float, degrees: bool = False) -> float:
    """
    Calculate the inverse sine (arcsin).
    
    Formula: theta = arcsin(x)
    
    Reference: Carl Friedrich Gauss (1799)
    
    Args:
        value: Value in [-1, 1]
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Angle whose sine is the given value
    """
    angle = math.asin(max(-1.0, min(1.0, value)))
    if degrees:
        angle = math.degrees(angle)
    return angle


def arccos(value: float, degrees: bool = False) -> float:
    """
    Calculate the inverse cosine (arccos).
    
    Formula: theta = arccos(x)
    
    Reference: Carl Friedrich Gauss (1799)
    
    Args:
        value: Value in [-1, 1]
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Angle whose cosine is the given value
    """
    angle = math.acos(max(-1.0, min(1.0, value)))
    if degrees:
        angle = math.degrees(angle)
    return angle


def arctan(value: float, degrees: bool = False) -> float:
    """
    Calculate the inverse tangent (arctan).
    
    Formula: theta = arctan(x)
    
    Reference: Carl Friedrich Gauss (1799)
    
    Args:
        value: Value
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Angle whose tangent is the given value
    """
    angle = math.atan(value)
    if degrees:
        angle = math.degrees(angle)
    return angle


def atan2(y: float, x: float, degrees: bool = False) -> float:
    """
    Calculate the two-argument arctangent.
    
    Formula: theta = atan2(y, x)
    
    Reference: IBM Fortran (1961)
    
    Args:
        y: Y coordinate
        x: X coordinate
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Angle in [-pi, pi] or [-180, 180]
    """
    angle = math.atan2(y, x)
    if degrees:
        angle = math.degrees(angle)
    return angle


def deg_to_rad(degrees: float) -> float:
    """
    Convert degrees to radians.
    
    Formula: rad = deg * pi / 180
    
    Reference: Roger Cotes (1714)
    
    Args:
        degrees: Angle in degrees
    
    Returns:
        Angle in radians
    """
    return math.radians(degrees)


def rad_to_deg(radians: float) -> float:
    """
    Convert radians to degrees.
    
    Formula: deg = rad * 180 / pi
    
    Reference: Roger Cotes (1714)
    
    Args:
        radians: Angle in radians
    
    Returns:
        Angle in degrees
    """
    return math.degrees(radians)


def inclination_angle(dx: float, dy: float, degrees: bool = True) -> float:
    """
    Calculate the inclination angle from horizontal and vertical components.
    
    Formula: theta = atan2(dx, dy)
    
    Reference: Euclid (~300 BC)
    
    Args:
        dx: Horizontal component
        dy: Vertical component
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Inclination angle
    """
    return atan2(dx, dy, degrees)


def angle_between_segments(p1: Tuple[float, float, float],
                          p2: Tuple[float, float, float],
                          p3: Tuple[float, float, float],
                          degrees: bool = True) -> float:
    """
    Calculate the angle between two segments (p1-p2 and p2-p3).
    
    Formula: theta = arccos((v1 . v2) / (||v1|| * ||v2||))
    
    Reference: Euclid (~300 BC)
    
    Args:
        p1: First point
        p2: Vertex point
        p3: Third point
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Angle between segments
    """
    from .vectors import subtract_vectors, norm, dot_product
    
    v1 = subtract_vectors(p1, p2)
    v2 = subtract_vectors(p3, p2)
    
    n1 = norm(v1)
    n2 = norm(v2)
    
    if n1 == 0 or n2 == 0:
        return 0.0
    
    dot = dot_product(v1, v2)
    cos_theta = dot / (n1 * n2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    
    angle = math.acos(cos_theta)
    
    if degrees:
        angle = math.degrees(angle)
    
    return angle


def dihedral_angle(normal1: Tuple[float, float, float],
                   normal2: Tuple[float, float, float],
                   degrees: bool = True) -> float:
    """
    Calculate the dihedral angle between two planes.
    
    Formula: theta = arccos((n1 . n2) / (||n1|| * ||n2||))
    
    Reference: Gaspard Monge (1795)
    
    Args:
        normal1: Normal vector of first plane
        normal2: Normal vector of second plane
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Dihedral angle
    """
    from .vectors import norm, dot_product
    
    n1 = norm(normal1)
    n2 = norm(normal2)
    
    if n1 == 0 or n2 == 0:
        return 0.0
    
    dot = dot_product(normal1, normal2)
    cos_theta = dot / (n1 * n2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    
    angle = math.acos(cos_theta)
    
    if degrees:
        angle = math.degrees(angle)
    
    return angle


def law_of_cosines(a: float, b: float, c: float) -> float:
    """
    Calculate an angle using the law of cosines.
    
    Formula: gamma = arccos((a^2 + b^2 - c^2) / (2ab))
    
    Reference: Al-Kashi (1427)
    
    Args:
        a: Length of side a
        b: Length of side b
        c: Length of side c (opposite to the angle)
    
    Returns:
        Angle opposite to side c in radians
    """
    if a == 0 or b == 0:
        return 0.0
    
    cos_gamma = (a**2 + b**2 - c**2) / (2 * a * b)
    cos_gamma = max(-1.0, min(1.0, cos_gamma))
    
    return math.acos(cos_gamma)


def law_of_sines(a: float, b: float, alpha: float) -> float:
    """
    Calculate an angle using the law of sines.
    
    Formula: beta = arcsin((b * sin(alpha)) / a)
    
    Reference: Nasir al-Din al-Tusi (13th century)
    
    Args:
        a: Length of side a
        b: Length of side b
        alpha: Angle opposite to side a (radians)
    
    Returns:
        Angle opposite to side b in radians
    """
    if a == 0:
        return 0.0
    
    sin_beta = (b * math.sin(alpha)) / a
    sin_beta = max(-1.0, min(1.0, sin_beta))
    
    return math.asin(sin_beta)
