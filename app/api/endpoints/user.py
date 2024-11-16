# api/endpoints/auth.py
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.models.user import User
from app.services.auth import AuthService

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    OAuth2 compatible token login
    """
    user = await AuthService.authenticate(
        form_data.username, 
        form_data.password, 
        db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # 创建访问令牌和刷新令牌
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_expires = timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    
    return Token(
        access_token=AuthService.create_access_token(
            user.id,
            expires_delta=access_token_expires
        ),
        refresh_token=AuthService.create_refresh_token(
            user.id,
            expires_delta=refresh_token_expires
        ),
        token_type="bearer"
    )

@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    注册新用户
    """
    return await AuthService.create_user(user_in, db)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    使用刷新令牌获取新的访问令牌
    """
    try:
        # 验证刷新令牌
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        user_id = int(payload["sub"])
        
        # 获取用户
        user = await db.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
            
        # 创建新的令牌
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_token_expires = timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        
        return Token(
            access_token=AuthService.create_access_token(
                user.id,
                expires_delta=access_token_expires
            ),
            refresh_token=AuthService.create_refresh_token(
                user.id,
                expires_delta=refresh_token_expires
            ),
            token_type="bearer"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    获取当前用户信息
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    更新当前用户信息
    """
    user = await AuthService.update_user(
        current_user.id,
        user_update,
        db
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user