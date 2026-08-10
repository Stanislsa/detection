"""
Règle de détection d'intrusion.
Détecte les personnes entrant dans des zones interdites.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np

from app.ai.rules.base_rule import BaseRuleEngine, Rule, RuleCondition, RuleAction
from app.desktop.workers.detection_worker import DetectionResult
from app.events.event_bus import EventBus
from app.events.event_types import IntrusionDetectedEvent
from app.core.logger import get_logger


@dataclass
class Zone:
    """Zone de détection."""
    id: str
    name: str
    polygon: List[tuple]  # Liste de points (x, y)
    allowed_classes: List[str] = None  # Classes autorisées (vide = aucune)
    max_persons: int = 0  # 0 = aucune personne autorisée
    
    def __post_init__(self):
        if self.allowed_classes is None:
            self.allowed_classes = []
    
    def contains_point(self, point: tuple) -> bool:
        """
        Vérifie si un point est dans la zone (algorithme ray casting).
        
        Args:
            point: Point (x, y)
        
        Returns:
            True si le point est dans la zone
        """
        x, y = point
        n = len(self.polygon)
        inside = False
        
        p1x, p1y = self.polygon[0]
        for i in range(n + 1):
            p2x, p2y = self.polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def get_center(self) -> tuple:
        """Retourne le centre de la zone."""
        if not self.polygon:
            return (0, 0)
        
        x = sum(p[0] for p in self.polygon) / len(self.polygon)
        y = sum(p[1] for p in self.polygon) / len(self.polygon)
        return (x, y)


class IntrusionRuleEngine(BaseRuleEngine):
    """
    Moteur de règles pour la détection d'intrusion.
    Détecte les personnes entrant dans des zones interdites.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialise le moteur de règles d'intrusion.
        
        Args:
            event_bus: Instance du bus d'événements
        """
        super().__init__(event_bus)
        self._zones: Dict[str, Zone] = {}
        self._person_tracking: Dict[str, List[Dict]] = {}  # Suivi des personnes par caméra
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configure les règles par défaut."""
        # Règle: Personne détectée dans une zone interdite
        rule = Rule(
            name="intrusion_zone",
            description="Détection d'intrusion dans une zone interdite",
            conditions=[
                RuleCondition(field="person_in_zone", operator="==", value=True),
                RuleCondition(field="zone_type", operator="==", value="restricted")
            ],
            actions=[
                RuleAction(
                    action_type="generate_alert",
                    parameters={
                        "alert_type": "intrusion",
                        "severity": "high",
                        "message": "Intrusion détectée dans une zone interdite"
                    }
                )
            ],
            cooldown_seconds=30
        )
        self.add_rule(rule)
        
        # Règle: Plusieurs personnes dans une zone
        rule = Rule(
            name="crowding_zone",
            description="Détection de foule dans une zone",
            conditions=[
                RuleCondition(field="person_count", operator=">", value=5),
                RuleCondition(field="duration", operator=">", value=60)
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
    
    def add_zone(self, zone: Zone):
        """
        Ajoute une zone de détection.
        
        Args:
            zone: Zone à ajouter
        """
        self._zones[zone.id] = zone
        self._logger.info(f"Zone ajoutée: {zone.name} ({zone.id})")
    
    def remove_zone(self, zone_id: str) -> bool:
        """
        Supprime une zone de détection.
        
        Args:
            zone_id: ID de la zone
        
        Returns:
            True si succès
        """
        if zone_id in self._zones:
            del self._zones[zone_id]
            self._logger.info(f"Zone supprimée: {zone_id}")
            return True
        return False
    
    def get_zones(self) -> Dict[str, Zone]:
        """Retourne toutes les zones."""
        return self._zones.copy()
    
    def process_detections(self, detections: List[DetectionResult], context: Dict[str, Any]):
        """
        Traite les détections avec le moteur de règles d'intrusion.
        
        Args:
            detections: Liste des détections
            context: Contexte additionnel (camera_id, frame, etc.)
        """
        camera_id = context.get("camera_id", "")
        frame = context.get("frame")
        
        # Filtrer les détections de personnes
        person_detections = [
            d for d in detections
            if d.class_name == "person"
        ]
        
        if not person_detections:
            return
        
        # Vérifier chaque zone
        for zone_id, zone in self._zones.items():
            # Compter les personnes dans la zone
            persons_in_zone = 0
            person_positions = []
            
            for detection in person_detections:
                # Centre de la bounding box
                bbox = detection.bbox
                center_x = bbox[0] + bbox[2] / 2
                center_y = bbox[1] + bbox[3] / 2
                
                if zone.contains_point((center_x, center_y)):
                    persons_in_zone += 1
                    person_positions.append((center_x, center_y))
            
            # Créer le contexte pour les règles
            rule_context = {
                "camera_id": camera_id,
                "zone_id": zone_id,
                "zone_type": "restricted" if zone.max_persons == 0 else "limited",
                "person_count": persons_in_zone,
                "person_in_zone": persons_in_zone > 0,
                "max_persons": zone.max_persons,
                "duration": self._get_person_duration(camera_id, zone_id, persons_in_zone),
                "timestamp": context.get("timestamp")
            }
            
            # Évaluer les règles
            triggered_rules = self.evaluate_rules(rule_context)
            
            # Générer des événements pour les règles déclenchées
            for rule in triggered_rules:
                if rule.name == "intrusion_zone" and persons_in_zone > 0:
                    # Trouver la première personne dans la zone
                    if person_positions:
                        event = IntrusionDetectedEvent(
                            camera_id=camera_id,
                            confidence=0.9,
                            zone_id=zone_id,
                            bbox=person_detections[0].bbox,
                            frame=frame
                        )
                        self.event_bus.publish(event)
    
    def _get_person_duration(self, camera_id: str, zone_id: str, current_count: int) -> float:
        """
        Calcule la durée de présence des personnes dans une zone.
        
        Args:
            camera_id: ID de la caméra
            zone_id: ID de la zone
            current_count: Nombre actuel de personnes
        
        Returns:
            Durée en secondes
        """
        key = f"{camera_id}_{zone_id}"
        
        if key not in self._person_tracking:
            self._person_tracking[key] = []
        
        tracking = self._person_tracking[key]
        
        # Ajouter l'observation actuelle
        from datetime import datetime
        now = datetime.now()
        tracking.append({
            "timestamp": now,
            "count": current_count
        })
        
        # Nettoyer les observations anciennes (> 5 minutes)
        tracking[:] = [
            t for t in tracking
            if (now - t["timestamp"]).total_seconds() < 300
        ]
        
        # Calculer la durée où des personnes étaient présentes
        if not tracking:
            return 0.0
        
        # Trouver la première observation avec des personnes
        first_with_persons = None
        for t in tracking:
            if t["count"] > 0:
                first_with_persons = t
                break
        
        if first_with_persons:
            return (now - first_with_persons["timestamp"]).total_seconds()
        
        return 0.0
    
    def _generate_alert(self, action: RuleAction, context: Dict[str, Any]):
        """Génère une alerte d'intrusion."""
        from app.events.event_types import AlertGeneratedEvent
        from app.desktop.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
        from datetime import datetime
        
        alert = Alert(
            id=0,  # Sera assigné par la base de données
            camera_id=int(context.get("camera_id", 0)),
            camera_name=f"Camera {context.get('camera_id')}",
            alert_type=AlertType.INTRUSION,
            severity=AlertSeverity.HIGH,
            status=AlertStatus.NEW,
            detected_at=datetime.now(),
            confidence=0.9,
            bbox=(0, 0, 0, 0),
            description=action.parameters.get("message", "Intrusion détectée")
        )
        
        event = AlertGeneratedEvent(alert=alert)
        self.event_bus.publish(event)
