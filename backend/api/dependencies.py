"""
FastAPI dependencies for authentication, database, and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext

from backend.core.config import settings
from backend.core.exceptions import AuthenticationException, AuthorizationException
from backend.core.logger import get_logger
from backend.database.base import get_db_dependency
from backend.database.models import User
from backend.database.crud import get_user_by_username

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# HTTP Bearer security
security = HTTPBearer()


def get_db():
    """FastAPI dependency for database sessions."""
    return get_db_dependency()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    from jose import jwt
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    from jose import jwt
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify and decode a JWT token."""
    from jose import JWTError, jwt
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    user_id = token_data.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )
    
    user = get_user_by_username(db, str(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )
    
    if user.is_account_locked():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is locked",
        )
    
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role for access."""
    from backend.core.constants import Role
    
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def require_permission(permission: str):
    """Require specific permission for access (decorator factory)."""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        from backend.security.rbac import rbac_manager
        
        if not rbac_manager.has_permission(str(current_user.id), permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required",
            )
        return current_user
    return permission_checker


def require_role(role: str):
    """Require specific role for access (decorator factory)."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        from backend.core.constants import Role
        
        if current_user.role.value != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required",
            )
        return current_user
    return role_checker
