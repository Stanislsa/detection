"""
Règle de détection de loitering (stationnement prolongé).
Détecte les personnes restant trop longtemps dans une zone.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.ai.rules.base_rule import BaseRuleEngine, Rule, RuleCondition, RuleAction
from app.desktop.workers.detection_worker import DetectionResult
from app.events.event_bus import EventBus
from app.events.event_types import AlertGeneratedEvent
from app.desktop.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from app.core.logger import get_logger


@dataclass
class PersonTrack:
    """Suivi d'une personne pour la détection de loitering."""
    person_id: str
    camera_id: str
    zone_id: str
    first_seen: datetime
    last_seen: datetime
    position_history: List[tuple]  # Historique des positions
    total_duration: float = 0.0  # Durée totale en secondes
    
    def update_position(self, position: tuple):
        """Met à jour la position de la personne."""
        self.position_history.append(position)
        if len(self.position_history) > 100:  # Limiter l'historique
            self.position_history.pop(0)
        self.last_seen = datetime.now()
        self.total_duration = (self.last_seen - self.first_seen).total_seconds()
    
    def is_moving(self, threshold: float = 50.0) -> bool:
        """
        Vérifie si la personne est en mouvement.
        
        Args:
            threshold: Seuil de mouvement en pixels
        
        Returns:
            True si la personne bouge significativement
        """
        if len(self.position_history) < 2:
            return False
        
        # Comparer la position actuelle avec la position il y a 10 frames
        lookback = min(10, len(self.position_history))
        old_pos = self.position_history[-lookback]
        current_pos = self.position_history[-1]
        
        dx = current_pos[0] - old_pos[0]
        dy = current_pos[1] - old_pos[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        return distance > threshold


class LoiteringRuleEngine(BaseRuleEngine):
    """
    Moteur de règles pour la détection de loitering.
    Détecte les personnes restant trop longtemps dans une zone.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialise le moteur de règles de loitering.
        
        Args:
            event_bus: Instance du bus d'événements
        """
        super().__init__(event_bus)
        self._person_tracks: Dict[str, PersonTrack] = {}  # Tracking par person_id
        self._loitering_threshold_seconds = 60  # 1 minute par défaut
        self._movement_threshold = 50.0  # pixels
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configure les règles par défaut."""
        # Règle: Loitering détecté (stationnement prolongé sans mouvement significatif)
        rule = Rule(
            name="loitering_detected",
            description="Détection de loitering (stationnement prolongé)",
            conditions=[
                RuleCondition(field="duration", operator=">", value=60),
                RuleCondition(field="is_moving", operator="==", value=False),
                RuleCondition(field="zone_type", operator="==", value="monitored")
            ],
            actions=[
                RuleAction(
                    action_type="generate_alert",
                    parameters={
                        "alert_type": "loitering",
                        "severity": "medium",
                        "message": "Stationnement prolongé détecté"
                    }
                )
            ],
            cooldown_seconds=120
        )
        self.add_rule(rule)
        
        # Règle: Loitering critique (stationnement très prolongé)
        rule = Rule(
            name="loitering_critical",
            description="Stationnement critique (très prolongé)",
            conditions=[
                RuleCondition(field="duration", operator=">", value=300),
                RuleCondition(field="is_moving", operator="==", value=False)
            ],
            actions=[
                RuleAction(
                    action_type="generate_alert",
                    parameters={
                        "alert_type": "loitering",
                        "severity": "high",
                        "message": "Stationnement critique détecté"
                    }
                )
            ],
            cooldown_seconds=300
        )
        self.add_rule(rule)
    
    def set_loitering_threshold(self, threshold_seconds: int):
        """
        Définit le seuil de temps pour le loitering.
        
        Args:
            threshold_seconds: Seuil en secondes
        """
        self._loitering_threshold_seconds = threshold_seconds
    
    def set_movement_threshold(self, threshold_pixels: float):
        """
        Définit le seuil de mouvement.
        
        Args:
            threshold_pixels: Seuil en pixels
        """
        self._movement_threshold = threshold_pixels
    
    def process_detections(self, detections: List[DetectionResult], context: Dict[str, Any]):
        """
        Traite les détections avec le moteur de règles de loitering.
        
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
        
        if not person_detections:
            return
        
        now = datetime.now()
        
        for detection in person_detections:
            # Calculer la position
            bbox = detection.bbox
            center_x = bbox[0] + bbox[2] / 2
            center_y = bbox[1] + bbox[3] / 2
            position = (center_x, center_y)
            
            # Créer un ID de personne unique
            person_id = f"{camera_id}_{zone_id}_{int(center_x)}_{int(center_y)}"
            
            # Créer ou mettre à jour le tracking
            if person_id not in self._person_tracks:
                self._person_tracks[person_id] = PersonTrack(
                    person_id=person_id,
                    camera_id=camera_id,
                    zone_id=zone_id,
                    first_seen=now,
                    last_seen=now,
                    position_history=[position]
                )
            else:
                self._person_tracks[person_id].update_position(position)
            
            # Créer le contexte pour les règles
            track = self._person_tracks[person_id]
            rule_context = {
                "camera_id": camera_id,
                "zone_id": zone_id,
                "zone_type": zone_type,
                "person_id": person_id,
                "duration": track.total_duration,
                "is_moving": track.is_moving(self._movement_threshold),
                "confidence": detection.confidence,
                "timestamp": context.get("timestamp")
            }
            
            # Évaluer les règles
            triggered_rules = self.evaluate_rules(rule_context)
            
            # Générer des alertes pour les règles déclenchées
            for rule in triggered_rules:
                self._generate_alert(rule, rule_context)
    
    def _generate_alert(self, rule: Rule, context: Dict[str, Any]):
        """Génère une alerte de loitering."""
        alert = Alert(
            id=0,
            camera_id=int(context.get("camera_id", 0)),
            camera_name=f"Camera {context.get('camera_id')}",
            alert_type=AlertType.MOVEMENT,
            severity=AlertSeverity.HIGH if rule.name == "loitering_critical" else AlertSeverity.MEDIUM,
            status=AlertStatus.NEW,
            detected_at=datetime.now(),
            confidence=context.get("confidence", 0.0),
            bbox=(0, 0, 0, 0),
            description=f"Stationnement de {context.get('duration', 0):.0f}s détecté dans la zone {context.get('zone_id')}"
        )
        
        event = AlertGeneratedEvent(alert=alert)
        self.event_bus.publish(event)
    
    def cleanup_old_tracks(self, max_age_seconds: int = 600):
        """
        Nettoie les tracks anciens.
        
        Args:
            max_age_seconds: Âge maximum en secondes
        """
        now = datetime.now()
        to_remove = []
        
        for person_id, track in self._person_tracks.items():
            if (now - track.last_seen).total_seconds() > max_age_seconds:
                to_remove.append(person_id)
        
        for person_id in to_remove:
            del self._person_tracks[person_id]
        
        if to_remove:
            self._logger.debug(f"Nettoyage de {len(to_remove)} tracks de loitering")
    
    def get_active_loitering(self) -> List[Dict[str, Any]]:
        """
        Retourne les cas de loitering actifs.
        
        Returns:
            Liste des informations de loitering
        """
        active = []
        
        for person_id, track in self._person_tracks.items():
            if track.total_duration > self._loitering_threshold_seconds:
                active.append({
                    "person_id": person_id,
                    "camera_id": track.camera_id,
                    "zone_id": track.zone_id,
                    "duration": track.total_duration,
                    "is_moving": track.is_moving(self._movement_threshold),
                    "first_seen": track.first_seen.isoformat(),
                    "last_seen": track.last_seen.isoformat()
                })
        
        return active
