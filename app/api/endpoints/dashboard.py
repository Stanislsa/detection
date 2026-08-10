"""
Endpoints pour le tableau de bord et les KPIs.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict
from datetime import datetime, timedelta

from app.models.base import get_db
from app.models.fall_event import FallEvent, GravityLevel
from app.models.alert import Alert
from app.models.camera import Camera

router = APIRouter()


@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    """
    Retourne les KPIs du système.
    """
    # Période d'analyse (30 derniers jours)
    since = datetime.utcnow() - timedelta(days=30)
    
    # Total des chutes
    total_falls = db.query(FallEvent).filter(FallEvent.detected_at >= since).count()
    
    # Répartition par gravité
    gravity_dist = db.query(
        FallEvent.gravity_level,
        func.count(FallEvent.id)
    ).filter(FallEvent.detected_at >= since).group_by(FallEvent.gravity_level).all()
    
    # Taux de faux positifs
    fp_count = db.query(FallEvent).filter(
        and_(FallEvent.detected_at >= since, FallEvent.is_false_positive == True)
    ).count()
    
    confirmed_count = db.query(FallEvent).filter(
        and_(FallEvent.detected_at >= since, FallEvent.is_false_positive == False)
    ).count()
    
    fpr = fp_count / (fp_count + confirmed_count) if (fp_count + confirmed_count) > 0 else 0
    
    # Temps moyen de détection
    avg_detection_time = db.query(func.avg(FallEvent.time_to_detection_ms)).filter(
        FallEvent.detected_at >= since
    ).scalar()
    
    # Alertes envoyées
    total_alerts = db.query(Alert).filter(Alert.sent_at >= since).count()
    
    # Caméras actives
    active_cameras = db.query(Camera).filter(Camera.is_active == True).count()
    
    return {
        "period_days": 30,
        "total_falls": total_falls,
        "gravity_distribution": {g.value: c for g, c in gravity_dist},
        "false_positive_rate": round(fpr * 100, 2),
        "avg_detection_time_ms": round(avg_detection_time, 2) if avg_detection_time else None,
        "total_alerts": total_alerts,
        "active_cameras": active_cameras
    }


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """
    Métriques de performance du système.
    """
    since = datetime.utcnow() - timedelta(days=30)
    
    # Matrice de confusion
    tp = db.query(FallEvent).filter(
        and_(FallEvent.detected_at >= since, FallEvent.is_false_positive == False)
    ).count()
    
    fp = db.query(FallEvent).filter(
        and_(FallEvent.detected_at >= since, FallEvent.is_false_positive == True)
    ).count()
    
    # Précision et Rappel
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = 1.0  # Simplifié : on considère qu'on ne manque pas de chutes
    
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "true_positives": tp,
        "false_positives": fp,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "accuracy": round((tp) / (tp + fp), 4) if (tp + fp) > 0 else 0
    }
