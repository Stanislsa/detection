"""
Vector Operations

Reference: docs/scientific_engine/02_LinearAlgebra.md
Hermann Grassmann - Die Lineale Ausdehnungslehre (1844)
"""

import math
from typing import Tuple


def add_vectors(v1: Tuple[float, float, float], 
                 v2: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Add two vectors.
    
    Formula: a + b = (ax+bx, ay+by, az+bz)
    
    Reference: Hermann Grassmann (1844)
    
    Args:
        v1: First vector (x, y, z)
        v2: Second vector (x, y, z)
    
    Returns:
        Sum vector (x, y, z)
    """
    return (v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2])


def subtract_vectors(v1: Tuple[float, float, float], 
                    v2: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Subtract two vectors.
    
    Formula: a - b = (ax-bx, ay-by, az-bz)
    
    Reference: Hermann Grassmann (1844)
    
    Args:
        v1: First vector (x, y, z)
        v2: Second vector (x, y, z)
    
    Returns:
        Difference vector (x, y, z)
    """
    return (v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])


def scalar_multiply(v: Tuple[float, float, float], k: float) -> Tuple[float, float, float]:
    """
    Multiply a vector by a scalar.
    
    Formula: k*a = (k*ax, k*ay, k*az)
    
    Reference: Hermann Grassmann (1844)
    
    Args:
        v: Vector (x, y, z)
        k: Scalar
    
    Returns:
        Scaled vector (x, y, z)
    """
    return (v[0] * k, v[1] * k, v[2] * k)


def scalar_divide(v: Tuple[float, float, float], k: float) -> Tuple[float, float, float]:
    """
    Divide a vector by a scalar.
    
    Formula: a/k = (ax/k, ay/k, az/k)
    
    Reference: Hermann Grassmann (1844)
    
    Args:
        v: Vector (x, y, z)
        k: Scalar (non-zero)
    
    Returns:
        Divided vector (x, y, z)
    """
    if k == 0:
        raise ValueError("Cannot divide by zero")
    return (v[0] / k, v[1] / k, v[2] / k)


