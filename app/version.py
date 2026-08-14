"""
Versionnement centralisé de l'application.
Contient les versions de l'application, du modèle IA, du schéma de base de données et du numéro de build.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class VersionInfo:
    """Informations de version de l'application."""
    # Version de l'application
    app_version: str = "1.0.0"
    app_name: str = "SentinelAI"
    
    # Version du modèle IA
    ai_model_version: str = "1.0.0"
    ai_model_name: str = "yolo11n.pt"

    # Version du schéma de base de données
    db_schema_version: str = "1.0.0"

    # Numéro de build
    build_number: str = "1"
    build_date: str = None

    # Informations supplémentaires
    environment: str = "development"  # development, staging, production
    python_version: str = "3.10-3.11"
    
    def __post_init__(self):
        if self.build_date is None:
            self.build_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_full_version(self) -> str:
        """
        Retourne la version complète.
        
        Returns:
            Version complète (app.version.build)
        """
        return f"{self.app_version}.{self.build_number}"
    
    def get_user_agent(self) -> str:
        """
        Retourne le user agent pour les requêtes HTTP.
        
        Returns:
            User agent string
        """
        return f"{self.app_name}/{self.app_version} (Build {self.build_number})"
    
    def to_dict(self) -> dict:
        """
        Retourne les informations de version sous forme de dictionnaire.
        
        Returns:
            Dictionnaire de version
        """
        return {
            "app_version": self.app_version,
            "app_name": self.app_name,
            "ai_model_version": self.ai_model_version,
            "ai_model_name": self.ai_model_name,
            "db_schema_version": self.db_schema_version,
            "build_number": self.build_number,
            "build_date": self.build_date,
            "environment": self.environment,
            "python_version": self.python_version
        }


# Instance singleton de version
_version_info = VersionInfo()


def get_version() -> VersionInfo:
    """
    Retourne les informations de version.
    
    Returns:
        Instance de VersionInfo
    """
    return _version_info


def get_app_version() -> str:
    """
    Retourne la version de l'application.
    
    Returns:
        Version de l'application
    """
    return _version_info.app_version


def get_full_version() -> str:
    """
    Retourne la version complète.
    
    Returns:
        Version complète
    """
    return _version_info.get_full_version()


def get_user_agent() -> str:
    """
    Retourne le user agent.
    
    Returns:
        User agent string
    """
    return _version_info.get_user_agent()


def set_environment(environment: str):
    """
    Définit l'environnement.
    
    Args:
        environment: Environnement (development, staging, production)
    """
    _version_info.environment = environment


def set_build_number(build_number: str):
    """
    Définit le numéro de build.
    
    Args:
        build_number: Numéro de build
    """
    _version_info.build_number = build_number


def set_ai_model_version(model_version: str, model_name: str):
    """
    Définit la version du modèle IA.
    
    Args:
        model_version: Version du modèle
        model_name: Nom du modèle
    """
    _version_info.ai_model_version = model_version
    _version_info.ai_model_name = model_name


def set_db_schema_version(schema_version: str):
    """
    Définit la version du schéma de base de données.
    
    Args:
        schema_version: Version du schéma
    """
    _version_info.db_schema_version = schema_version
