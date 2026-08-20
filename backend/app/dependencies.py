"""FastAPI dependency injection providers."""

from __future__ import annotations

from typing import Annotated, AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Depends, Header
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core import InvalidCredentialsError, TokenExpiredError
from app.database import get_async_session

# ── Type aliases for cleaner route signatures ────────────────

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# ── Redis ────────────────────────────────────────────────────

_redis_pool: aioredis.Redis | None = None


async def init_redis() -> aioredis.Redis:
    """Initialize the Redis connection pool (called at startup)."""
    global _redis_pool
    _redis_pool = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    return _redis_pool


async def close_redis() -> None:
    """Close the Redis connection pool (called at shutdown)."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """FastAPI dependency that yields a Redis connection."""
    if _redis_pool is None:
        raise RuntimeError("Redis not initialized")
    yield _redis_pool


RedisConn = Annotated[aioredis.Redis, Depends(get_redis)]


# ── Authentication ───────────────────────────────────────────

async def get_current_user_id(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> str:
    """Extract and validate the current user ID from the JWT Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise InvalidCredentialsError()

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if user_id is None or token_type != "access":
            raise InvalidCredentialsError()
        return user_id
    except JWTError:
        raise TokenExpiredError()


CurrentUserId = Annotated[str, Depends(get_current_user_id)]
