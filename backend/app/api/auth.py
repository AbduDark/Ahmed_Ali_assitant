"""Authentication API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import CurrentUserId
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_async_session),
):
    """Authenticate and receive access/refresh tokens."""
    return await AuthService.login(data.email, data.password, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_async_session),
):
    """Refresh an expired access token."""
    return await AuthService.refresh_token(data.refresh_token, db)


@router.get("/me", response_model=UserResponse)
async def get_me(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Get the current authenticated user."""
    user = await AuthService.get_current_user(user_id, db)
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        is_active=user.is_active,
    )
