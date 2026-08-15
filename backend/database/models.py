"""
Unified SQLAlchemy models with encryption support.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    ForeignKey, Text, Enum as SQLEnum, JSON, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

from .base import Base
from backend.core.constants import (
    Gender, GravityLevel, ProfileType, Role, 
    AlertStatus, AlertChannel, CameraStatus, FallStatus
)
from backend.core.logger import get_logger

logger = get_logger(__name__)


class User(Base):
    """User model for system authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))  # Argon2 hash
    role = Column(SQLEnum(Role), default=Role.VIEWER)
    
    # MFA
    totp_secret_encrypted = Column(Text)  # Encrypted TOTP secret
    mfa_enabled = Column(Boolean, default=False)
    
    # Account status
    is_active = Column(Boolean, default=True, index=True)
    is_locked = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Timestamps
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def lock_account(self, duration_minutes: int):
        """Lock account for specified duration."""
        from datetime import timedelta
        self.is_locked = True
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def unlock_account(self):
        """Unlock account."""
        self.is_locked = False
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def is_account_locked(self) -> bool:
        """Check if account is currently locked."""
        if not self.is_locked:
            return False
        if self.locked_until and datetime.utcnow() > self.locked_until:
            self.unlock_account()
            return False
        return True
    
    def increment_failed_attempts(self, lockout_duration: int):
        """Increment failed login attempts and lock if threshold reached."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # MAX_LOGIN_ATTEMPTS
            self.lock_account(lockout_duration)
    
    def reset_failed_attempts(self):
        """Reset failed login attempts after successful login."""
        self.failed_login_attempts = 0


class Person(Base):
    """Person model for monitored individuals."""
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(DateTime)
    gender = Column(SQLEnum(Gender))
    
    # Physical characteristics
    height = Column(Float)  # cm
    weight = Column(Float)  # kg
    
    # Profile
    profile_type = Column(SQLEnum(ProfileType), default=ProfileType.SENIOR_AUTONOME, index=True)
    mobility_notes = Column(Text)
    
    # Emergency contact (encrypted)
    emergency_contact_name = Column(String(200))
    emergency_contact_phone_encrypted = Column(Text)
    emergency_contact_email_encrypted = Column(Text)
    
    # Location (encrypted)
    address = Column(String(500))
    gps_latitude_encrypted = Column(Text)
    gps_longitude_encrypted = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fall_events = relationship("FallEvent", back_populates="person", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_person_name', 'first_name', 'last_name'),
        Index('idx_person_profile', 'profile_type'),
    )
    
    def encrypt_sensitive_data(self, phone: str = None, email: str = None, 
                               latitude: float = None, longitude: float = None):
        """Encrypt sensitive data using AES-256-GCM."""
        from backend.security.encryption import EncryptionManager
        from backend.core.config import settings
        
        enc = EncryptionManager(settings.SECRET_KEY)
        
        if phone:
            self.emergency_contact_phone_encrypted = enc.encrypt(phone.encode()).decode()
        if email:
            self.emergency_contact_email_encrypted = enc.encrypt(email.encode()).decode()
        if latitude is not None:
            self.gps_latitude_encrypted = enc.encrypt(str(latitude).encode()).decode()
        if longitude is not None:
            self.gps_longitude_encrypted = enc.encrypt(str(longitude).encode()).decode()
    
    def decrypt_sensitive_data(self) -> dict:
        """Decrypt and return sensitive data."""
        from backend.security.encryption import EncryptionManager
        from backend.core.config import settings
        
        enc = EncryptionManager(settings.SECRET_KEY)
        result = {}
        
        try:
            if self.emergency_contact_phone_encrypted:
                result['phone'] = enc.decrypt(self.emergency_contact_phone_encrypted.encode()).decode()
        except Exception as e:
            logger.warning(f"Failed to decrypt phone: {e}")
            result['phone'] = None
        
        try:
            if self.emergency_contact_email_encrypted:
                result['email'] = enc.decrypt(self.emergency_contact_email_encrypted.encode()).decode()
        except Exception as e:
            logger.warning(f"Failed to decrypt email: {e}")
            result['email'] = None
        
        try:
            if self.gps_latitude_encrypted:
                result['latitude'] = float(enc.decrypt(self.gps_latitude_encrypted.encode()).decode())
        except Exception as e:
            logger.warning(f"Failed to decrypt latitude: {e}")
            result['latitude'] = None
        
        try:
            if self.gps_longitude_encrypted:
                result['longitude'] = float(enc.decrypt(self.gps_longitude_encrypted.encode()).decode())
        except Exception as e:
            logger.warning(f"Failed to decrypt longitude: {e}")
            result['longitude'] = None
        
        return result


class Camera(Base):
    """Camera model for video sources."""
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    rtsp_url = Column(String(500), nullable=False)
    room = Column(String(100))
    
    # Configuration
    fps = Column(Integer, default=30)
    resolution_width = Column(Integer, default=1920)
    resolution_height = Column(Integer, default=1080)
    
    # Detection zones (JSON polygon coordinates)
    detection_zones = Column(JSON)
    
    # Status
    status = Column(SQLEnum(CameraStatus), default=CameraStatus.ACTIVE, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime)
    
    # Relationships
    fall_events = relationship("FallEvent", back_populates="camera", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_camera_status', 'status'),
        Index('idx_camera_active', 'is_active'),
    )


class FallEvent(Base):
    """Fall event model with physical data."""
    __tablename__ = "fall_events"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    
    # Detection timestamps
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    confirmed_at = Column(DateTime)
    
    # Gravity assessment
    gravity_score = Column(Float)  # 0-100
    gravity_level = Column(SQLEnum(GravityLevel), index=True)
    
    # Physical measurements
    impact_velocity = Column(Float)  # m/s
    trunk_angle_at_impact = Column(Float)  # degrees
    time_on_ground = Column(Float)  # seconds
    max_acceleration = Column(Float)  # m/s²
    vertical_velocity = Column(Float)  # m/s
    
    # Additional detection data
    detection_confidence = Column(Float)  # 0-1
    detection_method = Column(String(50))  # yolo, mediapipe, hybrid
    
    # File paths
    skeleton_video_path = Column(String(500))  # Anonymized video
    encrypted_video_path = Column(String(500))  # Encrypted raw video
    thumbnail_path = Column(String(500))
    
    # Status
    status = Column(SQLEnum(FallStatus), default=FallStatus.DETECTED, index=True)
    is_false_positive = Column(Boolean, default=False, index=True)
    confirmed_by = Column(String(200))  # Who confirmed/rejected
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    person = relationship("Person", back_populates="fall_events")
    camera = relationship("Camera", back_populates="fall_events")
    alerts = relationship("Alert", back_populates="fall_event", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_fall_detected_at', 'detected_at'),
        Index('idx_fall_person', 'person_id'),
        Index('idx_fall_camera', 'camera_id'),
        Index('idx_fall_status', 'status'),
        Index('idx_fall_false_positive', 'is_false_positive'),
    )


class Alert(Base):
    """Alert model for notifications."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    fall_event_id = Column(Integer, ForeignKey("fall_events.id"), nullable=False)
    
    # Notification details
    channel = Column(SQLEnum(AlertChannel), nullable=False, index=True)
    recipient = Column(String(200), nullable=False)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.PENDING, index=True)
    
    # Message content
    subject = Column(String(200))
    message_content = Column(Text)
    
    # Delivery tracking
    sent_at = Column(DateTime, index=True)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)
    delivery_time_ms = Column(Integer)  # Delivery latency
    error_message = Column(Text)
    
    # Retry tracking
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fall_event = relationship("FallEvent", back_populates="alerts")
    
    # Indexes
    __table_args__ = (
        Index('idx_alert_fall_event', 'fall_event_id'),
        Index('idx_alert_status', 'status'),
        Index('idx_alert_channel', 'channel'),
        Index('idx_alert_sent_at', 'sent_at'),
    )


class AuditLog(Base):
    """Audit log for security and compliance."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User info
    user_id = Column(Integer, ForeignKey("users.id"))
    username = Column(String(100))
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(200))
    resource_id = Column(Integer)
    
    # Request info
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    session_id = Column(String(100))
    
    # Result
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Integrity
    previous_hash = Column(String(64))  # Chain hash for integrity
    current_hash = Column(String(64))
    
    # Additional data
    details = Column(JSON)
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_resource', 'resource'),
    )


class SystemMetric(Base):
    """System metrics for monitoring and analytics."""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metric identification
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50))  # gauge, counter, histogram
    
    # Value
    metric_value = Column(Float, nullable=False)
    unit = Column(String(50))
    
    # Labels/Tags
    labels = Column(JSON)  # {"camera_id": 1, "model": "yolo11n"}
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_metric_name', 'metric_name'),
        Index('idx_metric_timestamp', 'timestamp'),
    )
