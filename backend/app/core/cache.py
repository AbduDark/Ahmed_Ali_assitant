"""Redis caching utilities."""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis

from app.core.logging import get_logger

logger = get_logger(__name__)


class Cache:
    """Simple Redis cache with JSON serialization."""

    def __init__(self, redis: aioredis.Redis, prefix: str = "cache"):
        self.redis = redis
        self.prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Any | None:
        """Get a cached value. Returns None if not found."""
        try:
            raw = await self.redis.get(self._key(key))
            if raw is None:
                return None
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Cache get error for key={key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 300,
    ) -> None:
        """Set a cached value with TTL."""
        try:
            raw = json.dumps(value, ensure_ascii=False, default=str)
            await self.redis.set(self._key(key), raw, ex=ttl_seconds)
        except Exception as e:
            logger.warning(f"Cache set error for key={key}: {e}")

    async def delete(self, key: str) -> None:
        """Delete a cached value."""
        try:
            await self.redis.delete(self._key(key))
        except Exception as e:
            logger.warning(f"Cache delete error for key={key}: {e}")

    async def invalidate_pattern(self, pattern: str) -> None:
        """Delete all keys matching a pattern."""
        try:
            full_pattern = self._key(pattern)
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(
                    cursor=cursor, match=full_pattern, count=100
                )
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            logger.warning(f"Cache invalidate error for pattern={pattern}: {e}")
