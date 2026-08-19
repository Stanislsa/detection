"""
Dashboard service - Business logic for dashboard analytics.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.logger import get_logger
from backend.database.crud import (
    get_fall_events, get_alerts, get_persons, get_cameras
)
from backend.database.models import FallEvent, Alert, Camera, Person

logger = get_logger(__name__)


class DashboardService:
    """
    Service for dashboard analytics and KPIs.
    """
    
    def __init__(self):
        """Initialize dashboard service."""
        pass
    
    def get_system_kpis(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get system KPIs.
        
        Args:
            db: Database session
            days: Number of days to analyze
        
        Returns:
            KPIs dictionary
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Fall statistics
        falls = get_fall_events(db, skip=0, limit=10000, start_date=start_date, end_date=end_date)
        total_falls = len(falls)
        true_positives = sum(1 for f in falls if not f.is_false_positive)
        false_positives = sum(1 for f in falls if f.is_false_positive)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = 1.0  # Simplified
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Alert statistics
        alerts = get_alerts(db, skip=0, limit=10000, start_date=start_date, end_date=end_date)
        total_alerts = len(alerts)
        sent_alerts = sum(1 for a in alerts if a.status.value == "sent")
        
        # Camera statistics
        active_cameras = db.query(Camera).filter(Camera.is_active == True).count()
        total_cameras = db.query(Camera).count()
        
        # Person statistics
        active_persons = db.query(Person).filter(Person.is_active == True).count()
        total_persons = db.query(Person).count()
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "detection": {
                "total_falls": total_falls,
                "true_positives": true_positives,
                "false_positives": false_positives,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1_score, 4),
                "false_positive_rate": round(false_positives / total_falls * 100, 2) if total_falls > 0 else 0.0
            },
            "alerts": {
                "total": total_alerts,
                "sent": sent_alerts,
                "success_rate": round(sent_alerts / total_alerts * 100, 2) if total_alerts > 0 else 0.0
            },
            "cameras": {
                "total": total_cameras,
                "active": active_cameras,
                "active_percentage": round(active_cameras / total_cameras * 100, 2) if total_cameras > 0 else 0.0
            },
            "persons": {
                "total": total_persons,
                "active": active_persons,
                "active_percentage": round(active_persons / total_persons * 100, 2) if total_persons > 0 else 0.0
            }
        }
    
    def get_time_series_data(
        self,
        db: Session,
        metric: str,
        days: int = 30,
        granularity: str = "daily"
    ) -> Dict[str, Any]:
        """
        Get time series data for a metric.
        
        Args:
            db: Database session
            metric: Metric name (falls, alerts, etc.)
            days: Number of days
            granularity: daily or hourly
        
        Returns:
            Time series data
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if metric == "falls":
            data = get_fall_events(db, skip=0, limit=10000, start_date=start_date, end_date=end_date)
        elif metric == "alerts":
            data = get_alerts(db, skip=0, limit=10000, start_date=start_date, end_date=end_date)
        else:
            return {"error": "Unknown metric"}
        
        # Group by time period
        time_series = {}
        for item in data:
            if granularity == "daily":
                key = item.created_at.strftime("%Y-%m-%d")
            else:
                key = item.created_at.strftime("%Y-%m-%d %H:00")
            
            time_series[key] = time_series.get(key, 0) + 1
        
        # Sort by time
        sorted_series = dict(sorted(time_series.items()))
        
        return {
            "metric": metric,
            "granularity": granularity,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "data": sorted_series
        }
    
    def get_camera_performance(
        self,
        db: Session,
        camera_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get camera performance metrics.
        
        Args:
            db: Database session
            camera_id: Specific camera ID or None for all
            days: Number of days
        
        Returns:
            Camera performance data
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if camera_id:
            cameras = [get_cameras(db, camera_id=camera_id)]
        else:
            cameras = get_cameras(db, skip=0, limit=1000)
        
        performance_data = []
        
        for camera in cameras:
            if not camera:
                continue
            
            # Get falls for this camera
            camera_falls = get_fall_events(
                db, skip=0, limit=10000,
                camera_id=camera.id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Calculate metrics
            total_falls = len(camera_falls)
            avg_confidence = sum(f.detection_confidence or 0.0 for f in camera_falls) / total_falls if total_falls > 0 else 0.0
            
            performance_data.append({
                "camera_id": camera.id,
                "camera_name": camera.name,
                "room": camera.room,
                "total_falls": total_falls,
                "avg_confidence": round(avg_confidence, 4),
                "status": camera.status.value,
                "is_active": camera.is_active,
                "last_seen": camera.last_seen.isoformat() if camera.last_seen else None
            })
        
        return {
            "period_days": days,
            "cameras": performance_data
        }
    
    def get_person_risk_analysis(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get risk analysis for persons.
        
        Args:
            db: Database session
            days: Number of days
        
        Returns:
            Risk analysis data
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        persons = get_persons(db, skip=0, limit=10000)
        
        risk_data = []
        
        for person in persons:
            # Get falls for this person
            person_falls = get_fall_events(
                db, skip=0, limit=10000,
                person_id=person.id,
                start_date=start_date,
                end_date=end_date
            )
            
            total_falls = len(person_falls)
            
            # Calculate risk score
            if total_falls > 0:
                avg_gravity_score = sum(f.gravity_score or 0.0 for f in person_falls) / total_falls
                risk_score = min(avg_gravity_score / 100.0 * total_falls, 1.0)
            else:
                avg_gravity_score = 0.0
                risk_score = 0.0
            
            risk_data.append({
                "person_id": person.id,
                "name": f"{person.first_name} {person.last_name}",
                "profile_type": person.profile_type.value if person.profile_type else None,
                "total_falls": total_falls,
                "avg_gravity_score": round(avg_gravity_score, 2),
                "risk_score": round(risk_score, 4),
                "risk_level": self._determine_risk_level(risk_score)
            })
        
        # Sort by risk score
        risk_data.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return {
            "period_days": days,
            "persons": risk_data
        }
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score."""
        if risk_score > 0.75:
            return "high"
        elif risk_score > 0.5:
            return "medium"
        elif risk_score > 0.25:
            return "low"
        else:
            return "minimal"


# Global dashboard service instance

    def get_kpi_history(self, db: Session, days: int = 30) -> Dict[str, Any]:
        from backend.services.kpi_history import build_kpi_history
        end_date = datetime.utcnow(); start_date = end_date - timedelta(days=days)
        falls = get_fall_events(db, skip=0, limit=10000, start_date=start_date, end_date=end_date)
        alerts = get_alerts(db, skip=0, limit=10000, start_date=start_date, end_date=end_date)
        return build_kpi_history(falls, alerts, days=days)

dashboard_service = DashboardService()

