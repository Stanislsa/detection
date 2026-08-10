"""
Schémas Pydantic pour les personnes surveillées.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import date, datetime


class PersonBase(BaseModel):
    """Champs communs."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    birth_date: Optional[date] = None
    gender: Optional[Literal["male", "female"]] = None
    height_cm: Optional[float] = Field(None, gt=50, lt=300)
    weight_kg: Optional[float] = Field(None, gt=10, lt=500)
    profile_type: Literal["senior_fragile", "senior_autonome", "adulte", "handicape"] = "senior_autonome"
    mobility_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_email: Optional[str] = None
    address: Optional[str] = None
    gps_latitude: Optional[float] = Field(None, ge=-90, le=90)
    gps_longitude: Optional[float] = Field(None, ge=-180, le=180)


class PersonCreate(PersonBase):
    """Création d'une personne."""
    pass


class PersonUpdate(BaseModel):
    """Mise à jour partielle."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    height_cm: Optional[float] = Field(None, gt=50, lt=300)
    weight_kg: Optional[float] = Field(None, gt=10, lt=500)
    profile_type: Optional[Literal["senior_fragile", "senior_autonome", "adulte", "handicape"]] = None
    is_active: Optional[int] = None


class PersonRead(PersonBase):
    """Lecture avec métadonnées."""
    id: int
    age: int = 0
    full_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: int = 1
    
    class Config:
        from_attributes = True
    
    @validator("age", always=True)
    def compute_age(cls, v, values):
        """Calcule l'âge à partir de la date de naissance."""
        birth = values.get("birth_date")
        if birth:
            today = datetime.today()
            return today.year - birth.year - (
                (today.month, today.day) < (birth.month, birth.day)
            )
        return 0
