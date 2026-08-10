"""
Kinematics Functions

Reference: docs/scientific_engine/04_Kinematics.md
Isaac Newton - Philosophiæ Naturalis Principia Mathematica (1687)
"""

import math
from typing import Tuple, List


def average_velocity(d1: float, d2: float, t1: float, t2: float) -> float:
    """
    Calculate average velocity.
    
    Formula: v_avg = (d2 - d1) / (t2 - t1)
    
    Reference: Isaac Newton (1687)
    
    Args:
        d1: Initial position (m)
        d2: Final position (m)
        t1: Initial time (s)
        t2: Final time (s)
    
    Returns:
        Average velocity (m/s)
    """
    if t2 == t1:
        return 0.0
    return (d2 - d1) / (t2 - t1)


def average_velocity_3d(p1: Tuple[float, float, float],
                       p2: Tuple[float, float, float],
                       t1: float, t2: float) -> Tuple[float, float, float]:
    """
    Calculate average velocity vector in 3D.
    
    Formula: v_avg = (p2 - p1) / (t2 - t1)
    
    Reference: Isaac Newton (1687)
    
    Args:
        p1: Initial position (x, y, z) in meters
        p2: Final position (x, y, z) in meters
        t1: Initial time (s)
        t2: Final time (s)
    
    Returns:
        Average velocity vector (vx, vy, vz) in m/s
    """
    from .vectors import subtract_vectors, scalar_divide
    
    displacement = subtract_vectors(p2, p1)
    dt = t2 - t1
    
    if dt == 0:
        return (0.0, 0.0, 0.0)
    
    return scalar_divide(displacement, dt)


def instantaneous_velocity(positions: List[float], times: List[float]) -> List[float]:
    """
    Calculate instantaneous velocities from position and time arrays.
    
    Formula: v = dd/dt
    
    Reference: Isaac Newton / Gottfried Leibniz (1687/1684)
    
    Args:
        positions: Array of positions (m)
        times: Array of times (s)
    
    Returns:
        Array of velocities (m/s)
    """
    velocities = []
    for i in range(1, len(positions)):
        v = average_velocity(positions[i-1], positions[i], times[i-1], times[i])
        velocities.append(v)
    return velocities


def average_acceleration(v1: float, v2: float, t1: float, t2: float) -> float:
    """
    Calculate average acceleration.
    
    Formula: a_avg = (v2 - v1) / (t2 - t1)
    
    Reference: Isaac Newton (1687)
    
    Args:
        v1: Initial velocity (m/s)
        v2: Final velocity (m/s)
        t1: Initial time (s)
        t2: Final time (s)
    
    Returns:
        Average acceleration (m/s²)
    """
    if t2 == t1:
        return 0.0
    return (v2 - v1) / (t2 - t1)


def average_acceleration_3d(v1: Tuple[float, float, float],
                          v2: Tuple[float, float, float],
                          t1: float, t2: float) -> Tuple[float, float, float]:
    """
    Calculate average acceleration vector in 3D.
    
    Formula: a_avg = (v2 - v1) / (t2 - t1)
    
    Reference: Isaac Newton (1687)
    
    Args:
        v1: Initial velocity (vx, vy, vz) in m/s
        v2: Final velocity (vx, vy, vz) in m/s
        t1: Initial time (s)
        t2: Final time (s)
    
    Returns:
        Average acceleration vector (ax, ay, az) in m/s²
    """
    from .vectors import subtract_vectors, scalar_divide
    
    delta_v = subtract_vectors(v2, v1)
    dt = t2 - t1
    
    if dt == 0:
        return (0.0, 0.0, 0.0)
    
    return scalar_divide(delta_v, dt)


def instantaneous_acceleration(velocities: List[float], times: List[float]) -> List[float]:
    """
    Calculate instantaneous accelerations from velocity and time arrays.
    
    Formula: a = dv/dt
    
    Reference: Isaac Newton / Gottfried Leibniz (1687/1684)
    
    Args:
        velocities: Array of velocities (m/s)
        times: Array of times (s)
    
    Returns:
        Array of accelerations (m/s²)
    """
    accelerations = []
    for i in range(1, len(velocities)):
        a = average_acceleration(velocities[i-1], velocities[i], times[i-1], times[i])
        accelerations.append(a)
    return accelerations


