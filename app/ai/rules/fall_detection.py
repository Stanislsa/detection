"""
Règle de détection de chutes.
Détecte les chutes de personnes basées sur l'analyse de pose.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.ai.rules.base_rule import BaseRuleEngine, Rule, RuleCondition, RuleAction
from app.desktop.workers.detection_worker import DetectionResult
from app.events.event_bus import EventBus
from app.events.event_types import FallDetectedEvent, AlertGeneratedEvent
from app.desktop.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from app.core.logger import get_logger


@dataclass
class FallMetrics:
    """Métriques pour la détection de chutes."""
    person_id: str
    camera_id: str
    last_position: tuple = (0, 0)
    current_position: tuple = (0, 0)
    velocity: float = 0.0
    acceleration: float = 0.0
    orientation_angle: float = 0.0  # Angle du corps par rapport à la verticale
    is_horizontal: bool = False
    last_seen: datetime = None
    
    def __post_init__(self):
        if self.last_seen is None:
            self.last_seen = datetime.now()


class FallDetectionRuleEngine(BaseRuleEngine):
    """
    Moteur de règles pour la détection de chutes.
    Analyse la pose et le mouvement pour détecter les chutes.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialise le moteur de règles de détection de chutes.
        
        Args:
            event_bus: Instance du bus d'événements
        """
        super().__init__(event_bus)
        self._person_metrics: Dict[str, FallMetrics] = {}  # Tracking par person_id
        self._fall_confidence_threshold = 0.7
        self._velocity_threshold = 2.0  # m/s
        self._orientation_threshold = 60  # degrés
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Configure les règles par défaut."""
        # Règle: Chute détectée (orientation horizontale + vitesse élevée)
        rule = Rule(
            name="fall_detected",
            description="Détection de chute basée sur l'orientation et la vitesse",
            conditions=[
                RuleCondition(field="is_horizontal", operator="==", value=True),
                RuleCondition(field="velocity", operator=">", value=1.5),
                RuleCondition(field="confidence", operator=">", value=0.7)
            ],
            actions=[
                RuleAction(
                    action_type="generate_alert",
                    parameters={
                        "alert_type": "fall",
                        "severity": "critical",
                        "message": "Chute détectée"
                    }
                )
            ],
            cooldown_seconds=30
        )
        self.add_rule(rule)
        
        # Règle: Chute probable (orientation horizontale seule)
        rule = Rule(
            name="fall_probable",
            description="Chute probable basée sur l'orientation",
            conditions=[
                RuleCondition(field="is_horizontal", operator="==", value=True),
                RuleCondition(field="confidence", operator=">", value=0.5)
            ],
            actions=[
                RuleAction(
                    action_type="generate_alert",
                    parameters={
                        "alert_type": "fall",
                        "severity": "high",
                        "message": "Chute probable détectée"
                    }
                )
            ],
            cooldown_seconds=30
        )
        self.add_rule(rule)
    
    def set_confidence_threshold(self, threshold: float):
        """
        Définit le seuil de confiance pour les chutes.
        
        Args:
            threshold: Seuil de confiance (0.0 - 1.0)
        """
        self._fall_confidence_threshold = max(0.0, min(1.0, threshold))
    
    def set_velocity_threshold(self, threshold: float):
        """
        Définit le seuil de vitesse pour les chutes.
        
        Args:
            threshold: Seuil de vitesse en m/s
        """
        self._velocity_threshold = threshold
    
    def set_orientation_threshold(self, threshold: float):
        """
        Définit le seuil d'orientation pour les chutes.
        
        Args:
            threshold: Seuil d'orientation en degrés
        """
        self._orientation_threshold = threshold
    
    def process_detections(self, detections: List[DetectionResult], context: Dict[str, Any]):
        """
        Traite les détections avec le moteur de règles de chutes.
        
        Args:
            detections: Liste des détections
            context: Contexte additionnel (camera_id, frame, landmarks, etc.)
        """
        camera_id = context.get("camera_id", "")
        frame = context.get("frame")
        landmarks = context.get("landmarks")  # MediaPipe landmarks
        
        # Filtrer les détections de chutes
        fall_detections = [
            d for d in detections
            if d.class_name == "fall"
        ]
        
        if not fall_detections:
            return
        
        for detection in fall_detections:
            # Extraire les métriques de la détection
            confidence = detection.confidence
            bbox = detection.bbox
            additional_data = detection.additional_data or {}
            
            # Calculer l'orientation si landmarks disponibles
            orientation_angle = 0.0
            is_horizontal = False
            
            if landmarks:
                orientation_angle = self._calculate_orientation(landmarks)
                is_horizontal = orientation_angle > self._orientation_threshold
            
            # Calculer la position
            center_x = bbox[0] + bbox[2] / 2
            center_y = bbox[1] + bbox[3] / 2
            
            # Créer ou mettre à jour les métriques de la personne
            person_id = f"{camera_id}_{int(center_x)}_{int(center_y)}"
            
            if person_id not in self._person_metrics:
                self._person_metrics[person_id] = FallMetrics(
                    person_id=person_id,
                    camera_id=camera_id,
                    current_position=(center_x, center_y)
                )
            else:
                metrics = self._person_metrics[person_id]
                metrics.last_position = metrics.current_position
                metrics.current_position = (center_x, center_y)
                metrics.velocity = self._calculate_velocity(
                    metrics.last_position,
                    metrics.current_position,
                    0.033  # ~30 FPS
                )
                metrics.orientation_angle = orientation_angle
                metrics.is_horizontal = is_horizontal
                metrics.last_seen = datetime.now()
            
            # Créer le contexte pour les règles
            rule_context = {
                "camera_id": camera_id,
                "person_id": person_id,
                "is_horizontal": is_horizontal,
                "velocity": self._person_metrics[person_id].velocity,
                "orientation_angle": orientation_angle,
                "confidence": confidence,
                "timestamp": context.get("timestamp")
            }
            
            # Évaluer les règles
            triggered_rules = self.evaluate_rules(rule_context)
            
            # Générer des événements pour les règles déclenchées
            for rule in triggered_rules:
                if rule.name in ["fall_detected", "fall_probable"]:
                    event = FallDetectedEvent(
                        camera_id=camera_id,
                        confidence=confidence,
                        bbox=bbox,
                        frame=frame
                    )
                    self.event_bus.publish(event)
    
    def _calculate_orientation(self, landmarks: List[Dict[str, float]]) -> float:
        """
        Calcule l'angle d'orientation du corps.
        
        Args:
            landmarks: Landmarks MediaPipe
        
        Returns:
            Angle en degrés (0 = vertical, 90 = horizontal)
        """
        try:
            # Utiliser les épaules et les hanches pour calculer l'angle
            # Indices MediaPipe: 11=épaule gauche, 12=épaule droite, 23=hanche gauche, 24=hanche droite
            
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            
            # Calculer le centre des épaules et des hanches
            shoulder_center_x = (left_shoulder["x"] + right_shoulder["x"]) / 2
            shoulder_center_y = (left_shoulder["y"] + right_shoulder["y"]) / 2
            
            hip_center_x = (left_hip["x"] + right_hip["x"]) / 2
            hip_center_y = (left_hip["y"] + right_hip["y"]) / 2
            
            # Calculer l'angle par rapport à la verticale
            dx = hip_center_x - shoulder_center_x
            dy = hip_center_y - shoulder_center_y
            
            angle = abs(90 - (abs(dx) / (abs(dy) + 0.001)) * 90)
            
            return min(90, angle)
            
        except (IndexError, KeyError, ZeroDivisionError):
            return 0.0
    
    def _calculate_velocity(self, last_pos: tuple, current_pos: tuple, dt: float) -> float:
        """
        Calcule la vitesse de déplacement.
        
        Args:
            last_pos: Position précédente (x, y)
            current_pos: Position actuelle (x, y)
            dt: Intervalle de temps en secondes
        
        Returns:
            Vitesse en pixels/seconde
        """
        dx = current_pos[0] - last_pos[0]
        dy = current_pos[1] - last_pos[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        return distance / dt if dt > 0 else 0.0
    
    def _generate_alert(self, action: RuleAction, context: Dict[str, Any]):
        """Génère une alerte de chute."""
        alert = Alert(
            id=0,
            camera_id=int(context.get("camera_id", 0)),
            camera_name=f"Camera {context.get('camera_id')}",
            alert_type=AlertType.FALL,
            severity=AlertSeverity.CRITICAL if action.parameters.get("severity") == "critical" else AlertSeverity.HIGH,
            status=AlertStatus.NEW,
            detected_at=datetime.now(),
            confidence=context.get("confidence", 0.0),
            bbox=(0, 0, 0, 0),
            description=action.parameters.get("message", "Chute détectée")
        )
        
        event = AlertGeneratedEvent(alert=alert)
        self.event_bus.publish(event)
    
    def cleanup_old_metrics(self, max_age_seconds: int = 300):
        """
        Nettoie les métriques anciennes.
        
        Args:
            max_age_seconds: Âge maximum en secondes
        """
        now = datetime.now()
        to_remove = []
        
        for person_id, metrics in self._person_metrics.items():
            if (now - metrics.last_seen).total_seconds() > max_age_seconds:
                to_remove.append(person_id)
        
        for person_id in to_remove:
            del self._person_metrics[person_id]
        
        if to_remove:
            self._logger.debug(f"Nettoyage de {len(to_remove)} métriques anciennes")
