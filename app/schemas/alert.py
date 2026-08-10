"""
Schémas Pydantic pour les alertes.
"""

from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class AlertBase(BaseModel):
    fall_event_id: int
    channel: Literal["telegram", "email"]
    recipient: str


class AlertRead(AlertBase):
    id: int
    sent_at: datetime
    status: str  # pending, sent, delivered, failed
    delivery_time_ms: Optional[int] = None
    
    class Config:
        from_attributes = True
