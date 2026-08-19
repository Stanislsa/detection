"""
Configuration centralisée avec Pydantic Settings.
Support des variables d'environnement et fichiers YAML.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from pathlib import Path
from typing import Literal, Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Configuration centralisée de l'application."""
    
    # ─── APPLICATION ───
    APP_NAME: str = "SentinelAI"
    APP_VERSION: str = "2.1.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # ─── SERVER ───
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, ge=1, le=65535)
    WORKERS: int = Field(default=1, ge=1)
    
    # ─── PATHS ───
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    DATA_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data")
    LOGS_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "logs")
    MODELS_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "models")
    
    # ─── DATABASE ───
    DATABASE_URL: str = Field(
        default="sqlite:///data/db/sentinel_ai.db",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_ECHO: bool = False
    
    # ─── SECURITY ───
    SECRET_KEY: str = Field(default="dev-only-change-me-sentinelai-2026-insecure", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # MFA
    MFA_ENABLED: bool = True
    MFA_ISSUER: str = "SentinelAI"
    
    # Rate Limiting
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # Encryption
    AES_KEY_SIZE: int = 256
    PBKDF2_ITERATIONS: int = 100_000
    KEY_ROTATION_DAYS: int = 90
    
    # ─── AI/ML ───
    # Backend selection
    AI_BACKEND: Literal["auto", "cpu", "cuda", "openvino", "directml"] = "auto"
    AI_DEVICE: str = "auto"
    
    # YOLO
    YOLO_MODEL: str = "yolo11n.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.5
    YOLO_NMS_THRESHOLD: float = 0.45
    YOLO_FRAME_SKIP: int = 3
    RTSP_TRANSPORT: str = "tcp"
    RTSP_OPEN_TIMEOUT_MS: int = 5000
    RTSP_READ_TIMEOUT_MS: int = 5000
    RTSP_RECONNECT_SEC: float = 3.0
    RTSP_BUFFER_SIZE: int = 1
    DETECTION_FPS: float = 5.0
    CAMERA_LAN_SUBNET: str = "192.168.1.0/24"
    CAMERA_RTSP_USER: str = ""
    CAMERA_RTSP_PASSWORD: str = ""

    YOLO_TARGET_RESOLUTION: tuple = (640, 480)
    
    # MediaPipe
    MEDIAPIPE_MODEL_COMPLEXITY: int = 1
    MEDIAPIPE_MIN_DETECTION_CONFIDENCE: float = 0.5
    MEDIAPIPE_MIN_TRACKING_CONFIDENCE: float = 0.5
    
    # OpenVINO
    OPENVINO_ENABLED: bool = True
    OPENVINO_DEVICE: str = "AUTO"
    OPENVINO_PRECISION: Literal["FP32", "FP16", "INT8"] = "FP16"
    
    # ─── DETECTION THRESHOLDS ───
    FALL_ACCEL_THRESHOLD: float = 3.0  # g
    FALL_ANGULAR_VELOCITY_THRESHOLD: float = 200.0  # deg/s
    FALL_VERTICAL_VELOCITY_THRESHOLD: float = -2.5  # m/s
    FALL_TRUNK_ANGLE_THRESHOLD: float = 60.0  # degrees
    
    IMMOBILITY_VARIANCE_THRESHOLD: float = 0.01  # m²
    IMMOBILITY_TIME_THRESHOLD: float = 3.0  # seconds
    
    CONFIDENCE_THRESHOLD: float = 0.75
    
    # ─── CAMERA ───
    DEFAULT_FPS: int = 30
    CAMERA_TIMEOUT: int = 5
    CAMERA_RECONNECT_ATTEMPTS: int = 5
    CAMERA_RECONNECT_INTERVAL: int = 5
    
    # ─── NOTIFICATIONS ───
    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="", env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: str = Field(default="", env="TELEGRAM_CHAT_ID")
    TELEGRAM_ALERT_COOLDOWN: int = 60  # seconds
    
    # Email
    SMTP_HOST: str = Field(default="", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: str = Field(default="", env="SMTP_USER")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = True
    
    # ─── LOGGING ───
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: bool = True
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: int = 30  # days
    
    # ─── CORS ───
    CORS_ORIGINS: list = Field(default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:8000", "http://localhost:8000", "*"])
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: list = Field(default_factory=lambda: ["*"])
    
    # ─── REDIS (for sessions and cache) ───
    REDIS_URL: str = Field(default="", env="REDIS_URL")
    REDIS_SESSION_TTL: int = 86400  # 24 hours
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return (init_settings, env_settings, file_secret_settings)
    
    @validator('CORS_ORIGINS', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache()
def get_settings() -> Settings:
    """Retourne l'instance singleton des settings."""
    return Settings()


settings = get_settings()
