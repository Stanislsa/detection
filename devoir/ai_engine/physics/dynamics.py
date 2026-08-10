"""
Dynamics Functions

Reference: docs/scientific_engine/05_Dynamics.md
Isaac Newton - Philosophiæ Naturalis Principia Mathematica (1687)
"""

import math
from typing import Tuple


def newton_second_law(mass: float, acceleration: float) -> float:
    """
    Calculate force using Newton's second law.
    
    Formula: F = m * a
    
    Reference: Isaac Newton (1687)
    
    Args:
        mass: Mass in kg
        acceleration: Acceleration in m/s²
    
    Returns:
        Force in Newtons (N)
    """
    return mass * acceleration


def weight(mass: float, g: float = 9.81) -> float:
    """
    Calculate weight (gravitational force).
    
    Formula: P = m * g
    
    Reference: Isaac Newton (1687)
    
    Args:
        mass: Mass in kg
        g: Gravitational acceleration (m/s², default 9.81)
    
    Returns:
        Weight in Newtons (N)
    """
    return mass * g


def kinetic_energy(mass: float, velocity: float) -> float:
    """
    Calculate kinetic energy.
    
    Formula: Ec = 0.5 * m * v^2
    
    Reference: Gottfried Leibniz / Isaac Newton (1686/1687)
    
    Args:
        mass: Mass in kg
        velocity: Velocity in m/s
    
    Returns:
        Kinetic energy in Joules (J)
    """
    return 0.5 * mass * velocity**2


def kinetic_energy_3d(mass: float, velocity: Tuple[float, float, float]) -> float:
    """
    Calculate kinetic energy from 3D velocity vector.
    
    Formula: Ec = 0.5 * m * ||v||^2
    
    Reference: Gottfried Leibniz / Isaac Newton (1686/1687)
    
    Args:
        mass: Mass in kg
        velocity: Velocity vector (vx, vy, vz) in m/s
    
    Returns:
        Kinetic energy in Joules (J)
    """
    from .vectors import norm
    v_norm = norm(velocity)
    return 0.5 * mass * v_norm**2


def potential_energy(mass: float, height: float, g: float = 9.81) -> float:
    """
    Calculate gravitational potential energy.
    
    Formula: Ep = m * g * h
    
    Reference: William Rankine (1853)
    
    Args:
        mass: Mass in kg
        height: Height in meters
        g: Gravitational acceleration (m/s², default 9.81)
    
    Returns:
        Potential energy in Joules (J)
    """
    return mass * g * height


def mechanical_energy(kinetic: float, potential: float) -> float:
    """
    Calculate total mechanical energy.
    
    Formula: Em = Ec + Ep
    
    Reference: William Rankine (1853)
    
    Args:
        kinetic: Kinetic energy in J
        potential: Potential energy in J
    
    Returns:
        Mechanical energy in Joules (J)
    """
    return kinetic + potential


def work(force: float, displacement: float, angle: float = 0.0) -> float:
    """
    Calculate work done by a force.
    
    Formula: W = F * d * cos(theta)
    
    Reference: Gaspard-Gustave Coriolis (1829)
    
    Args:
        force: Force in Newtons (N)
        displacement: Displacement in meters (m)
        angle: Angle between force and displacement in radians (default 0)
    
    Returns:
        Work in Joules (J)
    """
    return force * displacement * math.cos(angle)


def momentum(mass: float, velocity: float) -> float:
    """
    Calculate momentum (linear momentum).
    
    Formula: p = m * v
    
    Reference: Isaac Newton (1687)
    
    Args:
        mass: Mass in kg
        velocity: Velocity in m/s
    
    Returns:
        Momentum in kg·m/s
    """
    return mass * velocity


