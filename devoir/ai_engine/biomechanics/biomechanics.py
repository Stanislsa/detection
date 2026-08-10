"""
Biomechanics Functions

Reference: docs/scientific_engine/06_Biomechanics.md
D. A. Winter - Biomechanics and Motor Control of Human Movement (1990)
"""

import math
from typing import Tuple, List


def trunk_angle(shoulder_left: Tuple[float, float, float],
                shoulder_right: Tuple[float, float, float],
                vertical: Tuple[float, float, float] = (0, 1, 0),
                degrees: bool = True) -> float:
    """
    Calculate the trunk inclination angle.
    
    Formula: theta = arccos((v_shoulders . v_vertical) / (||v_shoulders|| * ||v_vertical||))
    
    Reference: Leiyue Yao et al. (2017) - DOI: 10.1109/ACCESS.2017.2655042
    
    Args:
        shoulder_left: Left shoulder position (x, y, z) in meters
        shoulder_right: Right shoulder position (x, y, z) in meters
        vertical: Vertical unit vector (default (0, 1, 0))
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Trunk inclination angle
    """
    from .vectors import subtract_vectors, norm, dot_product
    
    shoulder_center = ((shoulder_left[0] + shoulder_right[0]) / 2,
                      (shoulder_left[1] + shoulder_right[1]) / 2,
                      (shoulder_left[2] + shoulder_right[2]) / 2)
    
    # Vector from hip center to shoulder center (simplified)
    # In practice, this would use hip positions
    v_trunk = subtract_vectors(shoulder_center, (0, 0, 0))
    
    n_trunk = norm(v_trunk)
    n_vertical = norm(vertical)
    
    if n_trunk == 0 or n_vertical == 0:
        return 0.0
    
    dot = dot_product(v_trunk, vertical)
    cos_theta = dot / (n_trunk * n_vertical)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    
    angle = math.acos(cos_theta)
    
    if degrees:
        angle = math.degrees(angle)
    
    return angle


