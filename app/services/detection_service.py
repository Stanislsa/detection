"""
Service de détection de chute.

Orchestration de la détection temps réel.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import cv2

from app.core import DecisionTree, PoseEstimator, PoseLandmarks
from app.models import Person, Camera, FallEvent
from app.schemas import FallEventCreate


class DetectionService:
    """Service pour la détection de chute en temps réel."""
    
    def __init__(self, db, profile_type: str = "senior_autonome", fps: float = 30.0):
        """
        Initialise le service de détection.
        
        Args:
            db: Session de base de données
            profile_type: Type de profil utilisateur
            fps: Frames par seconde
        """
        self.db = db
        self.decision_tree = DecisionTree(profile_type=profile_type, fps=fps)
        self.pose_estimator = PoseEstimator()
        self.active_cameras: Dict[int, cv2.VideoCapture] = {}
    
    def process_frame(self, camera_id: int, frame, person_id: int) -> Dict[str, Any]:
        """
        Traite une frame vidéo pour la détection de chute.
        
        Args:
            camera_id: ID de la caméra
            frame: Frame OpenCV
            person_id: ID de la personne
        
        Returns:
            Résultat de la détection
        """
        # Estimer la posture
        pose_landmarks = self.pose_estimator.process_frame(frame)
        
        if not pose_landmarks:
            return {"status": "no_person_detected"}
        
        # Récupérer le contexte de la personne
        person = self.db.query(Person).filter(Person.id == person_id).first()
        context = {
            "age": self._calculate_age(person.birth_date) if person and person.birth_date else None,
            "profile_type": person.profile_type.value if person else None
        }
        
        # Traiter avec l'arbre de décision
        result = self.decision_tree.process_frame(pose_landmarks, context)
        
        # Si chute confirmée, créer l'événement en base de données
        if result["fall_detection"].status.value == "confirmed":
            self._create_fall_event(
                person_id=person_id,
                camera_id=camera_id,
                physics_state=result["physics_state"],
                gravity_result=result["gravity_assessment"]
            )
        
        return result
    
    def start_camera_stream(self, camera_id: int, rtsp_url: str):
        """
        Démarre le flux d'une caméra.
        
        Args:
            camera_id: ID de la caméra
            rtsp_url: URL RTSP
        """
        cap = cv2.VideoCapture(rtsp_url)
        if cap.isOpened():
            self.active_cameras[camera_id] = cap
            return True
        return False
    
    def stop_camera_stream(self, camera_id: int):
        """
        Arrête le flux d'une caméra.
        
        Args:
            camera_id: ID de la caméra
        """
        if camera_id in self.active_cameras:
            self.active_cameras[camera_id].release()
            del self.active_cameras[camera_id]
    
    def _calculate_age(self, birth_date: datetime) -> Optional[int]:
        """
        Calcule l'âge à partir de la date de naissance.
        
        Args:
            birth_date: Date de naissance
        
        Returns:
            Âge en années
        """
        if not birth_date:
            return None
        
        today = datetime.utcnow()
        age = today.year - birth_date.year
        
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        
        return age
    
    def _create_fall_event(
        self,
        person_id: int,
        camera_id: int,
        physics_state,
        gravity_result
    ):
        """
        Crée un événement de chute en base de données.
        
        Args:
            person_id: ID de la personne
            camera_id: ID de la caméra
            physics_state: État physique
            gravity_result: Résultat de gravité
        """
        from app.core import GravityLevel
        
        fall_event_data = FallEventCreate(
            person_id=person_id,
            camera_id=camera_id,
            gravity_score=gravity_result.score if gravity_result else None,
            gravity_level=GravityLevel[gravity_result.level.value.upper()] if gravity_result else None,
            impact_velocity=abs(physics_state.vertical_velocity),
            trunk_angle_at_impact=physics_state.trunk_angle,
            time_on_ground=0.0,  # À mettre à jour avec le temps réel
            max_acceleration=physics_state.resultant_acceleration
        )
        
        fall_event = FallEvent(**fall_event_data.model_dump())
        self.db.add(fall_event)
        self.db.commit()
        self.db.refresh(fall_event)
        
        return fall_event
    
    def reset(self):
        """Réinitialise le détecteur."""
        self.decision_tree.reset()
    
    def set_profile(self, profile_type: str):
        """
        Change le profil utilisateur.
        
        Args:
            profile_type: Nouveau type de profil
        """
        self.decision_tree.set_profile(profile_type)
    
    def cleanup(self):
        """Nettoie les ressources."""
        for camera_id, cap in self.active_cameras.items():
            cap.release()
        self.active_cameras.clear()
        self.pose_estimator.close()