def dot_product(v1: Tuple[float, float, float], 
                v2: Tuple[float, float, float]) -> float:
    """
    Calculate the dot product of two vectors.
    
    Formula: a . b = ax*bx + ay*by + az*bz
    
    Reference: Josiah Willard Gibbs, Oliver Heaviside (1880s)
    
    Args:
        v1: First vector (x, y, z)
        v2: Second vector (x, y, z)
    
    Returns:
        Dot product (scalar)
    """
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def cross_product(v1: Tuple[float, float, float], 
                 v2: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Calculate the cross product of two vectors.
    
    Formula: a x b = (ay*bz - az*by, az*bx - ax*bz, ax*by - ay*bx)
    
    Reference: Josiah Willard Gibbs, Oliver Heaviside (1880s)
    
    Args:
        v1: First vector (x, y, z)
        v2: Second vector (x, y, z)
    
    Returns:
        Cross product vector (x, y, z)
    """
    return (v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0])


def scalar_triple_product(v1: Tuple[float, float, float],
                         v2: Tuple[float, float, float],
                         v3: Tuple[float, float, float]) -> float:
    """
    Calculate the scalar triple product of three vectors.
    
    Formula: [a, b, c] = a . (b x c)
    
    Reference: William Rowan Hamilton (1843)
    
    Args:
        v1, v2, v3: Three vectors (x, y, z)
    
    Returns:
        Scalar triple product
    """
    return dot_product(v1, cross_product(v2, v3))


def norm(v: Tuple[float, float, float]) -> float:
    """
    Calculate the Euclidean norm of a vector.
    
    Formula: ||v|| = sqrt(vx^2 + vy^2 + vz^2)
    
    Reference: Euclid (~300 BC)
    
    Args:
        v: Vector (x, y, z)
    
    Returns:
        Vector norm (magnitude)
    """
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)


def normalize(v: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Normalize a vector to unit length.
    
    Formula: v_hat = v / ||v||
    
    Reference: Hermann Grassmann (1844)
    
    Args:
        v: Vector (x, y, z)
    
    Returns:
        Unit vector (x, y, z)
    """
    n = norm(v)
    if n == 0:
        return (0.0, 0.0, 0.0)
    return scalar_divide(v, n)


def angle_between_vectors(v1: Tuple[float, float, float],
                         v2: Tuple[float, float, float]) -> float:
    """
    Calculate the angle between two vectors in radians.
    
    Formula: theta = arccos((a . b) / (||a|| * ||b||))
    
    Reference: Euclid (~300 BC)
    
    Args:
        v1: First vector (x, y, z)
        v2: Second vector (x, y, z)
    
    Returns:
        Angle in radians [0, pi]
    """
    n1 = norm(v1)
    n2 = norm(v2)
    
    if n1 == 0 or n2 == 0:
        return 0.0
    
    dot = dot_product(v1, v2)
    cos_theta = dot / (n1 * n2)
    
    # Clamp to [-1, 1] to avoid numerical errors
    cos_theta = max(-1.0, min(1.0, cos_theta))
    
    return math.acos(cos_theta)


def projection(v: Tuple[float, float, float],
               onto: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Calculate the orthogonal projection of vector v onto vector onto.
    
    Formula: proj_onto(v) = ((v . onto) / ||onto||^2) * onto
    
    Reference: Hermann Grassmann (1844)
    
    Args:
        v: Vector to project (x, y, z)
        onto: Vector to project onto (x, y, z)
    
    Returns:
        Projection vector (x, y, z)
    """
    n_onto = norm(onto)
    if n_onto == 0:
        return (0.0, 0.0, 0.0)
    
    dot = dot_product(v, onto)
    scalar = dot / (n_onto ** 2)
    
    return scalar_multiply(onto, scalar)


def rotation_matrix_2d(theta: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Calculate the 2D rotation matrix for angle theta.
    
    Formula: R(theta) = [[cos(theta), -sin(theta)], [sin(theta), cos(theta)]]
    
    Reference: Leonhard Euler (1748)
    
    Args:
        theta: Rotation angle in radians
    
    Returns:
        Rotation matrix as tuple of two rows ((r11, r12), (r21, r22))
    """
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    
    return ((cos_t, -sin_t), (sin_t, cos_t))


def rotation_matrix_3d_z(theta: float) -> Tuple[Tuple[float, float, float],
                                             Tuple[float, float, float],
                                             Tuple[float, float, float]]:
    """
    Calculate the 3D rotation matrix around Z axis.
    
    Formula: Rz(theta) = [[cos, -sin, 0], [sin, cos, 0], [0, 0, 1]]
    
    Reference: Leonhard Euler (1748)
    
    Args:
        theta: Rotation angle in radians
    
    Returns:
        Rotation matrix as tuple of three rows
    """
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    
    return ((cos_t, -sin_t, 0.0),
            (sin_t, cos_t, 0.0),
            (0.0, 0.0, 1.0))


def rotation_matrix_3d_y(theta: float) -> Tuple[Tuple[float, float, float],
                                             Tuple[float, float, float],
                                             Tuple[float, float, float]]:
    """
    Calculate the 3D rotation matrix around Y axis.
    
    Formula: Ry(theta) = [[cos, 0, sin], [0, 1, 0], [-sin, 0, cos]]
    
    Reference: Leonhard Euler (1748)
    
    Args:
        theta: Rotation angle in radians
    
    Returns:
        Rotation matrix as tuple of three rows
    """
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    
    return ((cos_t, 0.0, sin_t),
            (0.0, 1.0, 0.0),
            (-sin_t, 0.0, cos_t))


def rotation_matrix_3d_x(theta: float) -> Tuple[Tuple[float, float, float],
                                             Tuple[float, float, float],
                                             Tuple[float, float, float]]:
    """
    Calculate the 3D rotation matrix around X axis.
    
    Formula: Rx(theta) = [[1, 0, 0], [0, cos, -sin], [0, sin, cos]]
    
    Reference: Leonhard Euler (1748)
    
    Args:
        theta: Rotation angle in radians
    
    Returns:
        Rotation matrix as tuple of three rows
    """
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    
    return ((1.0, 0.0, 0.0),
            (0.0, cos_t, -sin_t),
            (0.0, sin_t, cos_t))


def determinant_2x2(a: float, b: float, c: float, d: float) -> float:
    """
    Calculate the determinant of a 2x2 matrix.
    
    Formula: det([[a, b], [c, d]]) = ad - bc
    
    Reference: Gotthold Eisenstein (1843)
    
    Args:
        a, b: First row elements
        c, d: Second row elements
    
    Returns:
        Determinant
    """
    return a * d - b * c


def determinant_3x3(m: Tuple[Tuple[float, float, float],
                         Tuple[float, float, float],
                         Tuple[float, float, float]]) -> float:
    """
    Calculate the determinant of a 3x3 matrix.
    
    Reference: Gotthold Eisenstein (1843)
    
    Args:
        m: 3x3 matrix as tuple of three rows
    
    Returns:
        Determinant
    """
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
            m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
