"""
Schémas Pydantic pour les caméras.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class CameraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    rtsp_url: str = Field(..., min_length=10, max_length=500)
    room: Optional[str] = Field(None, max_length=100)
    fps: int = Field(default=30, ge=1, le=120)
    resolution_width: int = Field(default=1920, ge=320, le=3840)
    resolution_height: int = Field(default=1080, ge=240, le=2160)


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    room: Optional[str] = None
    is_active: Optional[bool] = None


class CameraRead(CameraBase):
    id: int
    is_active: bool
    is_connected: bool
    last_seen: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
