from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from datetime import timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = 30

from ecommerce_api.models import UserRegister, UserLogin, Token, User
from ecommerce_api.services import UserService
from ecommerce_api.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_password_hash, verify_password
)
from ecommerce_api.exceptions import UserNotFound, InvalidCredentials

user_service = UserService()

router = APIRouter()

@router.post("/register", response_model=User)
async def register_user(user_in: UserRegister):
    existing_user = await user_service.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = get_password_hash(user_in.password)
    user = await user_service.register_user(user_in.email, hashed_password)
    return user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_service.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    # The current_user object returned by get_current_active_user is a dict, 
    # but our User model expects a password_hash. We need to fetch the full user.
    full_user = await user_service.get_user_by_id(current_user["user_id"])
    if not full_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return full_user

@router.put("/me", response_model=User)
async def update_users_me(user_update: dict, current_user: User = Depends(get_current_active_user)):
    try:
        updated_user = await user_service.update_user(current_user["user_id"], user_update)
        return updated_user
    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")