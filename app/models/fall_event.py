"""
Modèle FallEvent - Événement de chute.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base, GravityLevel


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
