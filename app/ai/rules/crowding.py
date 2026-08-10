"""
Règle de détection de foule (crowding).
Détecte un nombre élevé de personnes dans une zone.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

from app.ai.rules.base_rule import BaseRuleEngine, Rule, RuleCondition, RuleAction
from app.desktop.workers.detection_worker import DetectionResult
from app.events.event_bus import EventBus
from app.events.event_types import AlertGeneratedEvent
from app.desktop.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from app.core.logger import get_logger


@dataclass
class ZoneCrowdingMetrics:
    """Métriques de foule pour une zone."""
    zone_id: str
    camera_id: str
    person_count: int = 0
    max_person_count: int = 0
    avg_person_count: float = 0.0
    count_history: List[int] = None
    first_over_threshold: Optional[datetime] = None
    duration_over_threshold: float = 0.0
    
    def __post_init__(self):
        if self.count_history is None:
            self.count_history = []
    
    def update(self, person_count: int):
        """Met à jour les métriques avec un nouveau comptage."""
        self.person_count = person_count
        self.count_history.append(person_count)
        
        if len(self.count_history) > 100:  # Limiter l'historique
            self.count_history.pop(0)
        
        self.max_person_count = max(self.max_person_count, person_count)
        self.avg_person_count = sum(self.count_history) / len(self.count_history)
    
    def get_duration_over_threshold(self, threshold: int) -> float:
        """
        Calcule la durée où le nombre de personnes dépasse le seuil.
        
        Args:
            threshold: Seuil de personnes
        
        Returns:
            Durée en secondes
        """
        now = datetime.now()
        
        if self.person_count > threshold:
            if self.first_over_threshold is None:
                self.first_over_threshold = now
            self.duration_over_threshold = (now - self.first_over_threshold).total_seconds()
        else:
            self.first_over_threshold = None
            self.duration_over_threshold = 0.0
        
        return self.duration_over_threshold


class CrowdingRuleEngine(BaseRuleEngine):
    """
    Moteur de règles pour la détection de foule.
    Détecte un nombre élevé de personnes dans une zone.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialise le moteur de règles de foule.
        
        Args:
            event_bus: Instance du bus d'événements
        """
        super().__init__(event_bus)
        self._zone_metrics: Dict[str, ZoneCrowdingMetrics] = {}  # Metrics par zone
        self._crowding_threshold = 5  # Nombre de personnes par défaut
        self._critical_threshold = 10  # Seuil critique
        self._duration_threshold = 30  # Durée minimale en secondes
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configure les règles par défaut."""
        # Règle: Foule détectée (nombre élevé de personnes)
        rule = Rule(
            name="crowding_detected",
            description="Détection de foule dans une zone",
            conditions=[
                RuleCondition(field="person_count", operator=">", value=5),
                RuleCondition(field="duration_over_threshold", operator=">", value=30)
            ],
            actions=[
                RuleAction(
                    action_type="generate_alert",
                    parameters={
                        "alert_type": "crowding",
                        "severity": "medium",
                        "message": "Foule détectée dans une zone"
                    }
                )
            ],
            cooldown_seconds=120
        )
        self.add_rule(rule)
        
        # Règle: Foule critique (très élevée)
        rule = Rule(
            name="crowding_critical",
            description="Foule critique détectée",
            conditions=[
                RuleCondition(field="person_count", operator=">", value=10),
                RuleCondition(field="duration_over_threshold", operator=">", value=15)
            ],
            actions=[
                RuleAction(
                    action_type="generate_alert",
                    parameters={
                        "alert_type": "crowding",
                        "severity": "high",
                        "message": "Foule critique détectée"
                    }
                )
            ],
            cooldown_seconds=60
        )
        self.add_rule(rule)
        
        # Règle: Foule soudaine (augmentation rapide)
        rule = Rule(
            name="crowding_sudden",
            description="Augmentation soudaine du nombre de personnes",
            conditions=[
                RuleCondition(field="person_count", operator=">", value=3),
                RuleCondition(field="increase_rate", operator=">", value=2.0)
            ],
            actions=[
                RuleAction(
                    action_type="generate_alert",
                    parameters={
                        "alert_type": "crowding",
                        "severity": "medium",
                        "message": "Augmentation soudaine du nombre de personnes"
                    }
                )
            ],
            cooldown_seconds=60
        )
        self.add_rule(rule)
    
    def set_crowding_threshold(self, threshold: int):
        """
        Définit le seuil de foule.
        
        Args:
            threshold: Nombre de personnes
        """
        self._crowding_threshold = threshold
    
    def set_critical_threshold(self, threshold: int):
        """
        Définit le seuil critique.
        
        Args:
            threshold: Nombre de personnes
        """
        self._critical_threshold = threshold
    
    def set_duration_threshold(self, threshold_seconds: int):
        """
        Définit la durée minimale pour déclencher une alerte.
        
        Args:
            threshold_seconds: Durée en secondes
        """
        self._duration_threshold = threshold_seconds
    
    def process_detections(self, detections: List[DetectionResult], context: Dict[str, Any]):
        """
        Traite les détections avec le moteur de règles de foule.
        
        Args:
            detections: Liste des détections
            context: Contexte additionnel (camera_id, frame, zone_id, etc.)
        """
        camera_id = context.get("camera_id", "")
        zone_id = context.get("zone_id", "")
        zone_type = context.get("zone_type", "monitored")
        frame = context.get("frame")
        
        # Filtrer les détections de personnes
        person_detections = [
            d for d in detections
            if d.class_name == "person"
        ]
        
        person_count = len(person_detections)
        
        # Créer ou mettre à jour les métriques de la zone
        zone_key = f"{camera_id}_{zone_id}"
        
        if zone_key not in self._zone_metrics:
            self._zone_metrics[zone_key] = ZoneCrowdingMetrics(
                zone_id=zone_id,
                camera_id=camera_id
            )
        
        self._zone_metrics[zone_key].update(person_count)
        
        # Calculer le taux d'augmentation
        increase_rate = 0.0
        if len(self._zone_metrics[zone_key].count_history) >= 10:
            recent = self._zone_metrics[zone_key].count_history[-10:]
            avg_recent = sum(recent) / len(recent)
            older = self._zone_metrics[zone_key].count_history[:-10]
            if older:
                avg_older = sum(older) / len(older)
                if avg_older > 0:
                    increase_rate = avg_recent / avg_older
        
        # Créer le contexte pour les règles
        rule_context = {
            "camera_id": camera_id,
            "zone_id": zone_id,
            "zone_type": zone_type,
            "person_count": person_count,
            "duration_over_threshold": self._zone_metrics[zone_key].get_duration_over_threshold(self._crowding_threshold),
            "increase_rate": increase_rate,
            "avg_person_count": self._zone_metrics[zone_key].avg_person_count,
            "max_person_count": self._zone_metrics[zone_key].max_person_count,
            "timestamp": context.get("timestamp")
        }
        
        # Évaluer les règles
        triggered_rules = self.evaluate_rules(rule_context)
        
        # Générer des alertes pour les règles déclenchées
        for rule in triggered_rules:
            self._generate_alert(rule, rule_context)
    
    def _generate_alert(self, rule: Rule, context: Dict[str, Any]):
        """Génère une alerte de foule."""
        alert = Alert(
            id=0,
            camera_id=int(context.get("camera_id", 0)),
            camera_name=f"Camera {context.get('camera_id')}",
            alert_type=AlertType.MOVEMENT,
            severity=AlertSeverity.HIGH if rule.name == "crowding_critical" else AlertSeverity.MEDIUM,
            status=AlertStatus.NEW,
            detected_at=datetime.now(),
            confidence=0.9,
            bbox=(0, 0, 0, 0),
            description=f"{context.get('person_count', 0)} personnes détectées dans la zone {context.get('zone_id')} (durée: {context.get('duration_over_threshold', 0):.0f}s)"
        )
        
        event = AlertGeneratedEvent(alert=alert)
        self.event_bus.publish(event)
    
    def get_zone_metrics(self, camera_id: str, zone_id: str) -> Optional[ZoneCrowdingMetrics]:
        """
        Retourne les métriques d'une zone.
        
        Args:
            camera_id: ID de la caméra
            zone_id: ID de la zone
        
        Returns:
            Métriques ou None
        """
        zone_key = f"{camera_id}_{zone_id}"
        return self._zone_metrics.get(zone_key)
    
    def get_all_zone_metrics(self) -> Dict[str, ZoneCrowdingMetrics]:
        """Retourne les métriques de toutes les zones."""
        return self._zone_metrics.copy()
    
    def cleanup_old_metrics(self, max_age_seconds: int = 3600):
        """
        Nettoie les métriques anciennes.
        
        Args:
            max_age_seconds: Âge maximum en secondes
        """
        now = datetime.now()
        to_remove = []
        
        for zone_key, metrics in self._zone_metrics.items():
            # Nettoyer si personne depuis longtemps
            if metrics.person_count == 0 and len(metrics.count_history) > 0:
                last_update = now - timedelta(seconds=len(metrics.count_history) * 0.1)  # Approximation
                if last_update.total_seconds() > max_age_seconds:
                    to_remove.append(zone_key)
        
        for zone_key in to_remove:
            del self._zone_metrics[zone_key]
        
        if to_remove:
            self._logger.debug(f"Nettoyage de {len(to_remove)} métriques de foule")
