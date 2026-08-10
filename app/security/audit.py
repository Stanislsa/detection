"""
Logs d'audit immuables avec chaîne de hachage SHA-256.
"""

import hashlib
import json
from datetime import datetime
from typing import Optional

from app.models.base import get_db_session
from app.models.audit_log import AuditLog


class AuditManager:
    """
    Gestion des logs d'audit.
    
    Immuabilité garantie par chaîne de hachage :
    H_n = SHA-256(H_{n-1} + données_log_n)
    """
    
    def __init__(self):
        self._last_hash = "0" * 64  # Genesis hash
    
    def _compute_hash(self, data: dict, previous_hash: str) -> str:
        """
        Calcule le hash du log.
        H = SHA-256(H_prev + JSON(data))
        """
        content = previous_hash + json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def log(self, user_id: str, action: str, resource: str,
            ip_address: str, success: bool, details: Optional[dict] = None,
            session_id: Optional[str] = None):
        """
        Enregistre un événement d'audit.
        """
        with get_db_session() as db:
            # Récupération du dernier hash
            last_log = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
            prev_hash = last_log.current_hash if last_log else self._last_hash
            
            # Préparation des données
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "action": action,
                "resource": resource,
                "success": success
            }
            
            # Calcul du hash
            current_hash = self._compute_hash(log_data, prev_hash)
            
            # Création du log
            audit = AuditLog(
                user_id=user_id,
                action=action,
                resource=resource,
                ip_address=ip_address,
                success=success,
                session_id=session_id,
                previous_hash=prev_hash,
                current_hash=current_hash,
                details=json.dumps(details) if details else None
            )
            
            db.add(audit)
            db.commit()
            
            return audit
