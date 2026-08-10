"""
Modèle Person - Personne surveillée.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base, Gender, ProfileType


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
    emergency_contact_phone_encrypted = Column(Text)  # Chiffré
    emergency_contact_email_encrypted = Column(Text)  # Chiffré
    address = Column(String(500))
    gps_latitude_encrypted = Column(Text)  # Chiffré
    gps_longitude_encrypted = Column(Text)  # Chiffré
    is_active = Column(Boolean, default=True)  # Soft delete
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    fall_events = relationship("FallEvent", back_populates="person")
    
    def encrypt_sensitive_data(self, phone: str = None, email: str = None, 
                               latitude: float = None, longitude: float = None):
        """Chiffre les données sensibles."""
        from app.security.encryption import EncryptionManager
        from app.config import settings
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
        """Déchiffre et retourne les données sensibles."""
        from app.security.encryption import EncryptionManager
        from app.config import settings
        enc = EncryptionManager(settings.SECRET_KEY)
        
        result = {}
        
        if self.emergency_contact_phone_encrypted:
            try:
                result['phone'] = enc.decrypt(self.emergency_contact_phone_encrypted.encode()).decode()
            except:
                result['phone'] = None
        
        if self.emergency_contact_email_encrypted:
            try:
                result['email'] = enc.decrypt(self.emergency_contact_email_encrypted.encode()).decode()
            except:
                result['email'] = None
        
        if self.gps_latitude_encrypted:
            try:
                result['latitude'] = float(enc.decrypt(self.gps_latitude_encrypted.encode()).decode())
            except:
                result['latitude'] = None
        
        if self.gps_longitude_encrypted:
            try:
                result['longitude'] = float(enc.decrypt(self.gps_longitude_encrypted.encode()).decode())
            except:
                result['longitude'] = None
        
        return result
