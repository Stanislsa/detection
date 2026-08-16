"""
Person management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from backend.api.dependencies import get_db, get_current_user, require_permission
from backend.database.crud import get_person, get_persons, create_person, update_person, delete_person
from backend.database.models import Person, User
from backend.core.constants import ProfileType, Gender

router = APIRouter()


# Pydantic schemas
class PersonBase(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    profile_type: ProfileType = ProfileType.SENIOR_AUTONOME
    mobility_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    address: Optional[str] = None


class PersonCreate(PersonBase):
    emergency_contact_phone: Optional[str] = None
    emergency_contact_email: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None


class PersonUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    profile_type: Optional[ProfileType] = None
    mobility_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_email: Optional[str] = None
    address: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None


class PersonResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    profile_type: ProfileType
    mobility_notes: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PersonResponse])
async def list_persons(
    skip: int = 0,
    limit: int = 100,
    profile_type: Optional[ProfileType] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all monitored persons."""
    persons = get_persons(db, skip=skip, limit=limit, profile_type=profile_type)
    return persons


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person_endpoint(
    person_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get person by ID."""
    person = get_person(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return person


@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person_endpoint(
    person_data: PersonCreate,
    current_user: User = Depends(require_permission("write_person")),
    db: Session = Depends(get_db)
):
    """Create new monitored person."""
    person_dict = person_data.model_dump()
    
    # Extract sensitive data for encryption
    phone = person_dict.pop("emergency_contact_phone", None)
    email = person_dict.pop("emergency_contact_email", None)
    latitude = person_dict.pop("gps_latitude", None)
    longitude = person_dict.pop("gps_longitude", None)
    
    # Create person
    person = create_person(db, person_dict)
    
    # Encrypt sensitive data
    if phone or email or latitude is not None or longitude is not None:
        person.encrypt_sensitive_data(phone, email, latitude, longitude)
        db.commit()
        db.refresh(person)
    
    return person


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person_endpoint(
    person_id: int,
    person_data: PersonUpdate,
    current_user: User = Depends(require_permission("write_person")),
    db: Session = Depends(get_db)
):
    """Update monitored person."""
    person = get_person(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    update_dict = person_data.model_dump(exclude_unset=True)
    
    # Handle sensitive data encryption
    phone = update_dict.pop("emergency_contact_phone", None)
    email = update_dict.pop("emergency_contact_email", None)
    latitude = update_dict.pop("gps_latitude", None)
    longitude = update_dict.pop("gps_longitude", None)
    
    # Update regular fields
    person = update_person(db, person_id, update_dict)
    
    # Encrypt sensitive data if provided
    if phone or email or latitude is not None or longitude is not None:
        person.encrypt_sensitive_data(phone, email, latitude, longitude)
        db.commit()
        db.refresh(person)
    
    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person_endpoint(
    person_id: int,
    current_user: User = Depends(require_permission("delete_person")),
    db: Session = Depends(get_db)
):
    """Delete monitored person (soft delete)."""
    success = delete_person(db, person_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return None


@router.get("/{person_id}/sensitive-data")
async def get_sensitive_data(
    person_id: int,
    current_user: User = Depends(require_permission("read_person")),
    db: Session = Depends(get_db)
):
    """Get decrypted sensitive data for a person."""
    person = get_person(db, person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    sensitive_data = person.decrypt_sensitive_data()
    return sensitive_data
