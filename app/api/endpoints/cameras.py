"""
Endpoints pour la gestion des caméras IP.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.base import get_db
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraRead, CameraUpdate

router = APIRouter()


@router.post("/", response_model=CameraRead, status_code=status.HTTP_201_CREATED)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    """Ajoute une nouvelle caméra."""
    db_camera = Camera(**camera.dict())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.get("/", response_model=List[CameraRead])
def list_cameras(db: Session = Depends(get_db)):
    """Liste les caméras."""
    return db.query(Camera).all()


@router.get("/{camera_id}", response_model=CameraRead)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """Récupère une caméra."""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    return camera


@router.put("/{camera_id}", response_model=CameraRead)
def update_camera(camera_id: int, camera_update: CameraUpdate, db: Session = Depends(get_db)):
    """Met à jour une caméra."""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    for field, value in camera_update.dict(exclude_unset=True).items():
        setattr(camera, field, value)
    
    db.commit()
    db.refresh(camera)
    return camera
