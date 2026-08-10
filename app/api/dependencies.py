"""
Dépendances FastAPI pour l'authentification et l'autorisation.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, List

from app.models.base import get_db
from app.models.user import User
from app.security.auth import AuthManager
from app.config import settings


# Schéma OAuth2 pour l'extraction du token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuel à partir du token JWT.
    
    Args:
        token: Token JWT d'accès
        db: Session de base de données
    
    Returns:
        Instance de l'utilisateur
    
    Raises:
        HTTPException 401 si le token est invalide
    """
    auth_manager = AuthManager()
    
    # Décoder le token
    payload = auth_manager.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Récupérer l'utilisateur avec eager loading des rôles
    from sqlalchemy.orm import joinedload
    user = db.query(User).options(joinedload(User.roles).joinedload("permissions")).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier si le compte est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    # Vérifier le lockout
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte temporairement verrouillé"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dépendance pour obtenir l'utilisateur actif.
    
    Args:
        current_user: Utilisateur actuel
    
    Returns:
        Utilisateur actif
    
    Raises:
        HTTPException 400 si le compte est inactif
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte inactif"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dépendance pour vérifier que l'utilisateur est administrateur.
    
    Args:
        current_user: Utilisateur actuel
    
    Returns:
        Utilisateur administrateur
    
    Raises:
        HTTPException 403 si l'utilisateur n'est pas admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes"
        )
    return current_user


async def require_permission(permission_name: str):
    """
    Dépendance pour vérifier une permission spécifique.
    
    Args:
        permission_name: Nom de la permission requise
    
    Returns:
        Fonction de dépendance FastAPI
    """
    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(permission_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission requise: {permission_name}"
            )
        return current_user
    return check_permission


async def require_role(role_name: str):
    """
    Dépendance pour vérifier un rôle spécifique.
    
    Args:
        role_name: Nom du rôle requis
    
    Returns:
        Fonction de dépendance FastAPI
    """
    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_role(role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle requis: {role_name}"
            )
        return current_user
    return check_role


async def require_any_permission(permissions: List[str]):
    """
    Dépendance pour vérifier que l'utilisateur a au moins une des permissions.
    
    Args:
        permissions: Liste des permissions (une suffit)
    
    Returns:
        Fonction de dépendance FastAPI
    """
    async def check_any_permission(current_user: User = Depends(get_current_user)) -> User:
        if not any(current_user.has_permission(perm) for perm in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Une des permissions requise: {', '.join(permissions)}"
            )
        return current_user
    return check_any_permission


async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dépendance optionnelle pour obtenir l'utilisateur actuel.
    Retourne None si pas de token ou token invalide.
    
    Args:
        token: Token JWT optionnel
        db: Session de base de données
    
    Returns:
        Utilisateur ou None
    """
    if not token:
        return None
    
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
