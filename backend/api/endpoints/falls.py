"""
Fall event management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.api.dependencies import get_db, get_current_user, require_permission
from backend.database.crud import (
    get_fall_event, get_fall_events, get_fall_events_by_person, get_fall_events_by_camera,
    create_fall_event, update_fall_event, confirm_fall_event
)
from backend.database.models import FallEvent, User
from backend.core.constants import GravityLevel, FallStatus

router = APIRouter()


# Pydantic schemas
class FallEventBase(BaseModel):
    person_id: int
    camera_id: int
    gravity_score: Optional[float] = None
    gravity_level: Optional[GravityLevel] = None
    impact_velocity: Optional[float] = None
    trunk_angle_at_impact: Optional[float] = None
    time_on_ground: Optional[float] = None
    max_acceleration: Optional[float] = None
    vertical_velocity: Optional[float] = None
    detection_confidence: Optional[float] = None
    detection_method: Optional[str] = None
    skeleton_video_path: Optional[str] = None
    encrypted_video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None


class FallEventCreate(FallEventBase):
    pass


class FallEventUpdate(BaseModel):
    gravity_score: Optional[float] = None
    gravity_level: Optional[GravityLevel] = None
    status: Optional[FallStatus] = None
    notes: Optional[str] = None


class FallEventResponse(BaseModel):
    id: int
    person_id: int
    camera_id: int
    detected_at: datetime
    confirmed_at: Optional[datetime] = None
    gravity_score: Optional[float] = None
    gravity_level: Optional[GravityLevel] = None
    impact_velocity: Optional[float] = None
    trunk_angle_at_impact: Optional[float] = None
    time_on_ground: Optional[float] = None
    max_acceleration: Optional[float] = None
    vertical_velocity: Optional[float] = None
    detection_confidence: Optional[float] = None
    detection_method: Optional[str] = None
    skeleton_video_path: Optional[str] = None
    encrypted_video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    status: FallStatus
    is_false_positive: bool
    confirmed_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[FallEventResponse])
async def list_fall_events(
    skip: int = 0,
    limit: int = 100,
    person_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    gravity_level: Optional[GravityLevel] = None,
    status: Optional[FallStatus] = None,
    is_false_positive: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List fall events with filters."""
    falls = get_fall_events(
        db, skip=skip, limit=limit, person_id=person_id, camera_id=camera_id,
        gravity_level=gravity_level, status=status, is_false_positive=is_false_positive,
        start_date=start_date, end_date=end_date
    )
    return falls


@router.get("/person/{person_id}", response_model=List[FallEventResponse])
async def get_person_fall_events(
    person_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get fall events for a specific person."""
    falls = get_fall_events_by_person(db, person_id, skip=skip, limit=limit)
    return falls


@router.get("/camera/{camera_id}", response_model=List[FallEventResponse])
async def get_camera_fall_events(
    camera_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get fall events for a specific camera."""
    falls = get_fall_events_by_camera(db, camera_id, skip=skip, limit=limit)
    return falls


@router.get("/{fall_id}", response_model=FallEventResponse)
async def get_fall_event_endpoint(
    fall_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get fall event by ID."""
    fall = get_fall_event(db, fall_id)
    if not fall:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fall event not found"
        )
    return fall


@router.post("/", response_model=FallEventResponse, status_code=status.HTTP_201_CREATED)
async def create_fall_event_endpoint(
    fall_data: FallEventCreate,
    current_user: User = Depends(require_permission("write_fall")),
    db: Session = Depends(get_db)
):
    """Create new fall event (typically called by detection system)."""
    fall_dict = fall_data.model_dump()
    fall = create_fall_event(db, fall_dict)
    return fall


@router.put("/{fall_id}", response_model=FallEventResponse)
async def update_fall_event_endpoint(
    fall_id: int,
    fall_data: FallEventUpdate,
    current_user: User = Depends(require_permission("write_fall")),
    db: Session = Depends(get_db)
):
    """Update fall event."""
    update_dict = fall_data.model_dump(exclude_unset=True)
    fall = update_fall_event(db, fall_id, update_dict)
    
    if not fall:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fall event not found"
        )
    return fall


@router.post("/{fall_id}/confirm")
async def confirm_fall_event_endpoint(
    fall_id: int,
    is_false_positive: bool = False,
    notes: Optional[str] = None,
    current_user: User = Depends(require_permission("write_fall")),
    db: Session = Depends(get_db)
):
    """Confirm or reject a fall event."""
    fall = confirm_fall_event(
        db, fall_id, 
        confirmed_by=current_user.username,
        is_false_positive=is_false_positive,
        notes=notes
    )
    
    if not fall:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fall event not found"
        )
    
    return {
        "message": "Fall event confirmed" if not is_false_positive else "Fall event marked as false positive",
        "fall_id": fall.id,
        "status": fall.status.value
    }


@router.delete("/{fall_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fall_event_endpoint(
    fall_id: int,
    current_user: User = Depends(require_permission("delete_fall")),
    db: Session = Depends(get_db)
):
    """Delete fall event."""
    from backend.database.crud import delete_fall_event
    success = delete_fall_event(db, fall_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fall event not found"
        )
    return None
