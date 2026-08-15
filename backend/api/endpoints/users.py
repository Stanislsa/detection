"""
User management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr

from backend.api.dependencies import get_db, get_current_user, require_admin, get_password_hash
from backend.database.crud import get_user, get_users, create_user, update_user, delete_user
from backend.database.models import User
from backend.core.constants import Role

router = APIRouter()


# Pydantic schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: Role = Role.VIEWER


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr = None
    role: Role = None
    is_active: bool = None
    mfa_enabled: bool = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: Role
    is_active: bool
    mfa_enabled: bool
    last_login: str = None
    created_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    # Users can only view their own profile unless admin
    if current_user.role != Role.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new user (admin only)."""
    # Check if username already exists
    from backend.database.crud import get_user_by_username
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Hash password
    user_dict = user_data.model_dump()
    user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
    
    user = create_user(db, user_dict)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user."""
    # Users can only update their own profile unless admin
    if current_user.role != Role.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Non-admins cannot change role or active status
    if current_user.role != Role.ADMIN:
        user_data.role = None
        user_data.is_active = None
    
    update_dict = user_data.model_dump(exclude_unset=True)
    user = update_user(db, user_id, update_dict)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete user (admin only, soft delete)."""
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None
