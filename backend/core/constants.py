"""
Constantes globales du système.
"""

from enum import Enum


class Gender(str, Enum):
    """Genre d'une personne."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class GravityLevel(str, Enum):
    """Niveau de gravité d'une chute."""
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"


class ProfileType(str, Enum):
    """Type de profil utilisateur."""
    SENIOR_FRAGILE = "senior_fragile"
    SENIOR_AUTONOME = "senior_autonome"
    ADULTE = "adulte"
    HANDICAPE = "handicape"


class Role(str, Enum):
    """Rôles utilisateurs."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    FAMILY = "family"


class AlertStatus(str, Enum):
    """Statut d'une alerte."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class AlertChannel(str, Enum):
    """Canaux de notification."""
    TELEGRAM = "telegram"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class CameraStatus(str, Enum):
    """Statut d'une caméra."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class FallStatus(str, Enum):
    """Statut d'une chute."""
    DETECTED = "detected"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    PENDING_REVIEW = "pending_review"


# ─── PHYSICAL CONSTANTS ───
GRAVITY = 9.81  # m/s²


# ─── DETECTION THRESHOLDS ───
FALL_CONFIDENCE_WEIGHTS = {
    "vertical_velocity": 0.35,
    "acceleration": 0.25,
    "trunk_angle": 0.25,
    "inertia": 0.10,
    "distance_to_ground": 0.05
}

GRAVITY_LEVEL_RANGES = {
    GravityLevel.FAIBLE: (0, 25),
    GravityLevel.MOYENNE: (26, 50),
    GravityLevel.ELEVEE: (51, 75),
    GravityLevel.CRITIQUE: (76, 100)
}

# ─── PROFILE CONFIGURATIONS ───
PROFILE_CONFIG = {
    ProfileType.SENIOR_FRAGILE: {
        "delay_observation": 8,
        "velocity_threshold": -2.0,
        "angle_threshold": 50.0,
        "immobility_threshold": 5.0,
        "gravity_time_weights": {
            "intensity": 0.25,
            "time_on_ground": 0.40,
            "injury_probability": 0.25,
            "reactivity": 0.10
        }
    },
    ProfileType.SENIOR_AUTONOME: {
        "delay_observation": 12,
        "velocity_threshold": -2.5,
        "angle_threshold": 60.0,
        "immobility_threshold": 8.0,
        "gravity_time_weights": {
            "intensity": 0.30,
            "time_on_ground": 0.35,
            "injury_probability": 0.20,
            "reactivity": 0.15
        }
    },
    ProfileType.ADULTE: {
        "delay_observation": 15,
        "velocity_threshold": -3.0,
        "angle_threshold": 70.0,
        "immobility_threshold": 10.0,
        "gravity_time_weights": {
            "intensity": 0.35,
            "time_on_ground": 0.30,
            "injury_probability": 0.15,
            "reactivity": 0.20
        }
    },
    ProfileType.HANDICAPE: {
        "delay_observation": 6,
        "velocity_threshold": -1.5,
        "angle_threshold": 45.0,
        "immobility_threshold": 4.0,
        "gravity_time_weights": {
            "intensity": 0.20,
            "time_on_ground": 0.45,
            "injury_probability": 0.25,
            "reactivity": 0.10
        }
    }
}

# ─── ANTHROPOMETRIC MODEL (Dempster 1955) ───
BODY_SEGMENT_MASS = {
    0: 0.081,    # Nose (head)
    11: 0.254,   # Left shoulder
    12: 0.254,   # Right shoulder
    13: 0.054,   # Left elbow
    14: 0.054,   # Right elbow
    15: 0.032,   # Left wrist
    16: 0.032,   # Right wrist
    23: 0.254,   # Left hip
    24: 0.254,   # Right hip
    25: 0.101,   # Left knee
    26: 0.101,   # Right knee
    27: 0.044,   # Left ankle
    28: 0.044,   # Right ankle
}
