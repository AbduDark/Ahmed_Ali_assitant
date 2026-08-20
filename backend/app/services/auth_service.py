"""Authentication service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import InvalidCredentialsError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.auth import TokenResponse


class AuthService:
    """Authentication business logic."""

    @staticmethod
    async def login(email: str, password: str, db: AsyncSession) -> TokenResponse:
        """Authenticate a user and return tokens."""
        result = await db.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        access_token = create_access_token(user.id, user.role.value)
        refresh_token = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @staticmethod
    async def refresh_token(refresh_token_str: str, db: AsyncSession) -> TokenResponse:
        """Refresh an access token."""
        from jose import JWTError
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise InvalidCredentialsError()

            user_id = payload.get("sub")
            if not user_id:
                raise InvalidCredentialsError()

        except JWTError:
            raise InvalidCredentialsError()

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise InvalidCredentialsError()

        access_token = create_access_token(user.id, user.role.value)
        new_refresh_token = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    @staticmethod
    async def get_current_user(user_id: str, db: AsyncSession) -> User:
        """Get the current authenticated user."""
        result = await db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("المستخدم")
        return user

    @staticmethod
    async def create_user(
        email: str,
        password: str,
        name: str,
        role: UserRole,
        db: AsyncSession,
    ) -> User:
        """Create a new user (for admin scripts)."""
        hashed = hash_password(password)
        user = User(
            email=email,
            hashed_password=hashed,
            name=name,
            role=role,
        )
        db.add(user)
        await db.flush()
        return user
