"""
Camera service - Business logic for camera management.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.core.logger import get_logger
from backend.core.constants import CameraStatus
from backend.database.crud import (
    get_camera, get_cameras, get_active_cameras,
    create_camera, update_camera, delete_camera, update_camera_last_seen
)

logger = get_logger(__name__)


class CameraService:
    """
    Service for camera management and monitoring.
    """
    
    def __init__(self):
        """Initialize camera service."""
        pass
    
    def get_camera_status(self, camera_id: int, db: Session) -> Dict[str, Any]:
        """
        Get detailed camera status.
        
        Args:
            camera_id: Camera ID
            db: Database session
        
        Returns:
            Camera status dictionary
        """
        camera = get_camera(db, camera_id)
        if not camera:
            return {"error": "Camera not found"}
        
        # Calculate uptime
        if camera.last_seen:
            uptime = datetime.utcnow() - camera.last_seen
            is_online = uptime.total_seconds() < 60  # Online if seen within 60 seconds
        else:
            is_online = False
            uptime = None
        
        return {
            "camera_id": camera.id,
            "name": camera.name,
            "status": camera.status.value,
            "is_active": camera.is_active,
            "is_online": is_online,
            "last_seen": camera.last_seen.isoformat() if camera.last_seen else None,
            "uptime_seconds": uptime.total_seconds() if uptime else None,
            "resolution": f"{camera.resolution_width}x{camera.resolution_height}",
            "fps": camera.fps,
            "detection_zones": camera.detection_zones
        }
    
    def update_heartbeat(self, camera_id: int, db: Session) -> bool:
        """
        Update camera heartbeat.
        
        Args:
            camera_id: Camera ID
            db: Database session
        
        Returns:
            True if successful
        """
        return update_camera_last_seen(db, camera_id)
    
    def get_all_camera_statuses(self, db: Session) -> List[Dict[str, Any]]:
        """
        Get status of all cameras.
        
        Args:
            db: Database session
        
        Returns:
            List of camera statuses
        """
        cameras = get_cameras(db, skip=0, limit=1000)
        
        statuses = []
        for camera in cameras:
            status = self.get_camera_status(camera.id, db)
            statuses.append(status)
        
        return statuses
    
    def check_camera_health(self, db: Session) -> Dict[str, Any]:
        """
        Check health of all cameras.
        
        Args:
            db: Database session
        
        Returns:
            Health summary
        """
        cameras = get_cameras(db, skip=0, limit=1000)
        
        online_count = 0
        offline_count = 0
        error_count = 0
        
        for camera in cameras:
            if camera.status == CameraStatus.ACTIVE:
                if camera.last_seen:
                    uptime = datetime.utcnow() - camera.last_seen
                    if uptime.total_seconds() < 60:
                        online_count += 1
                    else:
                        offline_count += 1
                else:
                    offline_count += 1
            elif camera.status == CameraStatus.ERROR:
                error_count += 1
            else:
                offline_count += 1
        
        return {
            "total_cameras": len(cameras),
            "online": online_count,
            "offline": offline_count,
            "error": error_count,
            "health_percentage": (online_count / len(cameras) * 100) if cameras else 0.0
        }


# Global camera service instance
camera_service = CameraService()
