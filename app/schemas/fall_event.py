"""
Schémas Pydantic pour les événements de chute.
"""

from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class FallEventBase(BaseModel):
    person_id: int
    camera_id: int
    gravity_level: Optional[Literal["faible", "moyenne", "elevee", "critique"]] = None
    gravity_score: Optional[float] = None


class FallEventCreate(FallEventBase):
    """Création d'un événement de chute."""
    pass


class FallEventUpdate(BaseModel):
    """Mise à jour partielle d'un événement de chute."""
    confirmed_at: Optional[datetime] = None
    is_false_positive: Optional[bool] = None
    confirmed_by: Optional[str] = None
    notes: Optional[str] = None


class FallEventRead(FallEventBase):
    id: int
    detected_at: datetime
    confirmed_at: Optional[datetime] = None
    alert_sent_at: Optional[datetime] = None

    # Données physiques
    impact_velocity: Optional[float] = None
    max_acceleration: Optional[float] = None
    trunk_angle_at_impact: Optional[float] = None
    time_on_ground: Optional[float] = None
    time_to_detection_ms: Optional[int] = None

    # Statut
    is_false_positive: bool = False

    class Config:
        from_attributes = True
