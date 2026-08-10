"""
Modèle User - Utilisateur du système d'authentification.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Optionnel
    totp_secret_encrypted = Column(Text, nullable=True)  # Secret TOTP chiffré
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations RBAC
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    
    def set_password(self, password_hash: str):
        """Définit le hash du mot de passe."""
        self.password_hash = password_hash
    
    def check_password(self, password_hash: str) -> bool:
        """Vérifie si le hash correspond."""
        return self.password_hash == password_hash
    
    def is_locked(self) -> bool:
        """Vérifie si le compte est verrouillé."""
        if not self.locked_until:
            return False
        if datetime.utcnow() > self.locked_until:
            self.locked_until = None
            self.failed_login_attempts = 0
            return False
        return True
    
    def increment_failed_attempts(self, lockout_minutes: int = 15):
        """Incrémente les tentatives échouées et verrouille si nécessaire."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)
    
    def reset_failed_attempts(self):
        """Réinitialise les tentatives échouées."""
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def has_permission(self, permission_name: str) -> bool:
        """Vérifie si l'utilisateur a une permission spécifique."""
        if self.is_admin:
            return True
        for role in self.roles:
            for perm in role.permissions:
                if perm.name == permission_name:
                    return True
        return False
    
    def has_role(self, role_name: str) -> bool:
        """Vérifie si l'utilisateur a un rôle spécifique."""
        return any(role.name == role_name for role in self.roles)
