"""
Endpoints pour l'authentification JWT + MFA.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.models.base import get_db
from app.security.auth import AuthManager

router = APIRouter()


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authentification avec mot de passe.
    Retourne un token JWT.
    """
    auth_manager = AuthManager(db)
    
    # Vérifier les identifiants
    user = auth_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Générer le token
    access_token = auth_manager.create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "email": user.email
        }
    }


@router.post("/mfa/verify")
def verify_mfa(
    username: str,
    code: str,
    db: Session = Depends(get_db)
):
    """
    Vérification du code MFA (2FA).
    """
    auth_manager = AuthManager(db)
    
    # Vérifier le code MFA
    if not auth_manager.verify_mfa_code(username, code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Code MFA invalide"
        )
    
    # Générer le token final
    access_token = auth_manager.create_access_token(data={"sub": username, "mfa_verified": True})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "mfa_verified": True
    }


@router.post("/refresh")
def refresh_token(
    current_token: str,
    db: Session = Depends(get_db)
):
    """
    Rafraîchissement du token JWT.
    """
    auth_manager = AuthManager(db)
    
    # Vérifier et rafraîchir le token
    new_token = auth_manager.refresh_access_token(current_token)
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )
    
    return {
        "access_token": new_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout():
    """
    Déconnexion (client-side token invalidation).
    """
    return {"message": "Déconnexion réussie"}
