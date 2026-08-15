"""
Audit logging for security and compliance.
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.core.logger import get_logger
from backend.database.crud import create_audit_log

logger = get_logger(__name__)


class AuditLogger:
    """
    Audit logger for security and compliance tracking.
    
    Logs all important actions with user context, IP addresses,
    and maintains chain of hashes for integrity verification.
    """
    
    def __init__(self):
        """Initialize audit logger."""
        self._previous_hash = None
    
    def log_action(
        self,
        db: Session,
        user_id: Optional[int],
        username: Optional[str],
        action: str,
        resource: Optional[str] = None,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log an audit action.
        
        Args:
            db: Database session
            user_id: User ID
            username: Username
            action: Action performed
            resource: Resource type
            resource_id: Resource ID
            ip_address: Client IP address
            user_agent: Client user agent
            session_id: Session ID
            success: Whether action succeeded
            error_message: Error message if failed
            details: Additional details
        """
        try:
            # Calculate current hash for integrity chain
            audit_data = {
                "user_id": user_id,
                "username": username,
                "action": action,
                "resource": resource,
                "resource_id": resource_id,
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            current_hash = self._calculate_hash(audit_data, self._previous_hash)
            
            # Create audit log entry
            audit_log_data = {
                "user_id": user_id,
                "username": username,
                "action": action,
                "resource": resource,
                "resource_id": resource_id,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "session_id": session_id,
                "success": success,
                "error_message": error_message,
                "previous_hash": self._previous_hash,
                "details": details or {}
            }
            
            create_audit_log(db, audit_log_data)
            
            # Update previous hash for chain
            self._previous_hash = current_hash
            
            logger.info(f"Audit log: {action} by {username} on {resource}")
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
    
    def _calculate_hash(self, data: Dict[str, Any], previous_hash: Optional[str] = None) -> str:
        """
        Calculate hash for audit entry integrity.
        
        Args:
            data: Audit data
            previous_hash: Previous hash in chain
        
        Returns:
            Hash string
        """
        hash_input = json.dumps(data, sort_keys=True).encode()
        if previous_hash:
            hash_input = hash_input + previous_hash.encode()
        
        return hashlib.sha256(hash_input).hexdigest()
    
    def verify_integrity(self, db: Session) -> bool:
        """
        Verify audit log integrity by checking hash chain.
        
        Args:
            db: Database session
        
        Returns:
            True if integrity verified
        """
        from backend.database.crud import get_audit_logs
        
        try:
            logs = get_audit_logs(db, skip=0, limit=10000)
            
            previous_hash = None
            for log in logs:
                # Reconstruct hash
                audit_data = {
                    "user_id": log.user_id,
                    "username": log.username,
                    "action": log.action,
                    "resource": log.resource,
                    "resource_id": log.resource_id,
                    "ip_address": log.ip_address,
                    "timestamp": log.timestamp.isoformat()
                }
                
                expected_hash = self._calculate_hash(audit_data, previous_hash)
                
                if log.current_hash != expected_hash:
                    logger.error(f"Audit integrity check failed at log {log.id}")
                    return False
                
                previous_hash = log.current_hash
            
            logger.info("Audit integrity verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Audit integrity verification failed: {e}")
            return False


# Global audit logger instance
audit_logger = AuditLogger()
