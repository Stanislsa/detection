"""
Modèle Alert - Alerte envoyée.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


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
