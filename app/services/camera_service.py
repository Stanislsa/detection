"""
Service de gestion des caméras.

Gestion des flux RTSP et test de connexion.
"""

from typing import List, Optional
import cv2
from sqlalchemy.orm import Session

from app.models import Camera
from app.schemas import CameraCreate, CameraUpdate


class CameraService:
    """Service pour la gestion des caméras."""
    
    def __init__(self, db: Session):
        """
        Initialise le service.
        
        Args:
            db: Session de base de données
        """
        self.db = db
    
    def get_cameras(self, skip: int = 0, limit: int = 100) -> List[Camera]:
        """
        Récupère la liste des caméras.
        
        Args:
            skip: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments
        
        Returns:
            Liste des caméras
        """
        return self.db.query(Camera).offset(skip).limit(limit).all()
    
    def get_active_cameras(self) -> List[Camera]:
        """
        Récupère les caméras actives.
        
        Returns:
            Liste des caméras actives
        """
        return self.db.query(Camera).filter(Camera.is_active == True).all()
    
    def get_camera(self, camera_id: int) -> Optional[Camera]:
        """
        Récupère une caméra par son ID.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            Caméra ou None
        """
        return self.db.query(Camera).filter(Camera.id == camera_id).first()
    
    def create_camera(self, camera_data: CameraCreate) -> Camera:
        """
        Crée une nouvelle caméra.
        
        Args:
            camera_data: Données de la caméra
        
        Returns:
            Caméra créée
        """
        camera = Camera(**camera_data.model_dump())
        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)
        return camera
    
    def update_camera(self, camera_id: int, camera_data: CameraUpdate) -> Optional[Camera]:
        """
        Met à jour une caméra.
        
        Args:
            camera_id: ID de la caméra
            camera_data: Nouvelles données
        
        Returns:
            Caméra mise à jour ou None
        """
        camera = self.get_camera(camera_id)
        if not camera:
            return None
        
        for field, value in camera_data.model_dump(exclude_unset=True).items():
            setattr(camera, field, value)
        
        self.db.commit()
        self.db.refresh(camera)
        return camera
    
    def delete_camera(self, camera_id: int) -> bool:
        """
        Supprime une caméra.
        
        Args:
            camera_id: ID de la caméra
        
        Returns:
            True si supprimée
        """
        camera = self.get_camera(camera_id)
        if not camera:
            return False
        
        self.db.delete(camera)
        self.db.commit()
        return True
    
    def test_connection(self, rtsp_url: str) -> dict:
        """
        Teste la connexion RTSP d'une caméra.
        
        Args:
            rtsp_url: URL RTSP
        
        Returns:
            Résultat du test
        """
        try:
            cap = cv2.VideoCapture(rtsp_url)
            
            if cap.isOpened():
                cap.release()
                return {
                    "status": "success",
                    "message": "Connexion réussie"
                }
            else:
                return {
                    "status": "failed",
                    "message": "Connexion échouée"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def update_last_seen(self, camera_id: int):
        """
        Met à jour le timestamp last_seen d'une caméra.
        
        Args:
            camera_id: ID de la caméra
        """
        from datetime import datetime
        
        camera = self.get_camera(camera_id)
        if camera:
            camera.last_seen = datetime.utcnow()
            self.db.commit()
