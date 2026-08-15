"""
Authentication and session management with JWT + MFA TOTP.
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

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.core.exceptions import AuthenticationException

logger = get_logger(__name__)

# Password hashing context (Argon2id)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class SessionManager:
    """
    Session manager for user sessions.
    
    In production, use Redis or database for session storage.
    """
    
    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, Dict] = {}
        self.session_duration = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    def create_session(self, user_id: int, username: str, ip_address: str = None, user_agent: str = None) -> str:
        """
        Create a new session.
        
        Args:
            user_id: User ID
            username: Username
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Session token
        """
        session_token = secrets.token_urlsafe(32)
        
        self.sessions[session_token] = {
            "user_id": user_id,
            "username": username,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + self.session_duration,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        logger.info(f"Session created for user: {username}")
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        Validate a session.
        
        Args:
            session_token: Session token
        
        Returns:
            Session data if valid, None otherwise
        """
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        # Check expiration
        if datetime.utcnow() > session["expires_at"]:
            del self.sessions[session_token]
            return None
        
        return session
    
    def revoke_session(self, session_token: str) -> bool:
        """
        Revoke a session.
        
        Args:
            session_token: Session token
        
        Returns:
            True if revoked
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
            logger.info(f"Session revoked: {session_token[:10]}...")
            return True
        return False
    
    def revoke_all_user_sessions(self, user_id: int) -> int:
        """
        Revoke all sessions for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Number of sessions revoked
        """
        count = 0
        tokens_to_revoke = []
        
        for token, session in self.sessions.items():
            if session["user_id"] == user_id:
                tokens_to_revoke.append(token)
        
        for token in tokens_to_revoke:
            del self.sessions[token]
            count += 1
        
        if count > 0:
            logger.info(f"Revoked {count} sessions for user_id: {user_id}")
        
        return count
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions removed
        """
        count = 0
        tokens_to_remove = []
        
        for token, session in self.sessions.items():
            if datetime.utcnow() > session["expires_at"]:
                tokens_to_remove.append(token)
        
        for token in tokens_to_remove:
            del self.sessions[token]
            count += 1
        
        if count > 0:
            logger.info(f"Cleaned up {count} expired sessions")
        
        return count
    
    def get_user_sessions(self, user_id: int) -> list:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            List of sessions
        """
        return [
            {
                "token": token[:10] + "...",  # Partial token for security
                "created_at": session["created_at"].isoformat(),
                "expires_at": session["expires_at"].isoformat(),
                "ip_address": session["ip_address"]
            }
            for token, session in self.sessions.items()
            if session["user_id"] == user_id and datetime.utcnow() <= session["expires_at"]
        ]


class AuthManager:
    """
    Authentication manager with JWT, MFA TOTP, and account lockout.
    """
    
    def __init__(self, db):
        """
        Initialize authentication manager.
        
        Args:
            db: Database session
        """
        self.db = db
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
    
    # ─── PASSWORD MANAGEMENT ───
    
    def hash_password(self, password: str) -> str:
        """Hash a password with Argon2id."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.warning(f"Password verification error: {e}")
            return False
    
    # ─── USER AUTHENTICATION ───
    
    def authenticate_user(
        self, 
        user, 
        password: str, 
        totp_code: Optional[str] = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> Tuple[bool, str]:
        """
        Authenticate a user with password and optional MFA.
        
        Args:
            user: User model instance
            password: Plain password
            totp_code: TOTP code (optional if MFA disabled)
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            (success, message)
        """
        # Check if account is active
        if not user.is_active:
            return False, "Account is disabled"
        
        # Check if account is locked
        if user.is_account_locked():
            remaining = int((user.locked_until - datetime.utcnow()).total_seconds())
            return False, f"Account locked. Try again in {remaining} seconds"
        
        # If no password, external auth only
        if not user.password_hash:
            if settings.MFA_ENABLED and totp_code:
                if self._verify_totp_encrypted(user, totp_code):
                    user.reset_failed_attempts()
                    user.last_login = datetime.utcnow()
                    self.db.commit()
                    return True, "Authentication successful"
                else:
                    user.increment_failed_attempts(settings.LOCKOUT_DURATION_MINUTES)
                    self.db.commit()
                    return False, "Invalid TOTP code"
            return True, "Authentication successful (no password)"
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            user.increment_failed_attempts(settings.LOCKOUT_DURATION_MINUTES)
            self.db.commit()
            logger.warning(f"Failed login attempt for user: {user.username}")
            return False, "Invalid password"
        
        # Verify MFA if enabled
        if settings.MFA_ENABLED and user.mfa_enabled:
            if totp_code:
                if not self._verify_totp_encrypted(user, totp_code):
                    user.increment_failed_attempts(settings.LOCKOUT_DURATION_MINUTES)
                    self.db.commit()
                    return False, "Invalid TOTP code"
            else:
                # MFA required but not provided
                return False, "MFA code required"
        
        # Authentication successful
        user.reset_failed_attempts()
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Successful authentication for user: {user.username}")
        return True, "Authentication successful"
    
    def _verify_totp_encrypted(self, user, code: str) -> bool:
        """Verify TOTP code with encrypted secret."""
        if not user.totp_secret_encrypted:
            return False
        
        try:
            from .encryption import EncryptionManager
            enc = EncryptionManager(settings.SECRET_KEY)
            secret = enc.decrypt(user.totp_secret_encrypted.encode()).decode()
            return self.verify_totp(secret, code)
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False
    
    # ─── JWT TOKEN MANAGEMENT ───
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Optional[dict]:
        """Decode and validate JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"Token decode error: {e}")
            return None
    
    def refresh_access_token(self, token: str) -> Optional[str]:
        """Refresh access token using refresh token."""
        payload = self.decode_token(token)
        if not payload or payload.get("type") != "refresh":
            return None
        return self.create_access_token({"sub": payload.get("sub")})
    
    # ─── MFA TOTP MANAGEMENT ───
    
    def generate_totp_secret(self) -> str:
        """Generate TOTP secret."""
        return pyotp.random_base32()
    
    def encrypt_totp_secret(self, secret: str) -> bytes:
        """Encrypt TOTP secret."""
        from .encryption import EncryptionManager
        enc = EncryptionManager(settings.SECRET_KEY)
        return enc.encrypt(secret.encode())
    
    def get_totp_uri(self, secret: str, username: str, issuer: str = None) -> str:
        """Generate TOTP provisioning URI."""
        if issuer is None:
            issuer = settings.MFA_ISSUER
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=issuer)
    
    def generate_qr_code(self, uri: str) -> str:
        """Generate QR code as base64 string."""
        qr = qrcode.make(uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_totp(self, secret: str, code: str) -> bool:
        """Verify TOTP code."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # ±1 period tolerance


# Global session manager instance
session_manager = SessionManager()
