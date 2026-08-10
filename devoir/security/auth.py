"""
Authentification multi-facteurs (MFA).

Mot de passe Argon2id + TOTP.
"""

import os
import pyotp
import argon2
from typing import Tuple, Optional, Dict
from datetime import datetime, timedelta

from config.constants import (
    MAX_LOGIN_ATTEMPTS, LOCKOUT_DURATION_MINUTES,
    SESSION_DURATION_HOURS
)


class PasswordManager:
    """
    Gestionnaire de mots de passe avec hachage Argon2id.
    
    Formule: hash = Argon2id(mot_de_passe, sel, mémoire=64MB, iterations=3, parallelisme=4)
    """
    
    def __init__(self):
        """Initialise le gestionnaire de mots de passe."""
        # Configuration Argon2id (recommandée par OWASP)
        self.hasher = argon2.PasswordHasher(
            time_cost=3,           # Itérations
            memory_cost=64 * 1024,  # 64 MB
            parallelism=4,         # Parallélisme
            hash_len=32,           # Longueur du hash
            salt_len=16,           # Longueur du sel
            type=argon2.Type.ID     # Argon2id (résistant aux attaques GPU/ASIC)
        )
    
    def hash_password(self, password: str) -> str:
        """
        Hache un mot de passe avec Argon2id.
        
        Args:
            password: Mot de passe en clair
        
        Returns:
            Hash du mot de passe (format: $argon2id$...$...$...)
        """
        return self.hasher.hash(password)
    
    def verify_password(self, password: str, hash_str: str) -> bool:
        """
        Vérifie un mot de passe contre son hash.
        
        Args:
            password: Mot de passe à vérifier
            hash_str: Hash stocké
        
        Returns:
            True si le mot de passe correspond
        """
        try:
            return self.hasher.verify(hash_str, password)
        except argon2.exceptions.VerifyMismatchError:
            return False
        except Exception:
            return False
    
    def check_needs_rehash(self, hash_str: str) -> bool:
        """
        Vérifie si le hash doit être recalculé (changement de paramètres).
        
        Args:
            hash_str: Hash stocké
        
        Returns:
            True si rehash nécessaire
        """
        try:
            return self.hasher.check_needs_rehash(hash_str)
        except Exception:
            return False


class TOTPManager:
    """
    Gestionnaire TOTP (Time-based One-Time Password).
    
    Formule: TOTP = HMAC-SHA1(K, ⌊(T - T0) / X⌋) mod 10^d
    
    Où:
    - K = clé secrète partagée
    - T = timestamp Unix
    - T0 = epoch (0)
    - X = période (30 secondes)
    - d = nombre de chiffres (6)
    """
    
    def __init__(self):
        """Initialise le gestionnaire TOTP."""
        self.period = 30  # 30 secondes par défaut
        self.digits = 6   # 6 chiffres par défaut
    
    def generate_secret(self) -> str:
        """
        Génère une clé secrète TOTP.
        
        Returns:
            Clé secrète en base32
        """
        return pyotp.random_base32()
    
    def generate_totp(self, secret: str) -> str:
        """
        Génère un code TOTP actuel.
        
        Args:
            secret: Clé secrète en base32
        
        Returns:
            Code TOTP à 6 chiffres
        """
        totp = pyotp.TOTP(secret, digits=self.digits, interval=self.period)
        return totp.now()
    
    def verify_totp(self, secret: str, code: str, valid_window: int = 1) -> bool:
        """
        Vérifie un code TOTP.
        
        Args:
            secret: Clé secrète en base32
            code: Code à vérifier
            valid_window: Fenêtre de validité (nombre de périodes avant/après)
        
        Returns:
            True si le code est valide
        """
        totp = pyotp.TOTP(secret, digits=self.digits, interval=self.period)
        return totp.verify(code, valid_window=valid_window)
    
    def get_provisioning_uri(self, secret: str, name: str, issuer: str = "Fall Detection") -> str:
        """
        Génère l'URI de provisionnement pour les apps d'authentification.
        
        Args:
            secret: Clé secrète en base32
            name: Nom de l'utilisateur
            issuer: Nom de l'application
        
        Returns:
            URI otpauth://
        """
        totp = pyotp.TOTP(secret, digits=self.digits, interval=self.period)
        return totp.provisioning_uri(name=name, issuer_name=issuer)


