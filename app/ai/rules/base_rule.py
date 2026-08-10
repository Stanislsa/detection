"""
Base pour le moteur de règles IA.
Définit l'interface commune pour toutes les règles de détection.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

from app.desktop.workers.detection_worker import DetectionResult
from app.events.event_bus import EventBus
from app.events.event_types import Event, EventType
from app.core.logger import get_logger


@dataclass
class RuleCondition:
    """Condition d'une règle."""
    field: str  # Champ à vérifier (ex: "person_count", "duration")
    operator: str  # Opérateur (ex: ">", "<", "==", ">=", "<=")
    value: Any  # Valeur de comparaison
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Évalue la condition dans un contexte donné.
        
        Args:
            context: Contexte d'évaluation
        
        Returns:
            True si la condition est remplie
        """
        field_value = context.get(self.field)
        
        if field_value is None:
            return False
        
        try:
            if self.operator == ">":
                return field_value > self.value
            elif self.operator == "<":
                return field_value < self.value
            elif self.operator == "==":
                return field_value == self.value
            elif self.operator == ">=":
                return field_value >= self.value
            elif self.operator == "<=":
                return field_value <= self.value
            elif self.operator == "!=":
                return field_value != self.value
            elif self.operator == "in":
                return field_value in self.value
            elif self.operator == "contains":
                return self.value in field_value
            else:
                return False
        except (TypeError, ValueError):
            return False


@dataclass
class RuleAction:
    """Action à exécuter quand une règle est déclenchée."""
    action_type: str  # "generate_alert", "log", "notify"
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class Rule:
    """Règle de détection."""
    name: str
    description: str
    conditions: List[RuleCondition]
    actions: List[RuleAction]
    enabled: bool = True
    cooldown_seconds: int = 60  # Temps minimum entre deux déclenchements
    last_triggered: Optional[datetime] = None
    
    def can_trigger(self) -> bool:
        """
        Vérifie si la règle peut être déclenchée (cooldown).
        
        Returns:
            True si le cooldown est écoulé
        """
        if self.last_triggered is None:
            return True
        
        cooldown_elapsed = (datetime.now() - self.last_triggered).total_seconds()
        return cooldown_elapsed >= self.cooldown_seconds
    
    def trigger(self):
        """Marque la règle comme déclenchée."""
        self.last_triggered = datetime.now()
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Évalue toutes les conditions de la règle.
        
        Args:
            context: Contexte d'évaluation
        
        Returns:
            True si toutes les conditions sont remplies
        """
        if not self.enabled:
            return False
        
        if not self.can_trigger():
            return False
        
        # Toutes les conditions doivent être remplies (AND)
        for condition in self.conditions:
            if not condition.evaluate(context):
                return False
        
        return True


class BaseRuleEngine(ABC):
    """
    Moteur de règles de base.
    Évalue les règles et exécute les actions appropriées.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialise le moteur de règles.
        
        Args:
            event_bus: Instance du bus d'événements
        """
        self.event_bus = event_bus
        self._rules: List[Rule] = []
        self._logger = get_logger(self.__class__.__name__)
    
    def add_rule(self, rule: Rule):
        """
        Ajoute une règle au moteur.
        
        Args:
            rule: Règle à ajouter
        """
        self._rules.append(rule)
        self._logger.info(f"Règle ajoutée: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Supprime une règle du moteur.
        
        Args:
            rule_name: Nom de la règle
        
        Returns:
            True si succès
        """
        for i, rule in enumerate(self._rules):
            if rule.name == rule_name:
                del self._rules[i]
                self._logger.info(f"Règle supprimée: {rule_name}")
                return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """
        Active une règle.
        
        Args:
            rule_name: Nom de la règle
        
        Returns:
            True si succès
        """
        for rule in self._rules:
            if rule.name == rule_name:
                rule.enabled = True
                self._logger.info(f"Règle activée: {rule_name}")
                return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """
        Désactive une règle.
        
        Args:
            rule_name: Nom de la règle
        
        Returns:
            True si succès
        """
        for rule in self._rules:
            if rule.name == rule_name:
                rule.enabled = False
                self._logger.info(f"Règle désactivée: {rule_name}")
                return True
        return False
    
    def get_rules(self) -> List[Rule]:
        """Retourne toutes les règles."""
        return self._rules.copy()
    
    def evaluate_rules(self, context: Dict[str, Any]) -> List[Rule]:
        """
        Évalue toutes les règles dans un contexte donné.
        
        Args:
            context: Contexte d'évaluation
        
        Returns:
            Liste des règles déclenchées
        """
        triggered_rules = []
        
        for rule in self._rules:
            if rule.evaluate(context):
                rule.trigger()
                triggered_rules.append(rule)
                self._execute_actions(rule, context)
        
        return triggered_rules
    
    def _execute_actions(self, rule: Rule, context: Dict[str, Any]):
        """
        Exécute les actions d'une règle déclenchée.
        
        Args:
            rule: Règle déclenchée
            context: Contexte d'évaluation
        """
        for action in rule.actions:
            try:
                self._execute_action(action, context)
            except Exception as e:
                self._logger.error(f"Erreur exécution action {action.action_type}: {e}")
    
    def _execute_action(self, action: RuleAction, context: Dict[str, Any]):
        """
        Exécute une action spécifique.
        
        Args:
            action: Action à exécuter
            context: Contexte d'évaluation
        """
        if action.action_type == "generate_alert":
            self._generate_alert(action, context)
        elif action.action_type == "log":
            self._log_event(action, context)
        elif action.action_type == "notify":
            self._send_notification(action, context)
        else:
            self._logger.warning(f"Type d'action inconnu: {action.action_type}")
    
    def _generate_alert(self, action: RuleAction, context: Dict[str, Any]):
        """Génère une alerte."""
        self._logger.info(f"Génération d'alerte: {action.parameters}")
        # Implémentation spécifique à surcharger
    
    def _log_event(self, action: RuleAction, context: Dict[str, Any]):
        """Log un événement."""
        self._logger.info(f"Log événement: {action.parameters}")
    
    def _send_notification(self, action: RuleAction, context: Dict[str, Any]):
        """Envoie une notification."""
        self._logger.info(f"Notification: {action.parameters}")
    
    @abstractmethod
    def process_detections(self, detections: List[DetectionResult], context: Dict[str, Any]):
        """
        Traite les détections avec le moteur de règles.
        
        Args:
            detections: Liste des détections
            context: Contexte additionnel
        """
        pass
