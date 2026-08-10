"""
Gestionnaire de traductions pour l'internationalisation.
Supporte le français et l'anglais avec chargement dynamique.
"""

from typing import Dict, Optional
from enum import Enum
from PyQt6.QtCore import QLocale, QTranslator

from app.core.logger import get_logger


class Language(Enum):
    """Langues supportées."""
    FRENCH = "fr"
    ENGLISH = "en"


class TranslationManager:
    """
    Gestionnaire de traductions avec dictionnaires.
    Alternative légère à Qt Linguist pour les traductions simples.
    """
    
    _instance = None
    
    # Dictionnaires de traductions
    _translations = {
        Language.FRENCH: {
            # Application
            "app_name": "Surveillance IA",
            "app_title": "Système de Surveillance Intelligent",
            
            # Navigation
            "nav_dashboard": "Tableau de bord",
            "nav_alerts": "Alertes",
            "nav_cameras": "Caméras",
            "nav_statistics": "Statistiques",
            "nav_users": "Utilisateurs",
            "nav_settings": "Paramètres",
            "nav_logout": "Déconnexion",
            
            # Dashboard
            "dashboard_title": "Tableau de bord",
            "dashboard_live": "Vue en direct",
            "dashboard_start": "Démarrer",
            "dashboard_stop": "Arrêter",
            "dashboard_capture": "Capturer",
            "dashboard_record": "Enregistrer",
            "dashboard_settings": "Paramètres",
            "dashboard_cameras_online": "Caméras en ligne",
            "dashboard_total_alerts": "Alertes totales",
            "dashboard_detections_today": "Détections aujourd'hui",
            "dashboard_system_status": "Statut système",
            
            # Alerts
            "alerts_title": "Alertes",
            "alerts_search": "Rechercher...",
            "alerts_filter_severity": "Filtrer par gravité",
            "alerts_filter_status": "Filtrer par statut",
            "alerts_export": "Exporter",
            "alerts_date": "Date",
            "alerts_time": "Heure",
            "alerts_camera": "Caméra",
            "alerts_type": "Type",
            "alerts_severity": "Gravité",
            "alerts_status": "Statut",
            "alerts_actions": "Actions",
            "alerts_view": "Voir",
            "alerts_delete": "Supprimer",
            
            # Alert Types
            "alert_type_fall": "Chute détectée",
            "alert_type_intrusion": "Intrusion",
            "alert_type_movement": "Mouvement suspect",
            "alert_type_abnormal": "Activité anormale",
            "alert_type_system": "Système",
            
            # Alert Severity
            "severity_critical": "Critique",
            "severity_high": "Élevée",
            "severity_medium": "Moyenne",
            "severity_low": "Faible",
            
            # Alert Status
            "status_new": "Nouveau",
            "status_in_progress": "En cours",
            "status_resolved": "Résolu",
            "status_false_positive": "Faux positif",
            
            # Cameras
            "cameras_title": "Caméras",
            "cameras_add": "Ajouter une caméra",
            "cameras_refresh": "Actualiser",
            "cameras_name": "Nom",
            "cameras_source": "Source",
            "cameras_status": "Statut",
            "cameras_online": "En ligne",
            "cameras_offline": "Hors ligne",
            "cameras_edit": "Modifier",
            "cameras_delete": "Supprimer",
            "cameras_config": "Configurer",
            
            # Statistics
            "statistics_title": "Statistiques",
            "statistics_alerts": "Alertes",
            "statistics_detections": "Détections",
            "statistics_cameras": "Caméras",
            "statistics_storage": "Stockage",
            "statistics_today": "Aujourd'hui",
            "statistics_week": "Cette semaine",
            "statistics_month": "Ce mois",
            
            # Users
            "users_title": "Utilisateurs",
            "users_add": "Ajouter un utilisateur",
            "users_search": "Rechercher un utilisateur...",
            "users_name": "Nom",
            "users_email": "Email",
            "users_role": "Rôle",
            "users_last_login": "Dernière connexion",
            "users_actions": "Actions",
            "users_role_admin": "Administrateur",
            "users_role_operator": "Opérateur",
            "users_role_viewer": "Visualiseur",
            
            # Settings
            "settings_title": "Paramètres",
            "settings_general": "Général",
            "settings_ai": "Intelligence Artificielle",
            "settings_cameras": "Caméras",
            "settings_notifications": "Notifications",
            "settings_security": "Sécurité",
            "settings_database": "Base de données",
            "settings_language": "Langue",
            "settings_theme": "Thème",
            "settings_theme_dark": "Sombre",
            "settings_theme_light": "Clair",
            
            # Login
            "login_title": "Connexion",
            "login_username": "Nom d'utilisateur",
            "login_password": "Mot de passe",
            "login_mfa_code": "Code MFA",
            "login_button": "Se connecter",
            "login_forgot_password": "Mot de passe oublié ?",
            "login_remember_me": "Se souvenir de moi",
            
            # Common
            "common_yes": "Oui",
            "common_no": "Non",
            "common_ok": "OK",
            "common_cancel": "Annuler",
            "common_save": "Enregistrer",
            "common_delete": "Supprimer",
            "common_edit": "Modifier",
            "common_add": "Ajouter",
            "common_search": "Rechercher",
            "common_filter": "Filtrer",
            "common_export": "Exporter",
            "common_import": "Importer",
            "common_loading": "Chargement...",
            "common_error": "Erreur",
            "common_success": "Succès",
            "common_warning": "Avertissement",
            "common_info": "Information",
            
            # Messages
            "msg_camera_added": "Caméra ajoutée avec succès",
            "msg_camera_deleted": "Caméra supprimée avec succès",
            "msg_camera_updated": "Caméra mise à jour avec succès",
            "msg_user_added": "Utilisateur ajouté avec succès",
            "msg_user_deleted": "Utilisateur supprimé avec succès",
            "msg_login_success": "Connexion réussie",
            "msg_login_failed": "Échec de la connexion",
            "msg_logout_success": "Déconnexion réussie",
            "msg_settings_saved": "Paramètres enregistrés",
        },
        Language.ENGLISH: {
            # Application
            "app_name": "Surveillance AI",
            "app_title": "Intelligent Surveillance System",
            
            # Navigation
            "nav_dashboard": "Dashboard",
            "nav_alerts": "Alerts",
            "nav_cameras": "Cameras",
            "nav_statistics": "Statistics",
            "nav_users": "Users",
            "nav_settings": "Settings",
            "nav_logout": "Logout",
            
            # Dashboard
            "dashboard_title": "Dashboard",
            "dashboard_live": "Live View",
            "dashboard_start": "Start",
            "dashboard_stop": "Stop",
            "dashboard_capture": "Capture",
            "dashboard_record": "Record",
            "dashboard_settings": "Settings",
            "dashboard_cameras_online": "Cameras Online",
            "dashboard_total_alerts": "Total Alerts",
            "dashboard_detections_today": "Detections Today",
            "dashboard_system_status": "System Status",
            
            # Alerts
            "alerts_title": "Alerts",
            "alerts_search": "Search...",
            "alerts_filter_severity": "Filter by severity",
            "alerts_filter_status": "Filter by status",
            "alerts_export": "Export",
            "alerts_date": "Date",
            "alerts_time": "Time",
            "alerts_camera": "Camera",
            "alerts_type": "Type",
            "alerts_severity": "Severity",
            "alerts_status": "Status",
            "alerts_actions": "Actions",
            "alerts_view": "View",
            "alerts_delete": "Delete",
            
            # Alert Types
            "alert_type_fall": "Fall Detected",
            "alert_type_intrusion": "Intrusion",
            "alert_type_movement": "Suspicious Movement",
            "alert_type_abnormal": "Abnormal Activity",
            "alert_type_system": "System",
            
            # Alert Severity
            "severity_critical": "Critical",
            "severity_high": "High",
            "severity_medium": "Medium",
            "severity_low": "Low",
            
            # Alert Status
            "status_new": "New",
            "status_in_progress": "In Progress",
            "status_resolved": "Resolved",
            "status_false_positive": "False Positive",
            
            # Cameras
            "cameras_title": "Cameras",
            "cameras_add": "Add Camera",
            "cameras_refresh": "Refresh",
            "cameras_name": "Name",
            "cameras_source": "Source",
            "cameras_status": "Status",
            "cameras_online": "Online",
            "cameras_offline": "Offline",
            "cameras_edit": "Edit",
            "cameras_delete": "Delete",
            "cameras_config": "Configure",
            
            # Statistics
            "statistics_title": "Statistics",
            "statistics_alerts": "Alerts",
            "statistics_detections": "Detections",
            "statistics_cameras": "Cameras",
            "statistics_storage": "Storage",
            "statistics_today": "Today",
            "statistics_week": "This Week",
            "statistics_month": "This Month",
            
            # Users
            "users_title": "Users",
            "users_add": "Add User",
            "users_search": "Search user...",
            "users_name": "Name",
            "users_email": "Email",
            "users_role": "Role",
            "users_last_login": "Last Login",
            "users_actions": "Actions",
            "users_role_admin": "Administrator",
            "users_role_operator": "Operator",
            "users_role_viewer": "Viewer",
            
            # Settings
            "settings_title": "Settings",
            "settings_general": "General",
            "settings_ai": "Artificial Intelligence",
            "settings_cameras": "Cameras",
            "settings_notifications": "Notifications",
            "settings_security": "Security",
            "settings_database": "Database",
            "settings_language": "Language",
            "settings_theme": "Theme",
            "settings_theme_dark": "Dark",
            "settings_theme_light": "Light",
            
            # Login
            "login_title": "Login",
            "login_username": "Username",
            "login_password": "Password",
            "login_mfa_code": "MFA Code",
            "login_button": "Sign In",
            "login_forgot_password": "Forgot password?",
            "login_remember_me": "Remember me",
            
            # Common
            "common_yes": "Yes",
            "common_no": "No",
            "common_ok": "OK",
            "common_cancel": "Cancel",
            "common_save": "Save",
            "common_delete": "Delete",
            "common_edit": "Edit",
            "common_add": "Add",
            "common_search": "Search",
            "common_filter": "Filter",
            "common_export": "Export",
            "common_import": "Import",
            "common_loading": "Loading...",
            "common_error": "Error",
            "common_success": "Success",
            "common_warning": "Warning",
            "common_info": "Information",
            
            # Messages
            "msg_camera_added": "Camera added successfully",
            "msg_camera_deleted": "Camera deleted successfully",
            "msg_camera_updated": "Camera updated successfully",
            "msg_user_added": "User added successfully",
            "msg_user_deleted": "User deleted successfully",
            "msg_login_success": "Login successful",
            "msg_login_failed": "Login failed",
            "msg_logout_success": "Logout successful",
            "msg_settings_saved": "Settings saved",
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._current_language = Language.FRENCH
            self._logger = get_logger(__name__)
            self._initialized = True
    
    def set_language(self, language: Language):
        """
        Définit la langue courante.
        
        Args:
            language: Langue à utiliser
        """
        self._current_language = language
        self._logger.info(f"Langue changée: {language.value}")
    
    def get_language(self) -> Language:
        """Retourne la langue courante."""
        return self._current_language
    
    def translate(self, key: str, default: Optional[str] = None) -> str:
        """
        Traduit une clé dans la langue courante.
        
        Args:
            key: Clé de traduction
            default: Texte par défaut si la clé n'existe pas
        
        Returns:
            Texte traduit ou le défaut
        """
        translations = self._translations.get(self._current_language, {})
        text = translations.get(key)
        
        if text is None:
            # Essayer dans l'autre langue comme fallback
            for lang in Language:
                if lang != self._current_language:
                    fallback = self._translations.get(lang, {}).get(key)
                    if fallback:
                        self._logger.warning(f"Traduction manquante pour '{key}' en {self._current_language.value}, utilisation du fallback")
                        return fallback
            
            # Utiliser le défaut ou la clé
            if default:
                self._logger.warning(f"Traduction manquante pour '{key}', utilisation du défaut")
                return default
            else:
                self._logger.warning(f"Traduction manquante pour '{key}', utilisation de la clé")
                return key
        
        return text
    
    def t(self, key: str, default: Optional[str] = None) -> str:
        """
        Raccourci pour translate().
        
        Args:
            key: Clé de traduction
            default: Texte par défaut
        
        Returns:
            Texte traduit
        """
        return self.translate(key, default)
    
    def get_available_languages(self) -> list:
        """Retourne la liste des langues disponibles."""
        return list(Language)


def get_translator() -> TranslationManager:
    """
    Fonction utilitaire pour récupérer le TranslationManager.
    
    Returns:
        Instance singleton du TranslationManager
    """
    return TranslationManager()


def t(key: str, default: Optional[str] = None) -> str:
    """
    Fonction globale de traduction.
    
    Args:
        key: Clé de traduction
        default: Texte par défaut
    
    Returns:
        Texte traduit
    """
    return get_translator().translate(key, default)
