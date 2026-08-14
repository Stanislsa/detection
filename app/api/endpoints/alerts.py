"""
Router pour la gestion des alertes.

Historique des alertes, confirmation/infirmation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app import schemas
from app.dependencies import get_db
from app import crud

router = APIRouter()


@router.get("/", response_model=List[schemas.Alert])
async def get_alerts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique de toutes les alertes.
    
    Args:
        skip: Nombre d'éléments à sauter (pagination)
        limit: Nombre maximum d'éléments à retourner
        db: Session de base de données
    
    Returns:
        Liste des alertes
    """
    alerts = crud.get_alerts(db, skip=skip, limit=limit)
    return alerts


@router.get("/{alert_id}", response_model=schemas.Alert)
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """
    Récupère une alerte par son ID.
    
    Args:
        alert_id: ID de l'alerte
        db: Session de base de données
    
    Returns:
        Alerte demandée
    
    Raises:
        HTTPException: Si l'alerte n'existe pas
    """
    alert = crud.get_alert(db, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return alert


@router.get("/fall-event/{fall_event_id}", response_model=List[schemas.Alert])
async def get_alerts_by_fall_event(fall_event_id: int, db: Session = Depends(get_db)):
    """
    Récupère toutes les alertes associées à un événement de chute.
    
    Args:
        fall_event_id: ID de l'événement de chute
        db: Session de base de données
    
    Returns:
        Liste des alertes pour l'événement
    """
    alerts = crud.get_alerts_by_fall_event(db, fall_event_id)
    return alerts


@router.post("/", response_model=schemas.Alert, status_code=status.HTTP_201_CREATED)
async def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    """
    Crée une nouvelle alerte.
    
    Args:
        alert: Données de l'alerte à créer
        db: Session de base de données
    
    Returns:
        Alerte créée
    """
    return crud.create_alert(db, alert)


@router.put("/{alert_id}", response_model=schemas.Alert)
async def update_alert(
    alert_id: int,
    alert: schemas.AlertUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour une alerte (statut de livraison, etc.).
    
    Args:
        alert_id: ID de l'alerte
        alert: Nouvelles données de l'alerte
        db: Session de base de données
    
    Returns:
        Alerte mise à jour
    
    Raises:
        HTTPException: Si l'alerte n'existe pas
    """
    updated_alert = crud.update_alert(db, alert_id, alert)
    if updated_alert is None:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return updated_alert


@router.post("/fall-event/{fall_event_id}/confirm")
async def confirm_fall_event(
    fall_event_id: int,
    confirmed: bool = True,
    notes: str = None,
    confirmed_by: str = None,
    db: Session = Depends(get_db)
):
    """
    Confirme ou infirme un événement de chute.
    
    Args:
        fall_event_id: ID de l'événement de chute
        confirmed: True pour confirmer, False pour infirmer (faux positif)
        notes: Notes additionnelles
        confirmed_by: Identifiant de la personne qui confirme
        db: Session de base de données
    
    Returns:
        Événement de chute mis à jour
    
    Raises:
        HTTPException: Si l'événement n'existe pas
    """
    fall_event = crud.get_fall_event(db, fall_event_id)
    if fall_event is None:
        raise HTTPException(status_code=404, detail="Événement de chute non trouvé")
    
    # Mettre à jour l'événement
    update_data = {
        "is_false_positive": not confirmed,
        "confirmed_at": datetime.utcnow(),
        "confirmed_by": confirmed_by
    }
    
    if notes:
        update_data["notes"] = notes
    
    updated_fall = crud.update_fall_event(
        db, 
        fall_event_id, 
        schemas.FallEventUpdate(**update_data)
    )
    
    return {
        "status": "confirmed" if confirmed else "rejected",
        "fall_event_id": fall_event_id,
        "message": "Événement " + ("confirmé" if confirmed else "rejeté comme faux positif")
    }
