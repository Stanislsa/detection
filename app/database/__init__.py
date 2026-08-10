"""
Package de modèles de base de données.
Modèles SQLAlchemy pour la persistance des données.
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()


class CameraStatus(str, enum.Enum):
    """Statut de caméra."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class AlertSeverity(str, enum.Enum):
    """Gravité d'alerte."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertStatus(str, enum.Enum):
    """Statut d'alerte."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class UserRole(str, enum.Enum):
    """Rôle utilisateur."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class DBCamera(Base):
    """Modèle de caméra en base de données."""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    source = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False)  # webcam, rtsp, file
    room = Column(String(100))
    is_active = Column(Boolean, default=True)
    fps = Column(Integer, default=30)
    resolution_width = Column(Integer, default=1920)
    resolution_height = Column(Integer, default=1080)
    status = Column(SQLEnum(CameraStatus), default=CameraStatus.OFFLINE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    alerts = relationship("DBAlert", back_populates="camera", cascade="all, delete-orphan")


class DBAlert(Base):
    """Modèle d'alerte en base de données."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.MEDIUM)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.NEW)
    confidence = Column(Float)
    bbox_x = Column(Integer)
    bbox_y = Column(Integer)
    bbox_width = Column(Integer)
    bbox_height = Column(Integer)
    description = Column(Text)
    image_path = Column(String(500))
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    camera = relationship("DBCamera", back_populates="alerts")


class DBUser(Base):
    """Modèle d'utilisateur en base de données."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DBStatistics(Base):
    """Modèle de statistiques en base de données."""
    __tablename__ = "statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    total_alerts = Column(Integer, default=0)
    critical_alerts = Column(Integer, default=0)
    high_alerts = Column(Integer, default=0)
    medium_alerts = Column(Integer, default=0)
    low_alerts = Column(Integer, default=0)
    total_detections = Column(Integer, default=0)
    fall_detections = Column(Integer, default=0)
    intrusion_detections = Column(Integer, default=0)
    movement_detections = Column(Integer, default=0)
    active_cameras = Column(Integer, default=0)
    online_cameras = Column(Integer, default=0)
    offline_cameras = Column(Integer, default=0)
    recording_hours = Column(Float, default=0.0)
    storage_used_gb = Column(Float, default=0.0)


class DBRecording(Base):
    """Modèle d'enregistrement vidéo en base de données."""
    __tablename__ = "recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    duration_seconds = Column(Integer)
    file_size_bytes = Column(Integer)
    format = Column(String(10))  # mp4, avi, etc.
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class DBSnapshot(Base):
    """Modèle de snapshot (capture d'image) en base de données."""
    __tablename__ = "snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class DBAuditLog(Base):
    """Modèle de log d'audit en base de données."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    ip_address = Column(String(50))
    success = Column(Boolean, default=True)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    previous_hash = Column(String(64))  # Pour chaînage immuable


def init_db_engine(database_url: str = "sqlite:///./surveillance.db"):
    """
    Initialise le moteur de base de données.
    
    Args:
        database_url: URL de connexion à la base de données
    
    Returns:
        Engine SQLAlchemy
    """
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(bind=engine)
    return engine


def get_db_session(engine):
    """
    Crée une session de base de données.
    
    Args:
        engine: Engine SQLAlchemy
    
    Returns:
        Session SQLAlchemy
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
