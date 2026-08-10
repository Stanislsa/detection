"""
Authentification JWT + MFA TOTP.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import qrcode
import io
import base64
import secrets

from app.config import settings


# Contexte de hachage Argon2id
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class SessionManager:
    """
    Gestionnaire de sessions utilisateur.
    
    Stocke les sessions en mémoire (en production: utiliser Redis ou DB).
    """
    
    def __init__(self):
        """Initialise le gestionnaire de sessions."""
        self.sessions: Dict[str, Dict] = {}
        self.session_duration = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    def create_session(self, user_id: int, username: str) -> str:
        """
        Crée une nouvelle session.
        
        Args:
            user_id: ID de l'utilisateur
            username: Nom d'utilisateur
        
        Returns:
            Token de session
        """
        session_token = secrets.token_urlsafe(32)
        
        self.sessions[session_token] = {
            "user_id": user_id,
            "username": username,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + self.session_duration,
            "ip_address": None,  # À définir lors de la création
            "user_agent": None
        }
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        Valide une session.
        
        Args:
            session_token: Token de session
        
        Returns:
            Données de session si valide, None sinon
        """
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        # Vérifier l'expiration
        if datetime.utcnow() > session["expires_at"]:
            del self.sessions[session_token]
            return None
        
        return session
    
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
    
    def revoke_all_user_sessions(self, user_id: int) -> int:
        """
        Révoque toutes les sessions d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
        
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
    
    def get_user_sessions(self, user_id: int) -> list:
        """
        Retourne toutes les sessions actives d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
        
        Returns:
            Liste des sessions
        """
        return [
            {
                "token": token,
                "created_at": session["created_at"].isoformat(),
                "expires_at": session["expires_at"].isoformat(),
                "ip_address": session["ip_address"]
            }
            for token, session in self.sessions.items()
            if session["user_id"] == user_id and datetime.utcnow() <= session["expires_at"]
        ]


class AuthManager:
    """
    Gestion de l'authentification :
    - Hachage des mots de passe (Argon2id)
    - Génération/validation JWT
    - MFA TOTP (RFC 6238)
    - Lockout anti-brute force
    """
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
    
    # ─── HASH MOT DE PASSE ───
    
    def hash_password(self, password: str) -> str:
        """Hache un mot de passe avec Argon2id."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe."""
        return pwd_context.verify(plain_password, hashed_password)
    
    # ─── AUTHENTIFICATION UTILISATEUR ───
    
    def authenticate_user(self, user, password: str, totp_code: Optional[str] = None) -> Tuple[bool, str]:
        """
        Authentifie un utilisateur avec mot de passe et optionnellement MFA.
        
        Args:
            user: Instance du modèle User
            password: Mot de passe en clair
            totp_code: Code TOTP (optionnel si MFA désactivé)
        
        Returns:
            (success, message)
        """
        # Vérifier si le compte est actif
        if not user.is_active:
            return False, "Compte désactivé"
        
        # Vérifier le lockout
        if user.is_locked():
            remaining = int((user.locked_until - datetime.utcnow()).total_seconds())
            return False, f"Compte verrouillé. Réessayez dans {remaining} secondes"
        
        # Si pas de mot de passe, authentification externe uniquement
        if not user.password_hash:
            if settings.MFA_ENABLED and totp_code:
                # Vérifier TOTP uniquement
                if self._verify_totp_encrypted(user, totp_code):
                    user.reset_failed_attempts()
                    user.last_login = datetime.utcnow()
                    return True, "Authentification réussie"
                else:
                    user.increment_failed_attempts(settings.LOCKOUT_DURATION_MINUTES)
                    return False, "Code TOTP incorrect"
            return True, "Authentification sans mot de passe"
        
        # Vérifier le mot de passe
        if not self.verify_password(password, user.password_hash):
            user.increment_failed_attempts(settings.LOCKOUT_DURATION_MINUTES)
            return False, "Mot de passe incorrect"
        
        # Vérifier MFA si activé
        if settings.MFA_ENABLED and totp_code:
            if not self._verify_totp_encrypted(user, totp_code):
                user.increment_failed_attempts(settings.LOCKOUT_DURATION_MINUTES)
                return False, "Code TOTP incorrect"
        
        # Authentification réussie
        user.reset_failed_attempts()
        user.last_login = datetime.utcnow()
        return True, "Authentification réussie"
    
    def _verify_totp_encrypted(self, user, code: str) -> bool:
        """Vérifie le code TOTP avec secret chiffré."""
        if not user.totp_secret_encrypted:
            return False
        # Note: Déchiffrement nécessaire ici avec EncryptionManager
        # Pour l'instant, on suppose que le secret est accessible
        # TODO: Implémenter le déchiffrement avec EncryptionManager
        from app.security.encryption import EncryptionManager
        enc = EncryptionManager(settings.SECRET_KEY)
        try:
            secret = enc.decrypt(user.totp_secret_encrypted.encode()).decode()
            return self.verify_totp(secret, code)
        except:
            return False
    
    # ─── JWT ───
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token JWT d'accès."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: dict) -> str:
        """Crée un token JWT de refresh."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[dict]:
        """Décode et valide un token JWT."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def refresh_access_token(self, token: str) -> Optional[str]:
        """Rafraîchit un token d'accès."""
        payload = self.decode_token(token)
        if not payload or payload.get("type") != "refresh":
            return None
        # Créer un nouveau access token
        return self.create_access_token({"sub": payload.get("sub")})
    
    # ─── MFA TOTP ───
    
    def generate_totp_secret(self) -> str:
        """Génère une clé secrète TOTP."""
        return pyotp.random_base32()
    
    def encrypt_totp_secret(self, secret: str) -> bytes:
        """Chiffre un secret TOTP."""
        from app.security.encryption import EncryptionManager
        enc = EncryptionManager(settings.SECRET_KEY)
        return enc.encrypt(secret.encode())
    
    def get_totp_uri(self, secret: str, username: str, issuer: str = "FallDetection") -> str:
        """Génère l'URI pour le QR code."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)
    
    def generate_qr_code(self, uri: str) -> str:
        """Génère un QR code en base64."""
        qr = qrcode.make(uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_totp(self, secret: str, code: str) -> bool:
        """Vérifie un code TOTP."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Tolérance ±1 période