def angular_velocity(theta1: float, theta2: float, t1: float, t2: float) -> float:
    """
    Calculate angular velocity.
    
    Formula: omega = (theta2 - theta1) / (t2 - t1)
    
    Reference: Leonhard Euler (1765)
    
    Args:
        theta1: Initial angle (rad)
        theta2: Final angle (rad)
        t1: Initial time (s)
        t2: Final time (s)
    
    Returns:
        Angular velocity (rad/s)
    """
    if t2 == t1:
        return 0.0
    return (theta2 - theta1) / (t2 - t1)


def angular_acceleration(omega1: float, omega2: float, t1: float, t2: float) -> float:
    """
    Calculate angular acceleration.
    
    Formula: alpha = (omega2 - omega1) / (t2 - t1)
    
    Reference: Leonhard Euler (1765)
    
    Args:
        omega1: Initial angular velocity (rad/s)
        omega2: Final angular velocity (rad/s)
        t1: Initial time (s)
        t2: Final time (s)
    
    Returns:
        Angular acceleration (rad/s²)
    """
    if t2 == t1:
        return 0.0
    return (omega2 - omega1) / (t2 - t1)


def displacement(p1: Tuple[float, float, float],
                p2: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Calculate displacement vector.
    
    Formula: dr = p2 - p1
    
    Reference: Isaac Newton (1687)
    
    Args:
        p1: Initial position (x, y, z) in meters
        p2: Final position (x, y, z) in meters
    
    Returns:
        Displacement vector (dx, dy, dz) in meters
    """
    from .vectors import subtract_vectors
    return subtract_vectors(p2, p1)


def vertical_velocity(y1: float, y2: float, t1: float, t2: float) -> float:
    """
    Calculate vertical velocity.
    
    Formula: vy = (y2 - y1) / (t2 - t1)
    
    Reference: Galileo Galilei (1638)
    
    Args:
        y1: Initial vertical position (m)
        y2: Final vertical position (m)
        t1: Initial time (s)
        t2: Final time (s)
    
    Returns:
        Vertical velocity (m/s)
    """
    if t2 == t1:
        return 0.0
    return (y2 - y1) / (t2 - t1)


def vertical_acceleration(vy1: float, vy2: float, t1: float, t2: float) -> float:
    """
    Calculate vertical acceleration.
    
    Formula: ay = (vy2 - vy1) / (t2 - t1)
    
    Reference: Galileo Galilei (1638)
    
    Args:
        vy1: Initial vertical velocity (m/s)
        vy2: Final vertical velocity (m/s)
        t1: Initial time (s)
        t2: Final time (s)
    
    Returns:
        Vertical acceleration (m/s²)
    """
    if t2 == t1:
        return 0.0
    return (vy2 - vy1) / (t2 - t1)


def horizontal_velocity(x1: float, x2: float, z1: float, z2: float,
                        t1: float, t2: float) -> float:
    """
    Calculate total horizontal velocity.
    
    Formula: vh = sqrt((dx/dt)^2 + (dz/dt)^2)
    
    Reference: Galileo Galilei (1638)
    
    Args:
        x1, z1: Initial horizontal positions (m)
        x2, z2: Final horizontal positions (m)
        t1: Initial time (s)
        t2: Final time (s)
    
    Returns:
        Horizontal velocity (m/s)
    """
    if t2 == t1:
        return 0.0
    
    vx = (x2 - x1) / (t2 - t1)
    vz = (z2 - z1) / (t2 - t1)
    
    return math.sqrt(vx**2 + vz**2)


def resultant_velocity(vx: float, vy: float, vz: float) -> float:
    """
    Calculate resultant velocity magnitude.
    
    Formula: v = sqrt(vx^2 + vy^2 + vz^2)
    
    Reference: Isaac Newton (1687)
    
    Args:
        vx, vy, vz: Velocity components (m/s)
    
    Returns:
        Resultant velocity (m/s)
    """
    return math.sqrt(vx**2 + vy**2 + vz**2)


def resultant_acceleration(ax: float, ay: float, az: float) -> float:
    """
    Calculate resultant acceleration magnitude.
    
    Formula: a = sqrt(ax^2 + ay^2 + az^2)
    
    Reference: Isaac Newton (1687)
    
    Args:
        ax, ay, az: Acceleration components (m/s²)
    
    Returns:
        Resultant acceleration (m/s²)
    """
    return math.sqrt(ax**2 + ay**2 + az**2)


def free_fall_velocity(v0: float, t: float, g: float = 9.81) -> float:
    """
    Calculate velocity during free fall.
    
    Formula: v(t) = v0 + g*t
    
    Reference: Galileo Galilei (1638)
    
    Args:
        v0: Initial velocity (m/s)
        t: Time (s)
        g: Gravitational acceleration (m/s², default 9.81)
    
    Returns:
        Velocity at time t (m/s)
    """
    return v0 + g * t


def free_fall_position(y0: float, v0: float, t: float, g: float = 9.81) -> float:
    """
    Calculate position during free fall.
    
    Formula: y(t) = y0 + v0*t + 0.5*g*t^2
    
    Reference: Galileo Galilei (1638)
    
    Args:
        y0: Initial position (m)
        v0: Initial velocity (m/s)
        t: Time (s)
        g: Gravitational acceleration (m/s², default 9.81)
    
    Returns:
        Position at time t (m)
    """
    return y0 + v0 * t + 0.5 * g * t**2


def fall_time(h: float, g: float = 9.81) -> float:
    """
    Calculate time of fall from height h.
    
    Formula: t = sqrt(2h/g)
    
    Reference: Galileo Galilei (1638)
    
    Args:
        h: Height of fall (m)
        g: Gravitational acceleration (m/s², default 9.81)
    
    Returns:
        Time of fall (s)
    """
    if h < 0:
        return 0.0
    return math.sqrt(2 * h / g)


def impact_velocity(h: float, g: float = 9.81) -> float:
    """
    Calculate impact velocity from height h.
    
    Formula: v = sqrt(2gh)
    
    Reference: Galileo Galilei (1638)
    
    Args:
        h: Height of fall (m)
        g: Gravitational acceleration (m/s², default 9.81)
    
    Returns:
        Impact velocity (m/s)
    """
    if h < 0:
        return 0.0
    return math.sqrt(2 * g * h)


def uniform_linear_motion(x0: float, v: float, t: float) -> float:
    """
    Calculate position in uniform linear motion.
    
    Formula: x(t) = x0 + v*t
    
    Reference: Isaac Newton (1687)
    
    Args:
        x0: Initial position (m)
        v: Constant velocity (m/s)
        t: Time (s)
    
    Returns:
        Position at time t (m)
    """
    return x0 + v * t


def uniformly_accelerated_motion(x0: float, v0: float, a: float, t: float) -> float:
    """
    Calculate position in uniformly accelerated motion.
    
    Formula: x(t) = x0 + v0*t + 0.5*a*t^2
    
    Reference: Isaac Newton (1687)
    
    Args:
        x0: Initial position (m)
        v0: Initial velocity (m/s)
        a: Constant acceleration (m/s²)
        t: Time (s)
    
    Returns:
        Position at time t (m)
    """
    return x0 + v0 * t + 0.5 * a * t**2


def relative_velocity(vA: Tuple[float, float, float],
                     vB: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Calculate relative velocity of A with respect to B.
    
    Formula: v_rel = vA - vB
    
    Reference: Galileo Galilei (1632)
    
    Args:
        vA: Velocity of object A (vx, vy, vz) in m/s
        vB: Velocity of object B (vx, vy, vz) in m/s
    
    Returns:
        Relative velocity (vx, vy, vz) in m/s
    """
    from .vectors import subtract_vectors
    return subtract_vectors(vA, vB)


def trajectory(positions: List[Tuple[float, float, float]],
             times: List[float]) -> List[Tuple[float, float, float]]:
    """
    Get the trajectory (path) from position and time arrays.
    
    Reference: Isaac Newton (1687)
    
    Args:
        positions: Array of positions (x, y, z) in meters
        times: Array of times (s)
    
    Returns:
        Trajectory as list of (x, y, z) positions
    """
    return positions


def curvature(v: Tuple[float, float, float],
             a: Tuple[float, float, float]) -> float:
    """
    Calculate curvature of a trajectory.
    
    Formula: kappa = ||v x a|| / ||v||^3
    
    Reference: Augustin-Louis Cauchy (1826)
    
    Args:
        v: Velocity vector (vx, vy, vz) in m/s
        a: Acceleration vector (ax, ay, az) in m/s²
    
    Returns:
        Curvature (m⁻¹)
    """
    from .vectors import cross_product, norm
    
    cross = cross_product(v, a)
    cross_norm = norm(cross)
    v_norm = norm(v)
    
    if v_norm == 0:
        return 0.0
    
    return cross_norm / (v_norm ** 3)
