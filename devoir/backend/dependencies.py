"""
Dépendances pour injection dans les routes FastAPI.

Gestion des sessions de base de données, authentification JWT, et autres dépendances.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from config import settings
from database import crud, models


# Configuration du hashing des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration de la sécurité HTTP Bearer
security = HTTPBearer()


def get_db(session_local):
    """
    Dépendance pour obtenir une session de base de données.
    
    Args:
        session_local: SessionLocal SQLAlchemy
    
    Yields:
        Session SQLAlchemy
    """
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie un mot de passe contre son hash.
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash du mot de passe
    
    Returns:
        True si le mot de passe correspond
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash un mot de passe.
    
    Args:
        password: Mot de passe en clair
    
    Returns:
        Hash du mot de passe
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT d'accès.
    
    Args:
        data: Données à encoder dans le token
        expires_delta: Durée de validité du token
    
    Returns:
        Token JWT encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Vérifie et décode un token JWT.
    
    Args:
        credentials: Credentials HTTP Bearer
    
    Returns:
        Données décodées du token
    
    Raises:
        HTTPException: Si le token est invalide
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(lambda: None)  # À adapter avec get_db
) -> Optional[models.Person]:
    """
    Récupère l'utilisateur actuel à partir du token.
    
    Args:
        token_data: Données du token JWT
        db: Session de base de données
    
    Returns:
        Personne authentifiée ou None
    
    Raises:
        HTTPException: Si l'utilisateur n'existe pas
    """
    user_id = token_data.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
        )
    
    # Note: À implémenter avec la fonction CRUD appropriée
    # user = crud.get_person(db, user_id)
    # if user is None:
    #     raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    # return user
    
    return None


def require_admin(current_user: models.Person = Depends(get_current_user)) -> models.Person:
    """
    Vérifie que l'utilisateur a les droits d'administrateur.
    
    Args:
        current_user: Utilisateur actuel
    
    Returns:
        Utilisateur si admin
    
    Raises:
        HTTPException: Si l'utilisateur n'est pas admin
    """
    # Note: À implémenter avec un champ 'is_admin' dans le modèle Person
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Droits administrateur requis"
    #     )
    return current_user
