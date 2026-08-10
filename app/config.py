"""
Configuration centralisée du système de détection de chutes.
Pydantic Settings avec validation automatique et chargement .env.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from pathlib import Path
from typing import Literal
import os


class Settings(BaseSettings):
    # ─── APPLICATION ───
    APP_NAME: str = "Fall Detection System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, ge=1, le=65535)
    
    # Chemins de base
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    DATA_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data")
    LOGS_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "logs")
    
    # ─── BASE DE DONNÉES ───
    DATABASE_URL: str = Field(
        default="sqlite:///data/db/fall_detection.db",
        env="DATABASE_URL"
    )
    
    # ─── SÉCURITÉ ───
    SECRET_KEY: str = Field(..., env="SECRET_KEY")  # Requis
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240  # 4 heures
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MFA_ENABLED: bool = True
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # ─── CHIFFREMENT ───
    AES_KEY_SIZE: int = 256  # bits
    PBKDF2_ITERATIONS: int = 100_000
    KEY_ROTATION_DAYS: int = 90
    
    # ─── CONSTANTES PHYSIQUES ───
    GRAVITY: float = 9.81  # m/s² (Galilée)
    
    # ─── SEUILS DE DÉTECTION (Bourke et al., 2007) ───
    FALL_ACCEL_THRESHOLD: float = Field(default=3.0)  # en g
    FALL_ANGULAR_VELOCITY_THRESHOLD: float = 200.0  # deg/s
    FALL_VERTICAL_VELOCITY_THRESHOLD: float = -2.5  # m/s
    FALL_TRUNK_ANGLE_THRESHOLD: float = 60.0  # degrés
    FALL_TRUNK_ANGLE_STRONG: float = 75.0  # degrés
    
    # ─── SEUILS D'IMMOBILITÉ ───
    IMMOBILITY_VARIANCE_THRESHOLD: float = 0.01  # m²
    IMMOBILITY_TIME_THRESHOLD: float = 3.0  # secondes
    
    # ─── PARAMÈTRES CAMÉRA ───
    DEFAULT_FPS: int = 30
    FRAME_INTERVAL: float = 1.0 / 30  # secondes
    CAMERA_TIMEOUT: int = 5  # secondes
    
    # ─── ALERTES ───
    TELEGRAM_BOT_TOKEN: str = Field(default="", env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = Field(default="", env="TELEGRAM_CHAT_ID")
    SMTP_HOST: str = Field(default="", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(default="", env="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    ALERT_COOLDOWN_SECONDS: int = 60  # Anti-spam
    
    # ─── SCORING ───
    CONFIDENCE_THRESHOLD: float = 0.75
    
    # ─── MEDIAPIPE ───
    MEDIAPIPE_MODEL_COMPLEXITY: int = Field(default=1)
    MEDIAPIPE_MIN_DETECTION_CONFIDENCE: float = Field(default=0.5)
    MEDIAPIPE_MIN_TRACKING_CONFIDENCE: float = Field(default=0.5)
    
    # ─── YOLO ───
    YOLO_MODEL_NAME: str = "yolo11n.pt"  # Nano pour CPU
    YOLO_CONFIDENCE_THRESHOLD: float = 0.5
    YOLO_USE_OPENVINO: bool = True  # Optimisation Intel CPU
    YOLO_FRAME_SKIP: int = 3  # 1 frame sur 3 traitée
    YOLO_DEVICE: str = "cpu"  # cpu, cuda, openvino
    YOLO_TARGET_RESOLUTION: tuple = (640, 480)  # Résolution réduite pour performance
    
    # ─── LOGGING ───
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instance globale
settings = Settings()

# ─── PROFILS UTILISATEUR (Arbre de décision adaptatif) ───

PROFILE_CONFIG = {
    "senior_fragile": {
        "delay_observation": 8,      # secondes
        "velocity_threshold": -2.0,   # m/s
        "angle_threshold": 50.0,      # degrés
        "immobility_threshold": 5.0,  # secondes
        "gravity_time_weights": {     # Pondération score gravité
            "intensity": 0.25,
            "time_on_ground": 0.40,   # Plus de poids au temps (fragilité)
            "injury_probability": 0.25,
            "reactivity": 0.10
        }
    },
    "senior_autonome": {
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
    "adulte": {
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
    "handicape": {
        "delay_observation": 6,
        "velocity_threshold": -1.5,
        "angle_threshold": 45.0,
        "immobility_threshold": 4.0,
        "gravity_time_weights": {
            "intensity": 0.20,
            "time_on_ground": 0.45,   # Très sensible au temps
            "injury_probability": 0.25,
            "reactivity": 0.10
        }
    }
}

# ─── POIDS DU SCORE DE CONFIANCE CHUTE ───
FALL_CONFIDENCE_WEIGHTS = {
    "vertical_velocity": 0.35,   # Srikongtham et al.
    "acceleration": 0.25,        # Bourke et al.
    "trunk_angle": 0.25,         # Noury et al.
    "inertia": 0.10,             # Euler
    "distance_to_ground": 0.05   # Proposition
}

# ─── NIVEAUX DE GRAVITÉ ───
GRAVITY_LEVELS = {
    "faible": (0, 25),
    "moyenne": (26, 50),
    "elevee": (51, 75),
    "critique": (76, 100)
}

# ─── MODÈLE ANTHROPOMÉTRIQUE DEMPSTER (1955) ───
# Ratio de masse par landmark MediaPipe (33 points)
BODY_SEGMENT_MASS = {
    0: 0.081,    # Nez (tête)
    11: 0.254,   # Épaule gauche
    12: 0.254,   # Épaule droite
    13: 0.054,   # Coude gauche
    14: 0.054,   # Coude droit
    15: 0.032,   # Poignet gauche
    16: 0.032,   # Poignet droit
    23: 0.254,   # Hanche gauche
    24: 0.254,   # Hanche droite
    25: 0.101,   # Genou gauche
    26: 0.101,   # Genou droit
    27: 0.044,   # Cheville gauche
    28: 0.044,   # Cheville droite
}
