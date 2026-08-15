"""
Person service - Business logic for person management.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.core.logger import get_logger
from backend.core.constants import ProfileType
from backend.database.crud import (
    get_person, get_persons, create_person, update_person, delete_person
)

logger = get_logger(__name__)


class PersonService:
    """
    Service for person management and profile handling.
    """
    
    def __init__(self):
        """Initialize person service."""
        pass
    
    def get_person_with_profile(self, person_id: int, db: Session) -> Dict[str, Any]:
        """
        Get person with full profile details.
        
        Args:
            person_id: Person ID
            db: Database session
        
        Returns:
            Person with profile
        """
        person = get_person(db, person_id)
        if not person:
            return {"error": "Person not found"}
        
        # Get profile configuration
        profile_config = self._get_profile_config(person.profile_type)
        
        # Get sensitive data (decrypted)
        sensitive_data = person.decrypt_sensitive_data()
        
        return {
            "id": person.id,
            "first_name": person.first_name,
            "last_name": person.last_name,
            "birth_date": person.birth_date.isoformat() if person.birth_date else None,
            "gender": person.gender.value if person.gender else None,
            "height": person.height,
            "weight": person.weight,
            "profile_type": person.profile_type.value if person.profile_type else None,
            "profile_config": profile_config,
            "mobility_notes": person.mobility_notes,
            "emergency_contact_name": person.emergency_contact_name,
            "sensitive_data": sensitive_data,
            "address": person.address,
            "is_active": person.is_active,
            "created_at": person.created_at.isoformat(),
            "updated_at": person.updated_at.isoformat()
        }
    
    def _get_profile_config(self, profile_type: Optional[ProfileType]) -> Dict[str, Any]:
        """
        Get profile configuration.
        
        Args:
            profile_type: Profile type
        
        Returns:
            Profile configuration
        """
        from backend.core.constants import PROFILE_CONFIG
        
        if profile_type:
            return PROFILE_CONFIG.get(profile_type, {})
        return {}
    
    def create_person_with_encryption(
        self,
        person_data: Dict[str, Any],
        sensitive_data: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Create person with encrypted sensitive data.
        
        Args:
            person_data: Regular person data
            sensitive_data: Sensitive data to encrypt
            db: Database session
        
        Returns:
            Created person
        """
        try:
            # Create person
            person = create_person(db, person_data)
            
            # Encrypt sensitive data
            if sensitive_data:
                person.encrypt_sensitive_data(
                    phone=sensitive_data.get("phone"),
                    email=sensitive_data.get("email"),
                    latitude=sensitive_data.get("latitude"),
                    longitude=sensitive_data.get("longitude")
                )
                db.commit()
                db.refresh(person)
            
            return {
                "success": True,
                "person_id": person.id,
                "profile_type": person.profile_type.value if person.profile_type else None
            }
            
        except Exception as e:
            logger.error(f"Failed to create person: {e}")
            return {"error": str(e)}
    
    def update_person_profile(
        self,
        person_id: int,
        profile_type: ProfileType,
        db: Session
    ) -> Dict[str, Any]:
        """
        Update person profile type.
        
        Args:
            person_id: Person ID
            profile_type: New profile type
            db: Database session
        
        Returns:
            Updated person
        """
        person = update_person(db, person_id, {"profile_type": profile_type})
        
        if not person:
            return {"error": "Person not found"}
        
        return {
            "success": True,
            "person_id": person.id,
            "profile_type": person.profile_type.value
        }
    
    def get_person_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get person statistics.
        
        Args:
            db: Database session
        
        Returns:
            Statistics dictionary
        """
        persons = get_persons(db, skip=0, limit=10000)
        
        # Profile distribution
        profile_dist = {}
        for person in persons:
            if person.profile_type:
                profile = person.profile_type.value
                profile_dist[profile] = profile_dist.get(profile, 0) + 1
        
        # Gender distribution
        gender_dist = {}
        for person in persons:
            if person.gender:
                gender = person.gender.value
                gender_dist[gender] = gender_dist.get(gender, 0) + 1
        
        return {
            "total_persons": len(persons),
            "active_persons": sum(1 for p in persons if p.is_active),
            "profile_distribution": profile_dist,
            "gender_distribution": gender_dist
        }


# Global person service instance
person_service = PersonService()
