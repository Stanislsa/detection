"""
Dashboard and analytics endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Optional
from datetime import datetime, timedelta

from backend.api.dependencies import get_db, get_current_user
from backend.database.models import FallEvent, Alert, Camera, Person
from backend.database.crud import get_fall_events, get_alerts
from backend.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/kpis")
async def get_kpis(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system KPIs including precision, recall, F1-score, and detection metrics.
    """
    # Default period: last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get fall events for period
    all_falls = get_fall_events(db, skip=0, limit=10000, start_date=start_date, end_date=end_date)
    
    # Calculate detection metrics
    total_falls = len(all_falls)
    true_positives = sum(1 for f in all_falls if not f.is_false_positive)
    false_positives = sum(1 for f in all_falls if f.is_false_positive)
    
    # Calculate metrics
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = 1.0  # Simplified - assumes no false negatives
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    false_positive_rate = false_positives / (false_positives + true_positives) if (false_positives + true_positives) > 0 else 0.0
    
    # Average detection time
    detection_times = [
        (f.confirmed_at - f.detected_at).total_seconds() 
        for f in all_falls 
        if f.confirmed_at and not f.is_false_positive
    ]
    avg_detection_time = sum(detection_times) / len(detection_times) if detection_times else 0.0
    
    # Gravity distribution
    gravity_dist = {}
    for fall in all_falls:
        if fall.gravity_level:
            level = fall.gravity_level.value
            gravity_dist[level] = gravity_dist.get(level, 0) + 1
    
    # Alert statistics
    all_alerts = get_alerts(db, skip=0, limit=10000, start_date=start_date, end_date=end_date)
    alert_stats = {
        "total": len(all_alerts),
        "sent": sum(1 for a in all_alerts if a.status.value == "sent"),
        "delivered": sum(1 for a in all_alerts if a.status.value == "delivered"),
        "failed": sum(1 for a in all_alerts if a.status.value == "failed"),
        "avg_delivery_time_ms": sum(a.delivery_time_ms for a in all_alerts if a.delivery_time_ms) / len(all_alerts) if all_alerts else 0.0
    }
    
    # Active cameras
    active_cameras = db.query(Camera).filter(Camera.is_active == True).count()
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "days": (end_date - start_date).days
        },
        "detection": {
            "total_falls": total_falls,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1_score, 4),
            "false_positive_rate": round(false_positive_rate, 4),
            "avg_detection_time_seconds": round(avg_detection_time, 2)
        },
        "gravity_distribution": gravity_dist,
        "alerts": alert_stats,
        "cameras": {
            "active": active_cameras,
            "total": db.query(Camera).count()
        },
        "persons": {
            "total": db.query(Person).filter(Person.is_active == True).count()
        }
    }


