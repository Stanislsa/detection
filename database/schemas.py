"""
Schémas Pydantic pour validation et sérialisation.
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class GravityLevel(str, Enum):
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"

class ProfileType(str, Enum):
    SENIOR_FRAGILE = "senior_fragile"
    SENIOR_AUTONOME = "senior_autonome"
    ADULTE = "adulte"
    HANDICAPE = "handicape"

# Person Schemas
class PersonBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    height: Optional[float] = None  # cm
    weight: Optional[float] = None  # kg
    profile_type: ProfileType = ProfileType.SENIOR_AUTONOME
    mobility_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None

class PersonCreate(PersonBase):
    pass

class PersonUpdate(PersonBase):
    pass

class Person(PersonBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Camera Schemas
class CameraBase(BaseModel):
    name: str = Field(..., max_length=100)
    rtsp_url: str = Field(..., max_length=500)
    room: Optional[str] = Field(None, max_length=100)
    is_active: bool = True
    fps: int = 30
    resolution_width: int = 1920
    resolution_height: int = 1080

class CameraCreate(CameraBase):
    pass

class CameraUpdate(CameraBase):
    pass

class Camera(CameraBase):
    id: int
    created_at: datetime
    last_seen: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# FallEvent Schemas
class FallEventBase(BaseModel):
    person_id: Optional[int] = None
    camera_id: Optional[int] = None
    gravity_score: Optional[float] = None
    gravity_level: Optional[GravityLevel] = None
    impact_velocity: Optional[float] = None  # m/s
    trunk_angle_at_impact: Optional[float] = None  # degrés
    time_on_ground: Optional[float] = None  # secondes
    max_acceleration: Optional[float] = None  # m/s²
    skeleton_video_path: Optional[str] = Field(None, max_length=500)
    encrypted_video_path: Optional[str] = Field(None, max_length=500)
    thumbnail_path: Optional[str] = Field(None, max_length=500)
    is_false_positive: bool = False
    confirmed_by: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

class FallEventCreate(FallEventBase):
    pass

class FallEventUpdate(FallEventBase):
    pass

class FallEvent(FallEventBase):
    id: int
    detected_at: datetime
    confirmed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Alert Schemas
class AlertBase(BaseModel):
    fall_event_id: int
    channel: str = Field(..., max_length=50)  # telegram, email
    recipient: str = Field(..., max_length=200)
    status: str = Field("sent", max_length=50)  # sent, delivered, read, failed
    message_content: Optional[str] = None
    delivery_time_ms: Optional[int] = None

class AlertCreate(AlertBase):
    pass

class AlertUpdate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    sent_at: datetime
    
    class Config:
        from_attributes = True

# AuditLog Schemas
class AuditLogBase(BaseModel):
    user_id: Optional[str] = Field(None, max_length=100)
    action: str = Field(..., max_length=100)
    resource: Optional[str] = Field(None, max_length=200)
    ip_address: Optional[str] = Field(None, max_length=50)
    success: bool = True
    session_id: Optional[str] = Field(None, max_length=100)
    previous_hash: Optional[str] = Field(None, max_length=64)
    details: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# SystemMetric Schemas
class SystemMetricBase(BaseModel):
    metric_name: str = Field(..., max_length=100)
    metric_value: float
    unit: Optional[str] = Field(None, max_length=50)

class SystemMetricCreate(SystemMetricBase):
    pass

class SystemMetric(SystemMetricBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True
