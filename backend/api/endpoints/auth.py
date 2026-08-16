"""
Authentication endpoints - Login, MFA, token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from backend.api.dependencies import (
    get_db, get_current_user, verify_password, 
    create_access_token, create_refresh_token
)
from backend.database.crud import get_user_by_username, create_user, update_user
from backend.security.auth import AuthManager
from backend.core.logger import get_logger
from backend.core.config import settings

router = APIRouter()
logger = get_logger(__name__)


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user with username and password.
    Returns JWT access token and refresh token.
    """
    auth_manager = AuthManager(db)
    
    user = get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Authenticate user
    success, message = auth_manager.authenticate_user(user, form_data.password)
    if not success:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    logger.info(f"Successful login for user: {form_data.username}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }
    }


@router.post("/mfa/setup")
async def setup_mfa(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Setup MFA for the current user.
    Returns QR code for TOTP setup.
    """
    from backend.security.auth import AuthManager
    
    auth_manager = AuthManager(db)
    
    # Generate TOTP secret
    secret = auth_manager.generate_totp_secret()
    encrypted_secret = auth_manager.encrypt_totp_secret(secret)
    
    # Update user with encrypted secret
    update_user(db, current_user.id, {
        "totp_secret_encrypted": encrypted_secret.decode(),
        "mfa_enabled": True
    })
    
    # Generate provisioning URI and QR code
    uri = auth_manager.get_totp_uri(secret, current_user.username, settings.APP_NAME)
    qr_code = auth_manager.generate_qr_code(uri)
    
    return {
        "secret": secret,  # Only show once for manual entry
        "qr_code": qr_code,
        "uri": uri
    }


@router.post("/mfa/verify")
async def verify_mfa(
    code: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify MFA code during login or setup.
    """
    from backend.security.auth import AuthManager
    
    auth_manager = AuthManager(db)
    
    if not auth_manager.verify_totp_encrypted(current_user, code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )
    
    return {"message": "MFA verified successfully"}


@router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    from jose import JWTError, jwt
    from backend.core.config import settings
    
    try:
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists and is active
        user = get_user_by_username(db, str(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """
    Logout current user.
    Note: JWT tokens are stateless, client should discard tokens.
    """
    logger.info(f"User logged out: {current_user.username}")
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """
    Get current user information.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.value,
        "mfa_enabled": current_user.mfa_enabled,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

# Email simulation endpoints
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from backend.notifications.email_simulator import email_sim

class EmailRequest(BaseModel):
    email: EmailStr
    username: Optional[str] = None

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=12)

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=12)
    new_password: str = Field(..., min_length=6)

@router.post("/send-verification")
async def send_verification_email(body: EmailRequest):
    mail = email_sim.send_verification(str(body.email), body.username or "")
    return {"ok": True, "simulated": True, "email": str(body.email), "dev_code": mail.code, "expires_at": mail.expires_at.isoformat()}

@router.post("/verify-email")
async def verify_email_code(body: VerifyCodeRequest):
    if not email_sim.consume_code(str(body.email), "verify_email", body.code):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    return {"ok": True, "message": "Email verified (simulated)"}

@router.post("/forgot-password")
async def forgot_password(body: EmailRequest):
    mail = email_sim.send_password_reset(str(body.email))
    return {"ok": True, "simulated": True, "email": str(body.email), "dev_code": mail.code}

@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    if not email_sim.consume_code(str(body.email), "password_reset", body.code):
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
    return {"ok": True, "message": "Password reset accepted (simulated)", "email": str(body.email)}

@router.post("/send-otp")
async def send_login_otp(body: EmailRequest):
    mail = email_sim.send_login_otp(str(body.email), body.username or "")
    return {"ok": True, "simulated": True, "dev_code": mail.code}

@router.post("/verify-otp")
async def verify_login_otp(body: VerifyCodeRequest):
    if not email_sim.consume_code(str(body.email), "login_otp", body.code):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return {"ok": True, "message": "OTP verified"}

@router.get("/email-sim/history")
async def email_sim_history(limit: int = 20):
    return {"items": email_sim.history(limit=limit), "simulated": True}
