"""
Distance Functions

Reference: docs/scientific_engine/01_Geometry.md
Euclid - Elements (~300 BC)
"""

import math
from typing import Tuple, List


def euclidean_distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate the Euclidean distance between two points in 2D.
    
    Formula: d = sqrt((x2-x1)^2 + (y2-y1)^2)
    
    Reference: Euclid - Elements (~300 BC)
    
    Args:
        x1, y1: Coordinates of the first point
        x2, y2: Coordinates of the second point
    
    Returns:
        Euclidean distance in meters
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def euclidean_distance_3d(x1: float, y1: float, z1: float, 
                         x2: float, y2: float, z2: float) -> float:
    """
    Calculate the Euclidean distance between two points in 3D.
    
    Formula: d = sqrt((x2-x1)^2 + (y2-y1)^2 + (z2-z1)^2)
    
    Reference: Euclid - Elements (~300 BC)
    
    Args:
        x1, y1, z1: Coordinates of the first point
        x2, y2, z2: Coordinates of the second point
    
    Returns:
        Euclidean distance in meters
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)


def centroid(points: List[Tuple[float, float, float]]) -> Tuple[float, float, float]:
    """
    Calculate the geometric center (centroid) of a set of points.
    
    Formula: C = (1/n) * sum(Pi)
    
    Reference: Archimedes - On the Equilibrium of Planes (~250 BC)
    
    Args:
        points: List of (x, y, z) coordinates
    
    Returns:
        Centroid coordinates (x, y, z)
    """
    n = len(points)
    if n == 0:
        return (0.0, 0.0, 0.0)
    
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    cz = sum(p[2] for p in points) / n
    
    return (cx, cy, cz)


def midpoint(p1: Tuple[float, float, float], 
            p2: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Calculate the midpoint between two points.
    
    Formula: M = ((x1+x2)/2, (y1+y2)/2, (z1+z2)/2)
    
    Reference: Euclid - Elements (~300 BC)
    
    Args:
        p1: First point (x, y, z)
        p2: Second point (x, y, z)
    
    Returns:
        Midpoint coordinates (x, y, z)
    """
    return ((p1[0] + p2[0]) / 2, 
            (p1[1] + p2[1]) / 2, 
            (p1[2] + p2[2]) / 2)


def point_to_plane_distance(point: Tuple[float, float, float],
                           plane_normal: Tuple[float, float, float],
                           plane_point: Tuple[float, float, float]) -> float:
    """
    Calculate the distance from a point to a plane.
    
    Formula: d = |(ax0 + by0 + cz0 + d)| / sqrt(a^2 + b^2 + c^2)
    
    Reference: Joseph-Louis Lagrange (1773)
    
    Args:
        point: Point coordinates (x, y, z)
        plane_normal: Plane normal vector (a, b, c)
        plane_point: A point on the plane (x, y, z)
    
    Returns:
        Distance from point to plane in meters
    """
    x0, y0, z0 = point
    a, b, c = plane_normal
    x1, y1, z1 = plane_point
    
    # Plane equation: a(x-x1) + b(y-y1) + c(z-z1) = 0
    # Distance formula
    numerator = abs(a * (x0 - x1) + b * (y0 - y1) + c * (z0 - z1))
    denominator = math.sqrt(a**2 + b**2 + c**2)
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def point_to_line_distance(point: Tuple[float, float, float],
                           line_p1: Tuple[float, float, float],
                           line_p2: Tuple[float, float, float]) -> float:
    """
    Calculate the distance from a point to a line in 3D.
    
    Formula: d = ||(P0-P1) x (P0-P2)|| / ||P2-P1||
    
    Reference: René Descartes (1637)
    
    Args:
        point: Point coordinates (x, y, z)
        line_p1: First point on the line
        line_p2: Second point on the line
    
    Returns:
        Distance from point to line in meters
    """
    from .vectors import cross_product, norm, subtract_vectors
    
    v1 = subtract_vectors(point, line_p1)
    v2 = subtract_vectors(point, line_p2)
    line_vec = subtract_vectors(line_p2, line_p1)
    
    cross = cross_product(v1, v2)
    cross_norm = norm(cross)
    line_norm = norm(line_vec)
    
    if line_norm == 0:
        return 0.0
    
    return cross_norm / line_norm


def triangle_area(a: Tuple[float, float, float],
                  b: Tuple[float, float, float],
                  c: Tuple[float, float, float]) -> float:
    """
    Calculate the area of a triangle formed by three points.
    
    Formula: A = 0.5 * ||(b-a) x (c-a)|
    
    Reference: Heron of Alexandria - Metrica (~60 AD)
    
    Args:
        a, b, c: Triangle vertices (x, y, z)
    
    Returns:
        Triangle area in square meters
    """
    from .vectors import cross_product, norm, subtract_vectors
    
    v1 = subtract_vectors(b, a)
    v2 = subtract_vectors(c, a)
    cross = cross_product(v1, v2)
    
    return 0.5 * norm(cross)


def tetrahedron_volume(a: Tuple[float, float, float],
                       b: Tuple[float, float, float],
                       c: Tuple[float, float, float],
                       d: Tuple[float, float, float]) -> float:
    """
    Calculate the volume of a tetrahedron formed by four points.
    
    Formula: V = (1/6) * |(a-b) . ((c-b) x (d-b))|
    
    Reference: Archimedes - On the Sphere and Cylinder (~250 BC)
    
    Args:
        a, b, c, d: Tetrahedron vertices (x, y, z)
    
    Returns:
        Tetrahedron volume in cubic meters
    """
    from .vectors import cross_product, dot_product, subtract_vectors
    
    v1 = subtract_vectors(a, b)
    v2 = subtract_vectors(c, b)
    v3 = subtract_vectors(d, b)
    
    cross = cross_product(v2, v3)
    scalar_triple = dot_product(v1, cross)
    
    return abs(scalar_triple) / 6.0


def pythagorean_theorem(a: float, b: float) -> float:
    """
    Calculate the hypotenuse using the Pythagorean theorem.
    
    Formula: c = sqrt(a^2 + b^2)
    
    Reference: Pythagoras of Samos (~570-495 BC)
    
    Args:
        a: Length of first cathetus
        b: Length of second cathetus
    
    Returns:
        Hypotenuse length
    """
    return math.sqrt(a**2 + b**2)
