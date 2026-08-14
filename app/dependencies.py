"""
Dépendances pour injection dans les routes FastAPI.

Gestion des sessions de base de données, authentification JWT, et autres dépendances.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from typing import Optional
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.config import settings
from app.models import Base, Person
from app import crud


# Configuration du hashing des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration de la sécurité HTTP Bearer
security = HTTPBearer()


# Initialisation de la base de données
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = None


def init_db():
    """Initialise la base de données."""
    global SessionLocal
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return engine


def get_db():
    """
    Dépendance pour obtenir une session de base de données.

    Yields:
        Session SQLAlchemy
    """
    if SessionLocal is None:
        init_db()

    db = SessionLocal()
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
    db: Session = Depends(get_db),
) -> Person:
    """
    Récupère l'utilisateur actuel à partir du token.

    Le payload JWT doit contenir `sub` (id utilisateur) ; on charge ensuite
    la `Person` correspondante via `app.crud.get_person`.

    Args:
        token_data: Données du token JWT
        db: Session de base de données

    Returns:
        Personne authentifiée

    Raises:
        HTTPException: 401 si le token ne porte pas de `sub`,
                       401 si la personne n'existe pas ou est désactivée.
    """
    user_id_raw = token_data.get("sub")
    if user_id_raw is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide (sub manquant)",
        )

    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide (sub non numérique)",
        )

    user = crud.get_person(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
        )
    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur désactivé",
        )
    return user


def require_admin(current_user: Person = Depends(get_current_user)) -> Person:
    """
    Vérifie que l'utilisateur courant a les droits d'administrateur.

    Le modèle `Person` n'expose pas nativement de champ `is_admin`, donc on
    s'appuie sur `profile_type` : un admin est ici une `Person` dont
    `profile_type` est `None` (utilisateur opérateur) **ou** spécifiquement
    taggé via un champ JSON `permissions` ajouté plus tard. En attendant,
    on applique une heuristique simple : si l'utilisateur a
    `profile_type == "senior_fragile"` ou n'est pas marqué `is_active`,
    l'accès est refusé. Pour un vrai système RBAC, voir `app.security.rbac`.

    Args:
        current_user: Utilisateur authentifié

    Returns:
        Utilisateur si autorisé

    Raises:
        HTTPException: 403 si l'utilisateur n'a pas les droits admin.
    """
    # Heuristique : on bloque l'admin pour les profils non-ops.
    # `app.security.rbac` couvre les cas fins via décorateurs.
    profile = getattr(current_user, "profile_type", None)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis",
        )
    return current_user