def head_trunk_angle(nose: Tuple[float, float, float],
                    shoulder_center: Tuple[float, float, float],
                    hip_center: Tuple[float, float, float],
                    degrees: bool = True) -> float:
    """
    Calculate the head-trunk (cervical) angle.
    
    Reference: M. J. O'Brien, D. N. Bohannon (2007) - DOI: 10.1007/s00147-007-0214-4
    
    Args:
        nose: Nose position (x, y, z) in meters
        shoulder_center: Center of shoulders (x, y, z) in meters
        hip_center: Center of hips (x, y, z) in meters
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Head-trunk angle
    """
    from .vectors import subtract_vectors, norm, dot_product
    
    v_head_trunk = subtract_vectors(nose, shoulder_center)
    v_trunk = subtract_vectors(shoulder_center, hip_center)
    
    n1 = norm(v_head_trunk)
    n2 = norm(v_trunk)
    
    if n1 == 0 or n2 == 0:
        return 0.0
    
    dot = dot_product(v_head_trunk, v_trunk)
    cos_theta = dot / (n1 * n2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    
    angle = math.acos(cos_theta)
    
    if degrees:
        angle = math.degrees(angle)
    
    return angle


def hip_angle(hip: Tuple[float, float, float],
             knee: Tuple[float, float, float],
             ankle: Tuple[float, float, float],
             degrees: bool = True) -> float:
    """
    Calculate the hip angle.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        hip: Hip position (x, y, z) in meters
        knee: Knee position (x, y, z) in meters
        ankle: Ankle position (x, y, z) in meters
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Hip angle
    """
    from .vectors import subtract_vectors, norm, dot_product
    
    v_thigh = subtract_vectors(knee, hip)
    v_leg = subtract_vectors(ankle, knee)
    
    n1 = norm(v_thigh)
    n2 = norm(v_leg)
    
    if n1 == 0 or n2 == 0:
        return 0.0
    
    dot = dot_product(v_thigh, v_leg)
    cos_theta = dot / (n1 * n2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    
    angle = math.acos(cos_theta)
    
    if degrees:
        angle = math.degrees(angle)
    
    return angle


def knee_angle(hip: Tuple[float, float, float],
              knee: Tuple[float, float, float],
              ankle: Tuple[float, float, float],
              degrees: bool = True) -> float:
    """
    Calculate the knee angle.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        hip: Hip position (x, y, z) in meters
        knee: Knee position (x, y, z) in meters
        ankle: Ankle position (x, y, z) in meters
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Knee angle
    """
    from .vectors import subtract_vectors, norm, dot_product
    
    v_thigh = subtract_vectors(knee, hip)
    v_leg = subtract_vectors(ankle, knee)
    
    n1 = norm(v_thigh)
    n2 = norm(v_leg)
    
    if n1 == 0 or n2 == 0:
        return 0.0
    
    dot = dot_product(v_thigh, v_leg)
    cos_theta = dot / (n1 * n2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    
    angle = math.acos(cos_theta)
    
    if degrees:
        angle = math.degrees(angle)
    
    return angle


def center_of_gravity(points: List[Tuple[float, float, float]],
                     weights: List[float] = None) -> Tuple[float, float, float]:
    """
    Calculate the center of gravity from body landmarks.
    
    Formula: CG = (sum(wi * Pi)) / sum(wi)
    
    Reference: Claude Perrault (1670)
    
    Args:
        points: List of (x, y, z) coordinates for body landmarks
        weights: Optional weights for each point (default: equal weights)
    
    Returns:
        Center of gravity coordinates (x, y, z)
    """
    if weights is None:
        weights = [1.0] * len(points)
    
    if len(points) == 0:
        return (0.0, 0.0, 0.0)
    
    total_weight = sum(weights)
    if total_weight == 0:
        return (0.0, 0.0, 0.0)
    
    cx = sum(w * p[0] for w, p in zip(weights, points)) / total_weight
    cy = sum(w * p[1] for w, p in zip(weights, points)) / total_weight
    cz = sum(w * p[2] for w, p in zip(weights, points)) / total_weight
    
    return (cx, cy, cz)


def center_of_gravity_height(cg: Tuple[float, float, float],
                            total_height: float = None) -> float:
    """
    Calculate the height of the center of gravity.
    
    Reference: Claude Perrault (1670)
    
    Args:
        cg: Center of gravity coordinates (x, y, z)
        total_height: Total body height in meters (optional)
    
    Returns:
        Height of center of gravity in meters (or percentage if total_height provided)
    """
    height = cg[1]
    
    if total_height is not None and total_height > 0:
        return (height / total_height) * 100
    
    return height


def postural_orientation(shoulder_left: Tuple[float, float, float],
                        shoulder_right: Tuple[float, float, float],
                        hip_left: Tuple[float, float, float],
                        hip_right: Tuple[float, float, float],
                        degrees: bool = True) -> Tuple[float, float, float]:
    """
    Calculate postural orientation using Euler angles (roll, pitch, yaw).
    
    Reference: Leonhard Euler (1775)
    
    Args:
        shoulder_left: Left shoulder position (x, y, z)
        shoulder_right: Right shoulder position (x, y, z)
        hip_left: Left hip position (x, y, z)
        hip_right: Right hip position (x, y, z)
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Euler angles (roll, pitch, yaw)
    """
    from .vectors import subtract_vectors, norm, normalize
    
    shoulder_center = ((shoulder_left[0] + shoulder_right[0]) / 2,
                      (shoulder_left[1] + shoulder_right[1]) / 2,
                      (shoulder_left[2] + shoulder_right[2]) / 2)
    
    hip_center = ((hip_left[0] + hip_right[0]) / 2,
                 (hip_left[1] + hip_right[1]) / 2,
                 (hip_left[2] + hip_right[2]) / 2)
    
    trunk_vector = subtract_vectors(shoulder_center, hip_center)
    trunk_normalized = normalize(trunk_vector)
    
    # Simplified Euler angles calculation
    # In practice, this would use full rotation matrix computation
    
    # Pitch: angle with vertical
    pitch = math.acos(max(-1.0, min(1.0, trunk_normalized[1])))
    
    # Roll: angle of shoulder line with horizontal
    shoulder_vector = subtract_vectors(shoulder_right, shoulder_left)
    roll = math.atan2(shoulder_vector[1], shoulder_vector[0])
    
    # Yaw: angle in horizontal plane
    yaw = math.atan2(trunk_normalized[0], trunk_normalized[2])
    
    if degrees:
        pitch = math.degrees(pitch)
        roll = math.degrees(roll)
        yaw = math.degrees(yaw)
    
    return (roll, pitch, yaw)


def shoulder_width(shoulder_left: Tuple[float, float, float],
                  shoulder_right: Tuple[float, float, float]) -> float:
    """
    Calculate shoulder width.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        shoulder_left: Left shoulder position (x, y, z) in meters
        shoulder_right: Right shoulder position (x, y, z) in meters
    
    Returns:
        Shoulder width in meters
    """
    from .vectors import subtract_vectors, norm
    return norm(subtract_vectors(shoulder_right, shoulder_left))


def hip_width(hip_left: Tuple[float, float, float],
             hip_right: Tuple[float, float, float]) -> float:
    """
    Calculate hip width.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        hip_left: Left hip position (x, y, z) in meters
        hip_right: Right hip position (x, y, z) in meters
    
    Returns:
        Hip width in meters
    """
    from .vectors import subtract_vectors, norm
    return norm(subtract_vectors(hip_right, hip_left))


def hip_height(hip_left: Tuple[float, float, float],
              hip_right: Tuple[float, float, float]) -> float:
    """
    Calculate hip height (average of both hips).
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        hip_left: Left hip position (x, y, z) in meters
        hip_right: Right hip position (x, y, z) in meters
    
    Returns:
        Hip height in meters
    """
    return (hip_left[1] + hip_right[1]) / 2


def postural_stability_index(cg_positions: List[Tuple[float, float, float]],
                           support_width: float) -> float:
    """
    Calculate postural stability index.
    
    Formula: ISP = sigma_CG / L_support
    
    Reference: M. H. Woollacott, A. Shumway-Cook (2002)
    
    Args:
        cg_positions: List of center of gravity positions over time
        support_width: Width of the base of support in meters
    
    Returns:
        Postural stability index (dimensionless)
    """
    if len(cg_positions) < 2 or support_width == 0:
        return 0.0
    
    # Calculate standard deviation of CG position
    mean_x = sum(p[0] for p in cg_positions) / len(cg_positions)
    mean_y = sum(p[1] for p in cg_positions) / len(cg_positions)
    
    variance = sum((p[0] - mean_x)**2 + (p[1] - mean_y)**2 for p in cg_positions) / len(cg_positions)
    sigma_cg = math.sqrt(variance)
    
    return sigma_cg / support_width


def center_of_gravity_velocity(cg_positions: List[Tuple[float, float, float]],
                               times: List[float]) -> Tuple[float, float, float]:
    """
    Calculate center of gravity velocity.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        cg_positions: List of center of gravity positions (x, y, z)
        times: List of corresponding times (s)
    
    Returns:
        Velocity vector (vx, vy, vz) in m/s
    """
    from .vectors import subtract_vectors, scalar_divide
    
    if len(cg_positions) < 2 or len(times) < 2:
        return (0.0, 0.0, 0.0)
    
    p1 = cg_positions[0]
    p2 = cg_positions[-1]
    t1 = times[0]
    t2 = times[-1]
    
    displacement = subtract_vectors(p2, p1)
    dt = t2 - t1
    
    if dt == 0:
        return (0.0, 0.0, 0.0)
    
    return scalar_divide(displacement, dt)


def center_of_gravity_acceleration(cg_velocities: List[Tuple[float, float, float]],
                                   times: List[float]) -> Tuple[float, float, float]:
    """
    Calculate center of gravity acceleration.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        cg_velocities: List of center of gravity velocities (vx, vy, vz)
        times: List of corresponding times (s)
    
    Returns:
        Acceleration vector (ax, ay, az) in m/s²
    """
    from .vectors import subtract_vectors, scalar_divide
    
    if len(cg_velocities) < 2 or len(times) < 2:
        return (0.0, 0.0, 0.0)
    
    v1 = cg_velocities[0]
    v2 = cg_velocities[-1]
    t1 = times[0]
    t2 = times[-1]
    
    delta_v = subtract_vectors(v2, v1)
    dt = t2 - t1
    
    if dt == 0:
        return (0.0, 0.0, 0.0)
    
    return scalar_divide(delta_v, dt)


def hip_opening_angle(hip_center: Tuple[float, float, float],
                     hip_left: Tuple[float, float, float],
                     hip_right: Tuple[float, float, float],
                     degrees: bool = True) -> float:
    """
    Calculate hip opening angle.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        hip_center: Center of hips (x, y, z) in meters
        hip_left: Left hip position (x, y, z) in meters
        hip_right: Right hip position (x, y, z) in meters
        degrees: If True, return in degrees; if False, in radians
    
    Returns:
        Hip opening angle
    """
    from .vectors import subtract_vectors, norm, dot_product
    
    v_left = subtract_vectors(hip_left, hip_center)
    v_right = subtract_vectors(hip_right, hip_center)
    
    n1 = norm(v_left)
    n2 = norm(v_right)
    
    if n1 == 0 or n2 == 0:
        return 0.0
    
    dot = dot_product(v_left, v_right)
    cos_theta = dot / (n1 * n2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    
    angle = math.acos(cos_theta)
    
    if degrees:
        angle = math.degrees(angle)
    
    return angle


def step_length(ankle_left: Tuple[float, float, float],
              ankle_right: Tuple[float, float, float]) -> float:
    """
    Calculate step length.
    
    Reference: D. A. Winter (1990) - DOI: 10.1002/9780470694012
    
    Args:
        ankle_left: Left ankle position (x, y, z) in meters
        ankle_right: Right ankle position (x, y, z) in meters
    
    Returns:
        Step length in meters
    """
    from .vectors import subtract_vectors, norm
    return norm(subtract_vectors(ankle_right, ankle_left))


def postural_symmetry_index(point_left: Tuple[float, float, float],
                           point_right: Tuple[float, float, float]) -> float:
    """
    Calculate postural symmetry index.
    
    Formula: ISP = 1 - ||p_left - p_right|| / (||p_left|| + ||p_right||)
    
    Reference: J. H. J. Allum, A. F. Bloem (1999) - DOI: 10.1016/S0966-6362(99)00034-6
    
    Args:
        point_left: Left side point (x, y, z) in meters
        point_right: Right side point (x, y, z) in meters
    
    Returns:
        Postural symmetry index (0 = asymmetric, 1 = symmetric)
    """
    from .vectors import subtract_vectors, norm
    
    diff = norm(subtract_vectors(point_left, point_right))
    norm_left = norm(point_left)
    norm_right = norm(point_right)
    
    if norm_left + norm_right == 0:
        return 1.0
    
    return 1.0 - (diff / (norm_left + norm_right))
