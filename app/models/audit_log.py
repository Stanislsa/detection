"""
Modèle AuditLog - Log d'audit.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime

from .base import Base


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
    previous_hash = Column(String(64))  # Hash du log précédent
    current_hash = Column(String(64))  # Hash de ce log (chaînage SHA-256)
    details = Column(Text)
