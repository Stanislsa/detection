"""
Router pour le tableau de bord.

Agrégations pour les KPIs : précision, rappel, F1-score, taux de faux positifs, temps moyen de détection.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from database import crud, models
from backend.dependencies import get_db

router = APIRouter()


@router.get("/kpis")
async def get_kpis(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Récupère les KPIs principaux du système.
    
    Formules:
    - Précision = TP / (TP + FP)
    - Rappel = TP / (TP + FN)
    - F1-Score = 2 * (Précision * Rappel) / (Précision + Rappel)
    - FPR = FP / (FP + TN)
    - TDD = (1/N) * Σ(t_detection_i - t_chute_i)
    
    Args:
        start_date: Date de début de la période
        end_date: Date de fin de la période
        db: Session de base de données
    
    Returns:
        Dictionnaire des KPIs
    """
    # Définir la période par défaut (30 derniers jours)
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Récupérer les événements de chute sur la période
    all_falls = crud.get_fall_events(db, skip=0, limit=1000)
    
    # Filtrer par date
    period_falls = [
        f for f in all_falls 
        if start_date <= f.detected_at <= end_date
    ]
    
    # Calculer les métriques
    total_falls = len(period_falls)
    true_positives = sum(1 for f in period_falls if not f.is_false_positive)
    false_positives = sum(1 for f in period_falls if f.is_false_positive)
    
    # Note: FN nécessite des données de référence (chutes réelles non détectées)
    # Pour l'instant, on utilise une estimation
    false_negatives = 0  # À implémenter avec des données de vérité terrain
    
    true_negatives = 0  # Difficile à calculer sans contexte
    
    # Calculer les KPIs
    precision = _calculate_precision(true_positives, false_positives)
    recall = _calculate_recall(true_positives, false_negatives)
    f1_score = _calculate_f1_score(precision, recall)
    fpr = _calculate_false_positive_rate(false_positives, true_negatives)
    
    # Temps moyen de détection
    avg_detection_time = _calculate_avg_detection_time(period_falls)
    
    # Statistiques de gravité
    gravity_distribution = _calculate_gravity_distribution(period_falls)
    
    # Statistiques d'alertes
    alerts = crud.get_alerts(db, skip=0, limit=1000)
    period_alerts = [
        a for a in alerts
        if start_date <= a.sent_at <= end_date
    ]
    
    alert_stats = {
        "total": len(period_alerts),
        "sent": sum(1 for a in period_alerts if a.status == "sent"),
        "delivered": sum(1 for a in period_alerts if a.status == "delivered"),
        "failed": sum(1 for a in period_alerts if a.status == "failed"),
        "avg_delivery_time_ms": _calculate_avg_delivery_time(period_alerts)
    }
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "detection": {
            "total_falls": total_falls,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "false_positive_rate": fpr,
            "avg_detection_time_seconds": avg_detection_time
        },
        "gravity_distribution": gravity_distribution,
        "alerts": alert_stats
    }


