"""
Chargeur de configuration unique.
Valide et charge tous les fichiers de configuration au démarrage.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dataclasses import dataclass

from app.core.logger import get_logger
from app.core.exceptions import ConfigException


@dataclass
class ConfigSchema:
    """Schéma de validation pour un fichier de configuration."""
    required_fields: list
    optional_fields: list = None
    field_types: dict = None
    
    def __post_init__(self):
        if self.optional_fields is None:
            self.optional_fields = []
        if self.field_types is None:
            self.field_types = {}


class ConfigLoader:
    """
    Chargeur de configuration unique.
    Valide et charge tous les fichiers YAML.
    """
    
    _instance = None
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._logger = get_logger(__name__)
        self._config_dir = Path(__file__).parent.parent.parent / "config"
        self._configs: Dict[str, Dict[str, Any]] = {}
        
        # Schémas de validation
        self._schemas = {
            "application": ConfigSchema(
                required_fields=["application"],
                field_types={"application": dict}
            ),
            "cameras": ConfigSchema(
                required_fields=["cameras"],
                field_types={"cameras": dict}
            ),
            "ai": ConfigSchema(
                required_fields=["ai"],
                field_types={"ai": dict}
            ),
            "notifications": ConfigSchema(
                required_fields=["notifications"],
                field_types={"notifications": dict}
            ),
            "storage": ConfigSchema(
                required_fields=["storage"],
                field_types={"storage": dict}
            ),
            "logging": ConfigSchema(
                required_fields=["logging"],
                field_types={"logging": dict}
            )
        }
        
        self._initialized = True
    
    def load_all(self) -> bool:
        """
        Charge et valide tous les fichiers de configuration.
        
        Returns:
            True si succès
        """
        self._logger.info("Chargement des fichiers de configuration...")
        
        success = True
        
        for config_name in self._schemas.keys():
            try:
                config = self.load(config_name)
                if config:
                    self._configs[config_name] = config
                    self._logger.info(f"Configuration chargée: {config_name}.yaml")
                else:
                    self._logger.warning(f"Configuration vide: {config_name}.yaml")
                    success = False
            except Exception as e:
                self._logger.error(f"Erreur chargement {config_name}.yaml: {e}")
                success = False
        
        if success:
            self._logger.info("Toutes les configurations chargées avec succès")
        else:
            self._logger.warning("Certaines configurations n'ont pas pu être chargées")
        
        return success
    
    def load(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Charge un fichier de configuration spécifique.
        
        Args:
            config_name: Nom du fichier (sans extension)
        
        Returns:
            Configuration ou None
        """
        config_path = self._config_dir / f"{config_name}.yaml"
        
        if not config_path.exists():
            self._logger.error(f"Fichier de configuration introuvable: {config_path}")
            raise ConfigException(f"Fichier de configuration introuvable: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                self._logger.error(f"Fichier de configuration vide: {config_path}")
                raise ConfigException(f"Fichier de configuration vide: {config_path}")
            
            # Valider la configuration
            self._validate(config_name, config)
            
            return config
            
        except yaml.YAMLError as e:
            self._logger.error(f"Erreur parsing YAML {config_path}: {e}")
            raise ConfigException(f"Erreur parsing YAML: {e}")
    
    def _validate(self, config_name: str, config: Dict[str, Any]):
        """
        Valide une configuration selon son schéma.
        
        Args:
            config_name: Nom de la configuration
            config: Configuration à valider
        """
        schema = self._schemas.get(config_name)
        
        if not schema:
            self._logger.warning(f"Aucun schéma pour {config_name}, validation ignorée")
            return
        
        # Vérifier les champs requis
        for field in schema.required_fields:
            if field not in config:
                raise ConfigException(f"Champ requis manquant: {field} dans {config_name}")
        
        # Vérifier les types
        for field, expected_type in schema.field_types.items():
            if field in config and not isinstance(config[field], expected_type):
                raise ConfigException(
                    f"Type invalide pour {field}: attendu {expected_type}, "
                    f"reçu {type(config[field])} dans {config_name}"
                )
    
    def get(self, config_name: str, key: str = None, default: Any = None) -> Any:
        """
        Retourne une valeur de configuration.
        
        Args:
            config_name: Nom de la configuration
            key: Clé (optionnel)
            default: Valeur par défaut
        
        Returns:
            Valeur de configuration
        """
        config = self._configs.get(config_name)
        
        if config is None:
            return default
        
        if key is None:
            return config
        
        keys = key.split(".")
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_application_config(self) -> Dict[str, Any]:
        """Retourne la configuration de l'application."""
        return self._configs.get("application", {})
    
    def get_cameras_config(self) -> Dict[str, Any]:
        """Retourne la configuration des caméras."""
        return self._configs.get("cameras", {})
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Retourne la configuration de l'IA."""
        return self._configs.get("ai", {})
    
    def get_notifications_config(self) -> Dict[str, Any]:
        """Retourne la configuration des notifications."""
        return self._configs.get("notifications", {})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Retourne la configuration du stockage."""
        return self._configs.get("storage", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Retourne la configuration de la journalisation."""
        return self._configs.get("logging", {})
    
    def reload(self, config_name: str = None) -> bool:
        """
        Recharge une ou toutes les configurations.
        
        Args:
            config_name: Nom de la configuration (None = toutes)
        
        Returns:
            True si succès
        """
        if config_name:
            try:
                config = self.load(config_name)
                self._configs[config_name] = config
                self._logger.info(f"Configuration rechargée: {config_name}.yaml")
                return True
            except Exception as e:
                self._logger.error(f"Erreur rechargement {config_name}.yaml: {e}")
                return False
        else:
            return self.load_all()
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Retourne toutes les configurations."""
        return self._configs.copy()


def get_config_loader() -> ConfigLoader:
    """
    Fonction utilitaire pour récupérer le ConfigLoader.
    
    Returns:
        Instance singleton du ConfigLoader
    """
    if ConfigLoader._instance is None:
        ConfigLoader._instance = ConfigLoader()
    return ConfigLoader._instance
