"""ARQ worker settings."""

from __future__ import annotations

from arq.connections import RedisSettings

from app.config import settings


def _parse_redis_url(url: str) -> RedisSettings:
    """Parse Redis URL into ARQ RedisSettings."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or 0),
        password=parsed.password,
    )


async def startup(ctx: dict) -> None:
    """Worker startup — initialize database connection."""
    from app.database import async_session_factory
    from app.core.logging import setup_logging
    setup_logging()
    ctx["db_factory"] = async_session_factory


async def shutdown(ctx: dict) -> None:
    """Worker shutdown."""
    pass


from app.workers.conversation_tasks import summarize_conversation
from app.workers.document_tasks import process_document


class WorkerSettings:
    """ARQ worker configuration."""

    functions = [process_document, summarize_conversation]
    redis_settings = _parse_redis_url(settings.redis_url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 5
    job_timeout = 600  # 10 minutes for large documents
