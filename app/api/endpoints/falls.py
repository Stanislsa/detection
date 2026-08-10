"""
Endpoints pour l'historique des chutes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.base import get_db
from app.models.fall_event import FallEvent, GravityLevel

router = APIRouter()


@router.get("/")
def list_falls(
    person_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    gravity_level: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Liste les événements de chute avec filtres."""
    query = db.query(FallEvent)
    
    if person_id:
        query = query.filter(FallEvent.person_id == person_id)
    if camera_id:
        query = query.filter(FallEvent.camera_id == camera_id)
    if gravity_level:
        query = query.filter(FallEvent.gravity_level == gravity_level)
    if start_date:
        query = query.filter(FallEvent.detected_at >= start_date)
    if end_date:
        query = query.filter(FallEvent.detected_at <= end_date)
    
    return query.order_by(FallEvent.detected_at.desc()).all()


@router.get("/{fall_id}")
def get_fall(fall_id: int, db: Session = Depends(get_db)):
    """Récupère un événement de chute."""
    fall = db.query(FallEvent).filter(FallEvent.id == fall_id).first()
    if not fall:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    return fall


@router.post("/{fall_id}/feedback")
def feedback_fall(
    fall_id: int,
    is_false_positive: bool,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Fournit un feedback sur une chute (vrai/faux positif)."""
    fall = db.query(FallEvent).filter(FallEvent.id == fall_id).first()
    if not fall:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    fall.is_false_positive = is_false_positive
    if notes:
        fall.notes = notes
    
    db.commit()
    return {"message": "Feedback enregistré"}
