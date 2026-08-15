"""
Fall detection service - Business logic for fall event management.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.core.logger import get_logger
from backend.core.constants import GravityLevel, FallStatus
from backend.database.crud import (
    get_fall_event, get_fall_events, create_fall_event, 
    update_fall_event, confirm_fall_event
)
from backend.ai.manager import ai_manager
from backend.notifications.manager import notification_manager

logger = get_logger(__name__)


class FallService:
    """
    Service for fall detection and event management.
    
    Coordinates between AI detection, database, and notifications.
    """
    
    def __init__(self):
        """Initialize fall service."""
        self.ai_manager = ai_manager
        self.notification_manager = notification_manager
    
    async def detect_and_process_fall(
        self,
        image,
        person_id: int,
        camera_id: int,
        person_profile: Optional[Dict] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Detect fall and process event.
        
        Args:
            image: Input image
            person_id: Person ID
            camera_id: Camera ID
            person_profile: Person profile
            db: Database session
        
        Returns:
            Fall event result
        """
        try:
            # Perform fall detection
            detection_result = self.ai_manager.detect_fall(image, person_profile)
            
            if not detection_result.get("fall_detected"):
                return {
                    "fall_detected": False,
                    "confidence": detection_result.get("confidence", 0.0)
                }
            
            # Create fall event record
            fall_event_data = {
                "person_id": person_id,
                "camera_id": camera_id,
                "detected_at": datetime.utcnow(),
                "gravity_score": detection_result.get("confidence", 0.0) * 100,
                "gravity_level": self._determine_gravity_level(detection_result),
                "vertical_velocity": detection_result.get("vertical_velocity", 0.0),
                "trunk_angle_at_impact": detection_result.get("trunk_angle", 0.0),
                "detection_confidence": detection_result.get("confidence", 0.0),
                "detection_method": detection_result.get("method", "hybrid"),
                "status": FallStatus.DETECTED
            }
            
            if db:
                fall_event = create_fall_event(db, fall_event_data)
                logger.info(f"Fall event created: {fall_event.id}")
                
                # Trigger notifications
                await self._trigger_notifications(fall_event, person_profile, db)
                
                return {
                    "fall_detected": True,
                    "fall_event_id": fall_event.id,
                    "confidence": detection_result.get("confidence", 0.0),
                    "gravity_level": fall_event.gravity_level.value if fall_event.gravity_level else "unknown"
                }
            
            return {
                "fall_detected": True,
                "confidence": detection_result.get("confidence", 0.0),
                "gravity_level": fall_event_data["gravity_level"].value if fall_event_data.get("gravity_level") else "unknown"
            }
            
        except Exception as e:
            logger.error(f"Fall detection failed: {e}")
            return {
                "fall_detected": False,
                "error": str(e)
            }
    
    def _determine_gravity_level(self, detection_result: Dict[str, Any]) -> Optional[GravityLevel]:
        """
        Determine gravity level from detection result.
        
        Args:
            detection_result: Detection result
        
        Returns:
            Gravity level
        """
        confidence = detection_result.get("confidence", 0.0)
        
        # Check for scientific decision
        if "scientific_decision" in detection_result:
            scientific = detection_result["scientific_decision"]
            if "severity" in scientific:
                return scientific["severity"].get("gravity_level")
        
        # Fallback to confidence-based determination
        if confidence > 0.9:
            return GravityLevel.CRITIQUE
        elif confidence > 0.75:
            return GravityLevel.ELEVEE
        elif confidence > 0.6:
            return GravityLevel.MOYENNE
        else:
            return GravityLevel.FAIBLE
    
    async def _trigger_notifications(
        self,
        fall_event,
        person_profile: Optional[Dict],
        db: Session
    ):
        """
        Trigger notifications for fall event.
        
        Args:
            fall_event: Fall event model
            person_profile: Person profile
            db: Database session
        """
        try:
            # Get person details
            from backend.database.crud import get_person
            person = get_person(db, fall_event.person_id)
            
            if not person:
                logger.warning(f"Person not found for fall event: {fall_event.id}")
                return
            
            # Decrypt sensitive data for notification
            sensitive_data = person.decrypt_sensitive_data()
            
            # Send notifications
            await self.notification_manager.send_fall_alert(
                person_name=f"{person.first_name} {person.last_name}",
                gravity_level=fall_event.gravity_level or GravityLevel.MOYENNE,
                gravity_score=fall_event.gravity_score or 0.0,
                location=person.address,
                gps_coords=(
                    sensitive_data.get("latitude"),
                    sensitive_data.get("longitude")
                ) if sensitive_data.get("latitude") else None
            )
            
            logger.info(f"Notifications sent for fall event: {fall_event.id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger notifications: {e}")
    
    def get_fall_statistics(
        self,
        db: Session,
        person_id: Optional[int] = None,
        camera_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get fall statistics.
        
        Args:
            db: Database session
            person_id: Filter by person
            camera_id: Filter by camera
            days: Number of days to analyze
        
        Returns:
            Statistics dictionary
        """
        from datetime import timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        falls = get_fall_events(
            db, skip=0, limit=10000,
            person_id=person_id, camera_id=camera_id,
            start_date=start_date, end_date=end_date
        )
        
        total = len(falls)
        true_positives = sum(1 for f in falls if not f.is_false_positive)
        false_positives = sum(1 for f in falls if f.is_false_positive)
        
        # Gravity distribution
        gravity_dist = {}
        for fall in falls:
            if fall.gravity_level:
                level = fall.gravity_level.value
                gravity_dist[level] = gravity_dist.get(level, 0) + 1
        
        return {
            "period_days": days,
            "total_falls": total,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_positive_rate": false_positives / total if total > 0 else 0.0,
            "gravity_distribution": gravity_dist
        }


# Global fall service instance
fall_service = FallService()
