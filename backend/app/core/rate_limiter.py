"""Redis-based sliding window rate limiter."""

from __future__ import annotations

import time

import redis.asyncio as aioredis

from app.config import settings
from app.core import RateLimitExceededError


class RateLimiter:
    """Sliding window rate limiter backed by Redis sorted sets."""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 60,
    ) -> None:
        """
        Check if the rate limit has been exceeded.

        Raises RateLimitExceededError if limit is exceeded.
        """
        now = time.time()
        window_start = now - window_seconds
        redis_key = f"ratelimit:{key}"

        pipe = self.redis.pipeline()
        # Remove expired entries
        pipe.zremrangebyscore(redis_key, 0, window_start)
        # Add current request
        pipe.zadd(redis_key, {str(now): now})
        # Count requests in window
        pipe.zcard(redis_key)
        # Set expiry on the key
        pipe.expire(redis_key, window_seconds + 1)
        results = await pipe.execute()

        request_count = results[2]
        if request_count > max_requests:
            raise RateLimitExceededError()

    async def check_student_limit(self, student_id: str) -> None:
        """Check per-student rate limit."""
        await self.check_rate_limit(
            key=f"student:{student_id}",
            max_requests=settings.rate_limit_student_per_minute,
            window_seconds=60,
        )

    async def check_global_limit(self) -> None:
        """Check global rate limit."""
        await self.check_rate_limit(
            key="global",
            max_requests=settings.rate_limit_global_per_minute,
            window_seconds=60,
        )