class AuthManager:
    """
    Gestionnaire d'authentification MFA.
    
    Combine mot de passe (Argon2id) et TOTP.
    """
    
    def __init__(self):
        """Initialise le gestionnaire d'authentification."""
        self.password_manager = PasswordManager()
        self.totp_manager = TOTPManager()
        
        # Stockage des tentatives de connexion (en production: utiliser Redis/DB)
        self.login_attempts: Dict[str, int] = {}
        self.lockout_until: Dict[str, datetime] = {}
    
    def register_user(self, password: str) -> Tuple[str, str]:
        """
        Enregistre un nouvel utilisateur.
        
        Args:
            password: Mot de passe
        
        Returns:
            (password_hash, totp_secret)
        """
        password_hash = self.password_manager.hash_password(password)
        totp_secret = self.totp_manager.generate_secret()
        
        return password_hash, totp_secret
    
    def authenticate(
        self,
        user_id: str,
        password: str,
        password_hash: str,
        totp_secret: str,
        totp_code: str
    ) -> Tuple[bool, str]:
        """
        Authentifie un utilisateur avec MFA.
        
        Args:
            user_id: Identifiant de l'utilisateur
            password: Mot de passe fourni
            password_hash: Hash du mot de passe stocké
            totp_secret: Clé secrète TOTP
            totp_code: Code TOTP fourni
        
        Returns:
            (success, message)
        """
        # Vérifier le verrouillage
        if self._is_locked_out(user_id):
            return False, "Compte temporairement verrouillé (trop de tentatives)"
        
        # Vérifier le mot de passe
        if not self.password_manager.verify_password(password, password_hash):
            self._record_failed_attempt(user_id)
            return False, "Mot de passe incorrect"
        
        # Vérifier le TOTP
        if not self.totp_manager.verify_totp(totp_secret, totp_code):
            self._record_failed_attempt(user_id)
            return False, "Code TOTP incorrect"
        
        # Authentification réussie
        self._reset_login_attempts(user_id)
        return True, "Authentification réussie"
    
    def _record_failed_attempt(self, user_id: str):
        """
        Enregistre une tentative de connexion échouée.
        
        Args:
            user_id: Identifiant de l'utilisateur
        """
        if user_id not in self.login_attempts:
            self.login_attempts[user_id] = 0
        
        self.login_attempts[user_id] += 1
        
        # Vérifier si on doit verrouiller
        if self.login_attempts[user_id] >= MAX_LOGIN_ATTEMPTS:
            lockout_time = timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            self.lockout_until[user_id] = datetime.utcnow() + lockout_time
    
    def _reset_login_attempts(self, user_id: str):
        """
        Réinitialise les tentatives de connexion.
        
        Args:
            user_id: Identifiant de l'utilisateur
        """
        if user_id in self.login_attempts:
            del self.login_attempts[user_id]
        if user_id in self.lockout_until:
            del self.lockout_until[user_id]
    
    def _is_locked_out(self, user_id: str) -> bool:
        """
        Vérifie si un compte est verrouillé.
        
        Args:
            user_id: Identifiant de l'utilisateur
        
        Returns:
            True si verrouillé
        """
        if user_id not in self.lockout_until:
            return False
        
        if datetime.utcnow() > self.lockout_until[user_id]:
            # Verrouillage expiré
            del self.lockout_until[user_id]
            return False
        
        return True
    
    def get_remaining_lockout_time(self, user_id: str) -> Optional[int]:
        """
        Retourne le temps de verrouillage restant en secondes.
        
        Args:
            user_id: Identifiant de l'utilisateur
        
        Returns:
            Secondes restantes ou None si non verrouillé
        """
        if user_id not in self.lockout_until:
            return None
        
        remaining = (self.lockout_until[user_id] - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))


class SessionManager:
    """
    Gestionnaire de sessions utilisateur.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de sessions."""
        self.sessions: Dict[str, Dict] = {}
        self.session_duration = timedelta(hours=SESSION_DURATION_HOURS)
    
    def create_session(self, user_id: str) -> str:
        """
        Crée une nouvelle session.
        
        Args:
            user_id: Identifiant de l'utilisateur
        
        Returns:
            Token de session
        """
        session_token = os.urandom(32).hex()
        
        self.sessions[session_token] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + self.session_duration
        }
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[str]:
        """
        Valide une session.
        
        Args:
            session_token: Token de session
        
        Returns:
            user_id si valide, None sinon
        """
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        # Vérifier l'expiration
        if datetime.utcnow() > session["expires_at"]:
            del self.sessions[session_token]
            return None
        
        return session["user_id"]
    
    def revoke_session(self, session_token: str) -> bool:
        """
        Révoque une session.
        
        Args:
            session_token: Token de session
        
        Returns:
            True si révoquée
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False
    
    def revoke_all_user_sessions(self, user_id: str) -> int:
        """
        Révoque toutes les sessions d'un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
        
        Returns:
            Nombre de sessions révoquées
        """
        count = 0
        tokens_to_revoke = []
        
        for token, session in self.sessions.items():
            if session["user_id"] == user_id:
                tokens_to_revoke.append(token)
        
        for token in tokens_to_revoke:
            del self.sessions[token]
            count += 1
        
        return count
    
    def cleanup_expired_sessions(self) -> int:
        """
        Nettoie les sessions expirées.
        
        Returns:
            Nombre de sessions supprimées
        """
        count = 0
        tokens_to_remove = []
        
        for token, session in self.sessions.items():
            if datetime.utcnow() > session["expires_at"]:
                tokens_to_remove.append(token)
        
        for token in tokens_to_remove:
            del self.sessions[token]
            count += 1
        
        return count