def momentum_3d(mass: float, velocity: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Calculate momentum vector in 3D.
    
    Formula: p = m * v
    
    Reference: Isaac Newton (1687)
    
    Args:
        mass: Mass in kg
        velocity: Velocity vector (vx, vy, vz) in m/s
    
    Returns:
        Momentum vector (px, py, pz) in kg·m/s
    """
    from .vectors import scalar_multiply
    return scalar_multiply(velocity, mass)


def angular_momentum(radius: Tuple[float, float, float],
                    momentum: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Calculate angular momentum.
    
    Formula: L = r x p
    
    Reference: Isaac Newton (1687)
    
    Args:
        radius: Position vector (rx, ry, rz) in meters
        momentum: Momentum vector (px, py, pz) in kg·m/s
    
    Returns:
        Angular momentum vector (Lx, Ly, Lz) in kg·m²/s
    """
    from .vectors import cross_product
    return cross_product(radius, momentum)


def moment_of_inertia_point(mass: float, radius: float) -> float:
    """
    Calculate moment of inertia for a point mass.
    
    Formula: I = m * r^2
    
    Reference: Leonhard Euler (1765)
    
    Args:
        mass: Mass in kg
        radius: Distance from rotation axis in meters
    
    Returns:
        Moment of inertia in kg·m²
    """
    return mass * radius**2


def friction_force(mu_k: float, normal_force: float) -> float:
    """
    Calculate kinetic friction force.
    
    Formula: Ff = mu_k * N
    
    Reference: Guillaume Amontons / Charles-Augustin Coulomb (1699/1785)
    
    Args:
        mu_k: Coefficient of kinetic friction (dimensionless)
        normal_force: Normal force in Newtons (N)
    
    Returns:
        Friction force in Newtons (N)
    """
    return mu_k * normal_force


def impact_force(mass: float, delta_v: float, delta_t: float) -> float:
    """
    Calculate impact force using impulse-momentum theorem.
    
    Formula: F = (m * delta_v) / delta_t
    
    Reference: Isaac Newton (1687)
    
    Args:
        mass: Mass in kg
        delta_v: Change in velocity in m/s
        delta_t: Impact duration in seconds
    
    Returns:
        Impact force in Newtons (N)
    """
    if delta_t == 0:
        return 0.0
    return (mass * delta_v) / delta_t


def coefficient_of_restitution(v_after: float, v_before: float) -> float:
    """
    Calculate coefficient of restitution.
    
    Formula: e = v_after / v_before
    
    Reference: Isaac Newton (1687)
    
    Args:
        v_after: Velocity after impact (m/s)
        v_before: Velocity before impact (m/s)
    
    Returns:
        Coefficient of restitution (dimensionless)
    """
    if v_before == 0:
        return 0.0
    return abs(v_after / v_before)


def coefficient_of_restitution_height(h_rebound: float, h_fall: float) -> float:
    """
    Calculate coefficient of restitution from heights.
    
    Formula: e = sqrt(h_rebound / h_fall)
    
    Reference: Isaac Newton (1687)
    
    Args:
        h_rebound: Rebound height in meters
        h_fall: Fall height in meters
    
    Returns:
        Coefficient of restitution (dimensionless)
    """
    if h_fall == 0:
        return 0.0
    return math.sqrt(h_rebound / h_fall)


def centripetal_force(mass: float, velocity: float, radius: float) -> float:
    """
    Calculate centripetal force.
    
    Formula: Fc = (m * v^2) / r
    
    Reference: Christiaan Huygens (1673)
    
    Args:
        mass: Mass in kg
        velocity: Tangential velocity in m/s
        radius: Radius of circular path in meters
    
    Returns:
        Centripetal force in Newtons (N)
    """
    if radius == 0:
        return 0.0
    return (mass * velocity**2) / radius


def centripetal_force_angular(mass: float, angular_velocity: float, radius: float) -> float:
    """
    Calculate centripetal force using angular velocity.
    
    Formula: Fc = m * omega^2 * r
    
    Reference: Christiaan Huygens (1673)
    
    Args:
        mass: Mass in kg
        angular_velocity: Angular velocity in rad/s
        radius: Radius of circular path in meters
    
    Returns:
        Centripetal force in Newtons (N)
    """
    return mass * angular_velocity**2 * radius


def ground_reaction_force(mass: float, g: float = 9.81, 
                         acceleration: Tuple[float, float, float] = (0, 0, 0)) -> Tuple[float, float, float]:
    """
    Calculate ground reaction force.
    
    Formula: F_grf = m * g + m * a
    
    Reference: Isaac Newton (1687)
    
    Args:
        mass: Mass in kg
        g: Gravitational acceleration (m/s², default 9.81)
        acceleration: Acceleration vector (ax, ay, az) in m/s²
    
    Returns:
        Ground reaction force vector (Fx, Fy, Fz) in Newtons (N)
    """
    from .vectors import scalar_multiply, add_vectors
    
    weight_vector = (0, mass * g, 0)
    ma_vector = scalar_multiply(acceleration, mass)
    
    return add_vectors(weight_vector, ma_vector)


def impact_pressure(force: float, area: float) -> float:
    """
    Calculate impact pressure.
    
    Formula: P = F / A
    
    Reference: Blaise Pascal (1647)
    
    Args:
        force: Force in Newtons (N)
        area: Contact area in square meters (m²)
    
    Returns:
        Pressure in Pascals (Pa)
    """
    if area == 0:
        return 0.0
    return force / area


def impact_energy(mass: float, impact_velocity: float) -> float:
    """
    Calculate impact energy.
    
    Formula: E = 0.5 * m * v^2
    
    Reference: Gottfried Leibniz (1686)
    
    Args:
        mass: Mass in kg
        impact_velocity: Impact velocity in m/s
    
    Returns:
        Impact energy in Joules (J)
    """
    return 0.5 * mass * impact_velocity**2


def power(force: float, velocity: float) -> float:
    """
    Calculate power.
    
    Formula: P = F * v
    
    Reference: James Watt (1782)
    
    Args:
        force: Force in Newtons (N)
        velocity: Velocity in m/s
    
    Returns:
        Power in Watts (W)
    """
    return force * velocity


def power_3d(force: Tuple[float, float, float],
             velocity: Tuple[float, float, float]) -> float:
    """
    Calculate power from 3D force and velocity vectors.
    
    Formula: P = F . v
    
    Reference: James Watt (1782)
    
    Args:
        force: Force vector (Fx, Fy, Fz) in Newtons (N)
        velocity: Velocity vector (vx, vy, vz) in m/s
    
    Returns:
        Power in Watts (W)
    """
    from .vectors import dot_product
    return dot_product(force, velocity)