@router.get("/statistics/falls")
async def get_fall_statistics(
    person_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed fall statistics."""
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    falls = get_fall_events(
        db, skip=0, limit=10000, person_id=person_id, 
        camera_id=camera_id, start_date=start_date, end_date=end_date
    )
    
    # Daily statistics
    daily_stats = {}
    for fall in falls:
        date_key = fall.detected_at.strftime("%Y-%m-%d")
        daily_stats[date_key] = daily_stats.get(date_key, 0) + 1
    
    # Hourly statistics
    hourly_stats = {}
    for fall in falls:
        hour_key = fall.detected_at.strftime("%H:00")
        hourly_stats[hour_key] = hourly_stats.get(hour_key, 0) + 1
    
    # Gravity distribution
    gravity_dist = {}
    for fall in falls:
        if fall.gravity_level:
            level = fall.gravity_level.value
            gravity_dist[level] = gravity_dist.get(level, 0) + 1
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total": len(falls),
        "daily_statistics": daily_stats,
        "hourly_statistics": hourly_stats,
        "gravity_distribution": gravity_dist
    }


@router.get("/statistics/cameras")
async def get_camera_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics per camera."""
    cameras = db.query(Camera).all()
    
    camera_stats = []
    for camera in cameras:
        camera_falls = get_fall_events(db, camera_id=camera.id, skip=0, limit=10000)
        
        stats = {
            "camera_id": camera.id,
            "camera_name": camera.name,
            "room": camera.room,
            "status": camera.status.value,
            "is_active": camera.is_active,
            "total_falls": len(camera_falls),
            "last_seen": camera.last_seen.isoformat() if camera.last_seen else None,
            "resolution": f"{camera.resolution_width}x{camera.resolution_height}",
            "fps": camera.fps
        }
        camera_stats.append(stats)
    
    return camera_stats


@router.get("/statistics/persons")
async def get_person_statistics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics per person."""
    from backend.core.constants import ProfileType, Gender
    
    persons = db.query(Person).filter(Person.is_active == True).all()
    
    profile_stats = {}
    gender_stats = {}
    
    for person in persons:
        # Profile type distribution
        profile = person.profile_type.value if person.profile_type else "unknown"
        profile_stats[profile] = profile_stats.get(profile, 0) + 1
        
        # Gender distribution
        gender = person.gender.value if person.gender else "unknown"
        gender_stats[gender] = gender_stats.get(gender, 0) + 1
    
    # Fall count per person
    person_fall_stats = []
    for person in persons:
        person_falls = get_fall_events(db, person_id=person.id, skip=0, limit=10000)
        person_fall_stats.append({
            "person_id": person.id,
            "name": f"{person.first_name} {person.last_name}",
            "profile_type": person.profile_type.value if person.profile_type else "unknown",
            "total_falls": len(person_falls),
            "false_positives": sum(1 for f in person_falls if f.is_false_positive)
        })
    
    return {
        "total_persons": len(persons),
        "profile_distribution": profile_stats,
        "gender_distribution": gender_stats,
        "person_fall_stats": person_fall_stats
    }


@router.get("/metrics")
async def get_system_metrics(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system performance metrics."""
    from backend.database.crud import get_aggregated_metrics
    
    # Recent metrics (last 24 hours)
    cpu_usage = get_aggregated_metrics(db, "cpu_usage", "avg")
    memory_usage = get_aggregated_metrics(db, "memory_usage", "avg")
    disk_usage = get_aggregated_metrics(db, "disk_usage", "avg")
    
    # Detection metrics
    detection_latency = get_aggregated_metrics(db, "detection_latency", "avg")
    frame_rate = get_aggregated_metrics(db, "frame_rate", "avg")
    
    return {
        "system": {
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory_usage,
            "disk_usage_percent": disk_usage
        },
        "detection": {
            "avg_latency_ms": detection_latency,
            "avg_frame_rate": frame_rate
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/stats")
async def get_stats(current_user=Depends(get_current_user), db: Session=Depends(get_db)):
    try:
        from backend.database.models import FallEvent, Alert, Camera, Person
        falls=db.query(FallEvent).count(); alerts=db.query(Alert).count()
        cameras=db.query(Camera).count(); persons=db.query(Person).count()
        active=db.query(Camera).filter(Camera.is_active==True).count()
    except Exception:
        falls=alerts=cameras=persons=active=0
    return {"falls_total":falls,"alerts_total":alerts,"cameras_total":cameras,"cameras_active":active,"persons_total":persons,"timestamp":datetime.utcnow().isoformat()}


@router.get("/history")
async def get_kpi_history(days: int = 30, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    from backend.services.dashboard_service import dashboard_service
    if hasattr(dashboard_service, "get_kpi_history"):
        return dashboard_service.get_kpi_history(db, days=max(1, min(days, 365)))
    from backend.services.kpi_history import build_kpi_history
    from backend.database.crud import get_fall_events, get_alerts
    from datetime import datetime, timedelta
    end = datetime.utcnow(); start = end - timedelta(days=days)
    falls = get_fall_events(db, skip=0, limit=10000, start_date=start, end_date=end)
    alerts = get_alerts(db, skip=0, limit=10000, start_date=start, end_date=end)
    return build_kpi_history(falls, alerts, days=days)
