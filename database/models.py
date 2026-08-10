"""
Modèles de base de données SQLAlchemy.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"

class GravityLevel(enum.Enum):
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"

class ProfileType(enum.Enum):
    SENIOR_FRAGILE = "senior_fragile"
    SENIOR_AUTONOME = "senior_autonome"
    ADULTE = "adulte"
    HANDICAPE = "handicape"

class Person(Base):
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(DateTime)
    gender = Column(SQLEnum(Gender))
    height = Column(Float)  # cm
    weight = Column(Float)  # kg
    profile_type = Column(SQLEnum(ProfileType), default=ProfileType.SENIOR_AUTONOME)
    mobility_notes = Column(Text)
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))
    emergency_contact_email = Column(String(200))
    address = Column(String(500))
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    fall_events = relationship("FallEvent", back_populates="person")

class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    rtsp_url = Column(String(500), nullable=False)
    room = Column(String(100))
    is_active = Column(Boolean, default=True)
    fps = Column(Integer, default=30)
    resolution_width = Column(Integer, default=1920)
    resolution_height = Column(Integer, default=1080)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime)
    
    fall_events = relationship("FallEvent", back_populates="camera")

class FallEvent(Base):
    __tablename__ = "fall_events"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    detected_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)
    gravity_score = Column(Float)
    gravity_level = Column(SQLEnum(GravityLevel))
    
    # Données physiques
    impact_velocity = Column(Float)  # m/s
    trunk_angle_at_impact = Column(Float)  # degrés
    time_on_ground = Column(Float)  # secondes
    max_acceleration = Column(Float)  # m/s²
    
    # Fichiers
    skeleton_video_path = Column(String(500))  # Vidéo anonymisée
    encrypted_video_path = Column(String(500))  # Vidéo brute chiffrée
    thumbnail_path = Column(String(500))
    
    # Statut
    is_false_positive = Column(Boolean, default=False)
    confirmed_by = Column(String(200))  # Qui a confirmé/infirmé
    notes = Column(Text)
    
    person = relationship("Person", back_populates="fall_events")
    camera = relationship("Camera", back_populates="fall_events")
    alerts = relationship("Alert", back_populates="fall_event")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    fall_event_id = Column(Integer, ForeignKey("fall_events.id"))
    sent_at = Column(DateTime, default=datetime.utcnow)
    channel = Column(String(50))  # telegram, email
    recipient = Column(String(200))
    status = Column(String(50))  # sent, delivered, read, failed
    message_content = Column(Text)
    delivery_time_ms = Column(Integer)  # Temps de livraison
    
    fall_event = relationship("FallEvent", back_populates="alerts")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100))
    action = Column(String(100), nullable=False)
    resource = Column(String(200))
    ip_address = Column(String(50))
    success = Column(Boolean)
    session_id = Column(String(100))
    previous_hash = Column(String(64))  # Chaîne de hachage
    details = Column(Text)

class SystemMetric(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_name = Column(String(100))
    metric_value = Column(Float)
    unit = Column(String(50))

# Création de la base de données
def init_db(db_path: str = "data/db/fall_detection.db"):
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine
