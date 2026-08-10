"""
Journalisation d'audit avec chaîne de hachage pour immuabilité.

Logs d'audit avec chaînage SHA-256.
"""

import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from database import crud, schemas


class AuditLogger:
    """
    Gestionnaire de logs d'audit avec chaîne de hachage.
    
    Formule: H_n = SHA-256(H_{n-1} + données_log_n)
    
    Assure l'immuabilité des logs via chaînage cryptographique.
    """
    
    def __init__(self, db_session=None):
        """
        Initialise le logger d'audit.
        
        Args:
            db_session: Session de base de données (optionnel)
        """
        self.db_session = db_session
        self.previous_hash = self._get_last_hash()
    
    def _get_last_hash(self) -> str:
        """
        Récupère le dernier hash de la chaîne.
        
        Returns:
            Hash précédent ou "0" * 64 si aucun log
        """
        if not self.db_session:
            return "0" * 64
        
        try:
            # Récupérer le dernier log
            last_log = crud.get_audit_logs(self.db_session, skip=0, limit=1)
            
            if last_log:
                return last_log[0].previous_hash or "0" * 64
            
            return "0" * 64
            
        except Exception:
            return "0" * 64
    
    def log_action(
        self,
        user_id: str,
        action: str,
        resource: str = None,
        ip_address: str = None,
        success: bool = True,
        session_id: str = None,
        details: Dict = None
    ) -> str:
        """
        Enregistre une action dans le log d'audit.
        
        Formule: H_n = SHA-256(H_{n-1} + données_log_n)
        
        Args:
            user_id: Identifiant de l'utilisateur
            action: Action effectuée
            resource: Ressource concernée
            ip_address: Adresse IP
            success: Succès de l'action
            session_id: ID de session
            details: Détails additionnels
        
        Returns:
            Hash du log créé
        """
        # Préparer les données du log
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "ip_address": ip_address,
            "success": success,
            "session_id": session_id,
            "details": details or {}
        }
        
        # Sérialiser en JSON
        log_json = json.dumps(log_data, sort_keys=True)
        
        # Calculer le nouveau hash
        new_hash = self._calculate_hash(self.previous_hash, log_json)
        
        # Créer l'entrée de log
        audit_log = schemas.AuditLogCreate(
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            success=success,
            session_id=session_id,
            previous_hash=self.previous_hash,
            details=json.dumps(details) if details else None
        )
        
        # Sauvegarder en base de données
        if self.db_session:
            try:
                crud.create_audit_log(self.db_session, audit_log)
            except Exception as e:
                print(f"Erreur lors de la sauvegarde du log d'audit: {e}")
        
        # Mettre à jour le hash précédent
        self.previous_hash = new_hash
        
        return new_hash
    
    def _calculate_hash(self, previous_hash: str, data: str) -> str:
        """
        Calcule le hash SHA-256.
        
        Formule: H = SHA-256(previous_hash + data)
        
        Args:
            previous_hash: Hash précédent
            data: Données à hacher
        
        Returns:
            Hash hexadécimal (64 caractères)
        """
        combined = previous_hash + data
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def verify_chain_integrity(self) -> bool:
        """
        Vérifie l'intégrité de la chaîne de logs.
        
        Parcourt tous les logs et vérifie que chaque hash correspond
        au calcul à partir du hash précédent.
        
        Returns:
            True si la chaîne est intacte
        """
        if not self.db_session:
            return True
        
        try:
            # Récupérer tous les logs
            logs = crud.get_audit_logs(self.db_session, skip=0, limit=10000)
            
            if not logs:
                return True
            
            # Vérifier le premier log
            expected_hash = "0" * 64
            
            for log in logs:
                # Recalculer le hash attendu
                log_data = {
                    "timestamp": log.timestamp.isoformat(),
                    "user_id": log.user_id,
                    "action": log.action,
                    "resource": log.resource,
                    "ip_address": log.ip_address,
                    "success": log.success,
                    "session_id": log.session_id,
                    "details": json.loads(log.details) if log.details else {}
                }
                
                log_json = json.dumps(log_data, sort_keys=True)
                calculated_hash = self._calculate_hash(expected_hash, log_json)
                
                # Vérifier que le hash stocké correspond
                if log.previous_hash != expected_hash:
                    print(f"Intégrité brisée au log {log.id}: hash précédent incorrect")
                    return False
                
                # Le hash actuel devrait être calculé à partir de ce log
                # Note: Dans une implémentation complète, il faudrait stocker
                # le hash actuel de chaque log, pas seulement le précédent
                
                expected_hash = calculated_hash
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la vérification de l'intégrité: {e}")
            return False
    
    def get_user_activity(self, user_id: str, limit: int = 100) -> List[Dict]:
        """
        Récupère l'activité d'un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            limit: Nombre maximum de logs
        
        Returns:
            Liste des logs de l'utilisateur
        """
        if not self.db_session:
            return []
        
        try:
            logs = crud.get_audit_logs(self.db_session, skip=0, limit=limit)
            
            user_logs = [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "resource": log.resource,
                    "success": log.success,
                    "ip_address": log.ip_address
                }
                for log in logs
                if log.user_id == user_id
            ]
            
            return user_logs
            
        except Exception:
            return []
    
    def export_logs_to_file(self, output_path: Path, start_date: datetime = None, end_date: datetime = None) -> bool:
        """
        Exporte les logs d'audit vers un fichier JSON.
        
        Args:
            output_path: Chemin du fichier de sortie
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
        
        Returns:
            True si export réussi
        """
        if not self.db_session:
            return False
        
        try:
            logs = crud.get_audit_logs(self.db_session, skip=0, limit=10000)
            
            # Filtrer par date
            if start_date or end_date:
                filtered_logs = []
                for log in logs:
                    if start_date and log.timestamp < start_date:
                        continue
                    if end_date and log.timestamp > end_date:
                        continue
                    filtered_logs.append(log)
                logs = filtered_logs
            
            # Convertir en JSON
            export_data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "total_logs": len(logs),
                "logs": [
                    {
                        "id": log.id,
                        "timestamp": log.timestamp.isoformat(),
                        "user_id": log.user_id,
                        "action": log.action,
                        "resource": log.resource,
                        "ip_address": log.ip_address,
                        "success": log.success,
                        "session_id": log.session_id,
                        "previous_hash": log.previous_hash,
                        "details": json.loads(log.details) if log.details else None
                    }
                    for log in logs
                ]
            }
            
            # Écrire le fichier
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export des logs: {e}")
            return False


class SecurityEventLogger:
    """
    Logger spécialisé pour les événements de sécurité.
    """
    
    def __init__(self, audit_logger: AuditLogger):
        """
        Initialise le logger d'événements de sécurité.
        
        Args:
            audit_logger: Instance d'AuditLogger
        """
        self.audit_logger = audit_logger
    
    def log_login_attempt(self, user_id: str, ip_address: str, success: bool, session_id: str = None):
        """Log une tentative de connexion."""
        self.audit_logger.log_action(
            user_id=user_id,
            action="LOGIN_ATTEMPT",
            resource="auth",
            ip_address=ip_address,
            success=success,
            session_id=session_id,
            details={"event_type": "authentication"}
        )
    
    def log_logout(self, user_id: str, session_id: str, ip_address: str = None):
        """Log une déconnexion."""
        self.audit_logger.log_action(
            user_id=user_id,
            action="LOGOUT",
            resource="auth",
            ip_address=ip_address,
            success=True,
            session_id=session_id,
            details={"event_type": "authentication"}
        )
    
    def log_fall_detected(self, user_id: str, person_id: int, camera_id: int, gravity_level: str):
        """Log une détection de chute."""
        self.audit_logger.log_action(
            user_id=user_id,
            action="FALL_DETECTED",
            resource="fall_detection",
            success=True,
            details={
                "event_type": "detection",
                "person_id": person_id,
                "camera_id": camera_id,
                "gravity_level": gravity_level
            }
        )
    
    def log_alert_sent(self, user_id: str, channel: str, recipient: str, fall_event_id: int):
        """Log l'envoi d'une alerte."""
        self.audit_logger.log_action(
            user_id=user_id,
            action="ALERT_SENT",
            resource="alert",
            success=True,
            details={
                "event_type": "notification",
                "channel": channel,
                "recipient": recipient,
                "fall_event_id": fall_event_id
            }
        )
    
    def log_data_access(self, user_id: str, resource: str, resource_id: int = None):
        """Log un accès aux données."""
        self.audit_logger.log_action(
            user_id=user_id,
            action="DATA_ACCESS",
            resource=resource,
            success=True,
            details={
                "event_type": "data_access",
                "resource_id": resource_id
            }
        )
    
    def log_config_change(self, user_id: str, config_key: str, old_value: str, new_value: str):
        """Log un changement de configuration."""
        self.audit_logger.log_action(
            user_id=user_id,
            action="CONFIG_CHANGE",
            resource="config",
            success=True,
            details={
                "event_type": "configuration",
                "config_key": config_key,
                "old_value": old_value,
                "new_value": new_value
            }
        )
    
    def log_permission_denied(self, user_id: str, action: str, resource: str):
        """Log un accès refusé."""
        self.audit_logger.log_action(
            user_id=user_id,
            action="PERMISSION_DENIED",
            resource=resource,
            success=False,
            details={
                "event_type": "authorization",
                "requested_action": action
            }
        )
