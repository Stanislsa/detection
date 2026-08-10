"""
Router pour la gestion des caméras.

CRUD caméras, test de connexion RTSP.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import crud, schemas, models
from backend.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Camera])
async def get_cameras(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Récupère la liste de toutes les caméras.
    
    Args:
        skip: Nombre d'éléments à sauter (pagination)
        limit: Nombre maximum d'éléments à retourner
        db: Session de base de données
    
    Returns:
        Liste des caméras
    """
    cameras = crud.get_cameras(db, skip=skip, limit=limit)
    return cameras


@router.get("/active", response_model=List[schemas.Camera])
async def get_active_cameras(db: Session = Depends(get_db)):
    """
    Récupère uniquement les caméras actives.
    
    Args:
        db: Session de base de données
    
    Returns:
        Liste des caméras actives
    """
    cameras = crud.get_active_cameras(db)
    return cameras


@router.get("/{camera_id}", response_model=schemas.Camera)
async def get_camera(camera_id: int, db: Session = Depends(get_db)):
    """
    Récupère une caméra par son ID.
    
    Args:
        camera_id: ID de la caméra
        db: Session de base de données
    
    Returns:
        Caméra demandée
    
    Raises:
        HTTPException: Si la caméra n'existe pas
    """
    camera = crud.get_camera(db, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    return camera


@router.post("/", response_model=schemas.Camera, status_code=status.HTTP_201_CREATED)
async def create_camera(camera: schemas.CameraCreate, db: Session = Depends(get_db)):
    """
    Crée une nouvelle caméra.
    
    Args:
        camera: Données de la caméra à créer
        db: Session de base de données
    
    Returns:
        Caméra créée
    """
    return crud.create_camera(db, camera)


@router.put("/{camera_id}", response_model=schemas.Camera)
async def update_camera(
    camera_id: int,
    camera: schemas.CameraUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour une caméra.
    
    Args:
        camera_id: ID de la caméra
        camera: Nouvelles données de la caméra
        db: Session de base de données
    
    Returns:
        Caméra mise à jour
    
    Raises:
        HTTPException: Si la caméra n'existe pas
    """
    updated_camera = crud.update_camera(db, camera_id, camera)
    if updated_camera is None:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    return updated_camera


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    """
    Supprime une caméra.
    
    Args:
        camera_id: ID de la caméra
        db: Session de base de données
    
    Raises:
        HTTPException: Si la caméra n'existe pas
    """
    success = crud.delete_camera(db, camera_id)
    if not success:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")


@router.post("/{camera_id}/test")
async def test_camera_connection(camera_id: int, db: Session = Depends(get_db)):
    """
    Teste la connexion RTSP d'une caméra.
    
    Args:
        camera_id: ID de la caméra
        db: Session de base de données
    
    Returns:
        Résultat du test de connexion
    
    Raises:
        HTTPException: Si la caméra n'existe pas
    """
    camera = crud.get_camera(db, camera_id)
    if camera is None:
        raise HTTPException(status_code=404, detail="Caméra non trouvée")
    
    # Note: Implémentation du test RTSP à faire avec OpenCV
    # cap = cv2.VideoCapture(camera.rtsp_url)
    # if cap.isOpened():
    #     cap.release()
    #     return {"status": "success", "message": "Connexion réussie"}
    # else:
    #     return {"status": "failed", "message": "Connexion échouée"}
    
    return {
        "status": "pending",
        "message": "Test de connexion RTSP à implémenter avec OpenCV",
        "rtsp_url": camera.rtsp_url
    }
