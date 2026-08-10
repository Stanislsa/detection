"""
Service de tableau de bord.

Agrégation des KPIs et métriques.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import FallEvent, Alert, Person, Camera


class DashboardService:
    """Service pour le tableau de bord et les KPIs."""
    
    def __init__(self, db: Session):
        """
        Initialise le service.
        
        Args:
            db: Session de base de données
        """
        self.db = db
    
    def get_kpis(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """
        Récupère les KPIs principaux.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
        
        Returns:
            Dictionnaire des KPIs
        """
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Récupérer les événements de chute sur la période
        period_falls = self.db.query(FallEvent).filter(
            FallEvent.detected_at >= start_date,
            FallEvent.detected_at <= end_date
        ).all()
        
        # Calculer les métriques
        total_falls = len(period_falls)
        true_positives = sum(1 for f in period_falls if not f.is_false_positive)
        false_positives = sum(1 for f in period_falls if f.is_false_positive)
        
        # Calculer les KPIs
        precision = self._calculate_precision(true_positives, false_positives)
        recall = self._calculate_recall(true_positives, 0)  # FN nécessite données de référence
        f1_score = self._calculate_f1_score(precision, recall)
        
        # Statistiques de gravité
        gravity_distribution = self._calculate_gravity_distribution(period_falls)
        
        # Statistiques d'alertes
        period_alerts = self.db.query(Alert).filter(
            Alert.sent_at >= start_date,
            Alert.sent_at <= end_date
        ).all()
        
        alert_stats = {
            "total": len(period_alerts),
            "sent": sum(1 for a in period_alerts if a.status == "sent"),
            "delivered": sum(1 for a in period_alerts if a.status == "delivered"),
            "failed": sum(1 for a in period_alerts if a.status == "failed"),
            "avg_delivery_time_ms": self._calculate_avg_delivery_time(period_alerts)
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
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score
            },
            "gravity_distribution": gravity_distribution,
            "alerts": alert_stats
        }
    
    def get_camera_statistics(self) -> List[Dict]:
        """
        Statistiques par caméra.
        
        Returns:
            Liste des statistiques par caméra
        """
        cameras = self.db.query(Camera).all()
        
        camera_stats = []
        for camera in cameras:
            falls = self.db.query(FallEvent).filter(
                FallEvent.camera_id == camera.id
            ).all()
            
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
    
    def get_profile_statistics(self) -> Dict:
        """
        Statistiques par profil utilisateur.
        
        Returns:
            Statistiques par profil
        """
        persons = self.db.query(Person).all()
        
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
    
    def _calculate_precision(self, tp: int, fp: int) -> float:
        """Calcule la précision."""
        if tp + fp == 0:
            return 0.0
        return tp / (tp + fp)
    
    def _calculate_recall(self, tp: int, fn: int) -> float:
        """Calcule le rappel."""
        if tp + fn == 0:
            return 0.0
        return tp / (tp + fn)
    
    def _calculate_f1_score(self, precision: float, recall: float) -> float:
        """Calcule le F1-Score."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def _calculate_gravity_distribution(self, falls: List[FallEvent]) -> Dict[str, int]:
        """Calcule la distribution des niveaux de gravité."""
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
    
    def _calculate_avg_delivery_time(self, alerts: List[Alert]) -> float:
        """Calcule le temps moyen de livraison des alertes."""
        if not alerts:
            return 0.0
        
        delivery_times = [a.delivery_time_ms for a in alerts if a.delivery_time_ms is not None]
        
        if not delivery_times:
            return 0.0
        
        return sum(delivery_times) / len(delivery_times)