@router.get("/stats/falls")
async def get_fall_statistics(
    person_id: Optional[int] = None,
    camera_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Statistiques détaillées sur les chutes.
    
    Args:
        person_id: Filtrer par personne
        camera_id: Filtrer par caméra
        start_date: Date de début
        end_date: Date de fin
        db: Session de base de données
    
    Returns:
        Statistiques de chutes
    """
    # Définir la période par défaut
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Récupérer les chutes
    if person_id:
        falls = crud.get_fall_events_by_person(db, person_id, skip=0, limit=1000)
    elif camera_id:
        falls = crud.get_fall_events_by_camera(db, camera_id, skip=0, limit=1000)
    else:
        falls = crud.get_fall_events(db, skip=0, limit=1000)
    
    # Filtrer par date
    period_falls = [
        f for f in falls
        if start_date <= f.detected_at <= end_date
    ]
    
    # Statistiques par jour
    daily_stats = _calculate_daily_stats(period_falls)
    
    # Statistiques par heure
    hourly_stats = _calculate_hourly_stats(period_falls)
    
    # Distribution par gravité
    gravity_dist = _calculate_gravity_distribution(period_falls)
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total": len(period_falls),
        "daily_statistics": daily_stats,
        "hourly_statistics": hourly_stats,
        "gravity_distribution": gravity_dist
    }


@router.get("/stats/cameras")
async def get_camera_statistics(db: Session = Depends(get_db)):
    """
    Statistiques par caméra.
    
    Args:
        db: Session de base de données
    
    Returns:
        Statistiques par caméra
    """
    cameras = crud.get_cameras(db, skip=0, limit=100)
    
    camera_stats = []
    for camera in cameras:
        falls = crud.get_fall_events_by_camera(db, camera.id, skip=0, limit=1000)
        
        stats = {
            "camera_id": camera.id,
            "camera_name": camera.name,
            "room": camera.room,
            "is_active": camera.is_active,
            "total_falls": len(falls),
            "last_seen": camera.last_seen.isoformat() if camera.last_seen else None
        }
        
        camera_stats.append(stats)
    
    return camera_stats


@router.get("/stats/profiles")
async def get_profile_statistics(db: Session = Depends(get_db)):
    """
    Statistiques par profil utilisateur.
    
    Args:
        db: Session de base de données
    
    Returns:
        Statistiques par profil
    """
    persons = crud.get_persons(db, skip=0, limit=100)
    
    profile_stats = {
        "total_persons": len(persons),
        "by_profile_type": {},
        "by_gender": {}
    }
    
    for person in persons:
        # Par type de profil
        profile_type = person.profile_type.value if person.profile_type else "unknown"
        if profile_type not in profile_stats["by_profile_type"]:
            profile_stats["by_profile_type"][profile_type] = 0
        profile_stats["by_profile_type"][profile_type] += 1
        
        # Par genre
        gender = person.gender.value if person.gender else "unknown"
        if gender not in profile_stats["by_gender"]:
            profile_stats["by_gender"][gender] = 0
        profile_stats["by_gender"][gender] += 1
    
    return profile_stats


# Fonctions auxiliaires pour les calculs

def _calculate_precision(tp: int, fp: int) -> float:
    """
    Calcule la précision.
    
    Formule: Précision = TP / (TP + FP)
    
    Args:
        tp: True Positives
        fp: False Positives
    
    Returns:
        Précision [0, 1]
    """
    if tp + fp == 0:
        return 0.0
    return tp / (tp + fp)


def _calculate_recall(tp: int, fn: int) -> float:
    """
    Calcule le rappel.
    
    Formule: Rappel = TP / (TP + FN)
    
    Args:
        tp: True Positives
        fn: False Negatives
    
    Returns:
        Rappel [0, 1]
    """
    if tp + fn == 0:
        return 0.0
    return tp / (tp + fn)


def _calculate_f1_score(precision: float, recall: float) -> float:
    """
    Calcule le F1-Score.
    
    Formule: F1 = 2 * (Précision * Rappel) / (Précision + Rappel)
    
    Args:
        precision: Précision
        recall: Rappel
    
    Returns:
        F1-Score [0, 1]
    """
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)


def _calculate_false_positive_rate(fp: int, tn: int) -> float:
    """
    Calcule le taux de faux positifs.
    
    Formule: FPR = FP / (FP + TN)
    
    Args:
        fp: False Positives
        tn: True Negatives
    
    Returns:
        FPR [0, 1]
    """
    if fp + tn == 0:
        return 0.0
    return fp / (fp + tn)


def _calculate_avg_detection_time(falls: List[models.FallEvent]) -> float:
    """
    Calcule le temps moyen de détection.
    
    Formule: TDD = (1/N) * Σ(t_detection_i - t_chute_i)
    
    Note: En pratique, t_chute_i est difficile à obtenir sans annotation manuelle.
    Ici, on utilise le temps entre la détection et la confirmation comme approximation.
    
    Args:
        falls: Liste des événements de chute
    
    Returns:
        Temps moyen en secondes
    """
    if not falls:
        return 0.0
    
    detection_times = []
    for fall in falls:
        if fall.confirmed_at:
            delta = (fall.confirmed_at - fall.detected_at).total_seconds()
            detection_times.append(delta)
    
    if not detection_times:
        return 0.0
    
    return sum(detection_times) / len(detection_times)


def _calculate_avg_delivery_time(alerts: List[models.Alert]) -> float:
    """
    Calcule le temps moyen de livraison des alertes.
    
    Args:
        alerts: Liste des alertes
    
    Returns:
        Temps moyen en millisecondes
    """
    if not alerts:
        return 0.0
    
    delivery_times = [a.delivery_time_ms for a in alerts if a.delivery_time_ms is not None]
    
    if not delivery_times:
        return 0.0
    
    return sum(delivery_times) / len(delivery_times)


def _calculate_gravity_distribution(falls: List[models.FallEvent]) -> Dict[str, int]:
    """
    Calcule la distribution des niveaux de gravité.
    
    Args:
        falls: Liste des événements de chute
    
    Returns:
        Dictionnaire des comptes par niveau
    """
    distribution = {
        "faible": 0,
        "moyenne": 0,
        "elevee": 0,
        "critique": 0,
        "unknown": 0
    }
    
    for fall in falls:
        if fall.gravity_level:
            level = fall.gravity_level.value
            if level in distribution:
                distribution[level] += 1
            else:
                distribution["unknown"] += 1
        else:
            distribution["unknown"] += 1
    
    return distribution


def _calculate_daily_stats(falls: List[models.FallEvent]) -> Dict[str, int]:
    """
    Calcule les statistiques par jour.
    
    Args:
        falls: Liste des événements de chute
    
    Returns:
        Dictionnaire des comptes par jour
    """
    daily_stats = {}
    
    for fall in falls:
        date_key = fall.detected_at.strftime("%Y-%m-%d")
        if date_key not in daily_stats:
            daily_stats[date_key] = 0
        daily_stats[date_key] += 1
    
    return daily_stats


def _calculate_hourly_stats(falls: List[models.FallEvent]) -> Dict[str, int]:
    """
    Calcule les statistiques par heure.
    
    Args:
        falls: Liste des événements de chute
    
    Returns:
        Dictionnaire des comptes par heure
    """
    hourly_stats = {}
    
    for fall in falls:
        hour_key = fall.detected_at.strftime("%H:00")
        if hour_key not in hourly_stats:
            hourly_stats[hour_key] = 0
        hourly_stats[hour_key] += 1
    
    return hourly_stats
