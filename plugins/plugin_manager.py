"""
Gestionnaire de plugins.
Charge et gère les plugins de détecteurs, règles et notifications.
"""

from typing import Dict, Any, Optional, List, Type
from pathlib import Path
from abc import ABC, abstractmethod
import importlib
import inspect

from backend.core.logger import get_logger


class Plugin(ABC):
    """
    Classe de base pour tous les plugins.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nom du plugin."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Version du plugin."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description du plugin."""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any] = None):
        """
        Initialise le plugin.
        
        Args:
            config: Configuration du plugin
        """
        pass
    
    @abstractmethod
    def shutdown(self):
        """Arrête le plugin."""
        pass


class DetectorPlugin(Plugin):
    """
    Plugin de détecteur IA.
    """
    
    @abstractmethod
    def detect(self, frame, **kwargs) -> List[Dict[str, Any]]:
        """
        Exécute la détection sur un frame.
        
        Args:
            frame: Frame à traiter
            **kwargs: Arguments supplémentaires
        
        Returns:
            Liste des détections
        """
        pass


class RulePlugin(Plugin):
    """
    Plugin de règle de détection.
    """
    
    @abstractmethod
    def evaluate(self, detections: List[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        """
        Évalue la règle sur des détections.
        
        Args:
            detections: Liste des détections
            context: Contexte d'évaluation
        
        Returns:
            True si la règle est déclenchée
        """
        pass


class NotificationPlugin(Plugin):
    """
    Plugin de canal de notification.
    """
    
    @abstractmethod
    def send(self, message: str, **kwargs) -> bool:
        """
        Envoie une notification.
        
        Args:
            message: Message à envoyer
            **kwargs: Arguments supplémentaires
        
        Returns:
            True si succès
        """
        pass


class PluginManager:
    """
    Gestionnaire de plugins.
    Charge et gère tous les plugins.
    """
    
    _instance = None
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._logger = get_logger(__name__)
        self._plugins_dir = Path(__file__).parent
        
        # Plugins chargés
        self._detectors: Dict[str, DetectorPlugin] = {}
        self._rules: Dict[str, RulePlugin] = {}
        self._notifications: Dict[str, NotificationPlugin] = {}
        
        self._initialized = True
        self._logger.info("PluginManager initialisé")
    
    def load_all(self):
        """Charge tous les plugins disponibles."""
        self._logger.info("Chargement des plugins...")
        
        # Charger les détecteurs
        self._load_plugins("detectors", DetectorPlugin, self._detectors)
        
        # Charger les règles
        self._load_plugins("rules", RulePlugin, self._rules)
        
        # Charger les notifications
        self._load_plugins("notifications", NotificationPlugin, self._notifications)
        
        total = len(self._detectors) + len(self._rules) + len(self._notifications)
        self._logger.info(f"Plugins chargés: {total} (détecteurs: {len(self._detectors)}, règles: {len(self._rules)}, notifications: {len(self._notifications)})")
    
    def _load_plugins(self, subdir: str, plugin_class: Type[Plugin], registry: Dict[str, Plugin]):
        """
        Charge les plugins d'un répertoire.
        
        Args:
            subdir: Sous-répertoire
            plugin_class: Classe de plugin attendue
            registry: Registre des plugins
        """
        plugin_dir = self._plugins_dir / subdir
        
        if not plugin_dir.exists():
            self._logger.debug(f"Répertoire de plugins inexistant: {plugin_dir}")
            return
        
        # Parcourir les fichiers Python
        for py_file in plugin_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            module_name = f"plugins.{subdir}.{py_file.stem}"
            
            try:
                module = importlib.import_module(module_name)
                
                # Trouver les classes de plugin
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, plugin_class) and obj is not plugin_class:
                        plugin = obj()
                        registry[plugin.name] = plugin
                        self._logger.info(f"Plugin chargé: {plugin.name} ({subdir})")
                        
            except Exception as e:
                self._logger.error(f"Erreur chargement plugin {module_name}: {e}")
    
    def get_detector(self, name: str) -> Optional[DetectorPlugin]:
        """
        Retourne un détecteur par son nom.
        
        Args:
            name: Nom du détecteur
        
        Returns:
            Plugin ou None
        """
        return self._detectors.get(name)
    
    def get_rule(self, name: str) -> Optional[RulePlugin]:
        """
        Retourne une règle par son nom.
        
        Args:
            name: Nom de la règle
        
        Returns:
            Plugin ou None
        """
        return self._rules.get(name)
    
    def get_notification(self, name: str) -> Optional[NotificationPlugin]:
        """
        Retourne une notification par son nom.
        
        Args:
            name: Nom de la notification
        
        Returns:
            Plugin ou None
        """
        return self._notifications.get(name)
    
    def get_all_detectors(self) -> Dict[str, DetectorPlugin]:
        """Retourne tous les détecteurs."""
        return self._detectors.copy()
    
    def get_all_rules(self) -> Dict[str, RulePlugin]:
        """Retourne toutes les règles."""
        return self._rules.copy()
    
    def get_all_notifications(self) -> Dict[str, NotificationPlugin]:
        """Retourne toutes les notifications."""
        return self._notifications.copy()
    
    def initialize_plugin(self, name: str, plugin_type: str, config: Dict[str, Any] = None):
        """
        Initialise un plugin spécifique.
        
        Args:
            name: Nom du plugin
            plugin_type: Type de plugin (detector, rule, notification)
            config: Configuration du plugin
        """
        registry_map = {
            "detector": self._detectors,
            "rule": self._rules,
            "notification": self._notifications
        }
        
        registry = registry_map.get(plugin_type)
        if not registry:
            self._logger.error(f"Type de plugin inconnu: {plugin_type}")
            return
        
        plugin = registry.get(name)
        if plugin:
            try:
                plugin.initialize(config)
                self._logger.info(f"Plugin initialisé: {name} ({plugin_type})")
            except Exception as e:
                self._logger.error(f"Erreur initialisation plugin {name}: {e}")
    
    def shutdown_plugin(self, name: str, plugin_type: str):
        """
        Arrête un plugin spécifique.
        
        Args:
            name: Nom du plugin
            plugin_type: Type de plugin (detector, rule, notification)
        """
        registry_map = {
            "detector": self._detectors,
            "rule": self._rules,
            "notification": self._notifications
        }
        
        registry = registry_map.get(plugin_type)
        if not registry:
            self._logger.error(f"Type de plugin inconnu: {plugin_type}")
            return
        
        plugin = registry.get(name)
        if plugin:
            try:
                plugin.shutdown()
                self._logger.info(f"Plugin arrêté: {name} ({plugin_type})")
            except Exception as e:
                self._logger.error(f"Erreur arrêt plugin {name}: {e}")
    
    def reload_plugin(self, name: str, plugin_type: str):
        """
        Recharge un plugin spécifique.
        
        Args:
            name: Nom du plugin
            plugin_type: Type de plugin (detector, rule, notification)
        """
        self.shutdown_plugin(name, plugin_type)
        self.load_all()


def get_plugin_manager() -> PluginManager:
    """
    Fonction utilitaire pour récupérer le PluginManager.
    
    Returns:
        Instance singleton du PluginManager
    """
    if PluginManager._instance is None:
        PluginManager._instance = PluginManager()
    return PluginManager._instance
