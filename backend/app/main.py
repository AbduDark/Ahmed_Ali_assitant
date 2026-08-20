"""
FastAPI application entry point.

Handles:
- App lifecycle (startup/shutdown)
- CORS, middleware
- Route registration
- Telegram bot lifecycle
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # ── Startup ──────────────────────────────────────────
    setup_logging()
    logger.info(f"Starting {settings.app_name} ({settings.app_env})")

    # Initialize Redis
    from app.dependencies import init_redis
    await init_redis()
    logger.info("Redis connected")

    # Initialize Telegram bot
    from app.messaging.telegram.bot import telegram_bot
    try:
        await telegram_bot.initialize()
        await telegram_bot.start()
    except Exception as e:
        logger.warning(f"Telegram bot initialization failed: {e}")

    logger.info(f"{settings.app_name} started successfully")

    yield

    # ── Shutdown ─────────────────────────────────────────
    logger.info("Shutting down...")

    # Stop Telegram bot
    try:
        await telegram_bot.stop()
    except Exception as e:
        logger.warning(f"Telegram bot shutdown error: {e}")

    # Close Redis
    from app.dependencies import close_redis
    await close_redis()

    # Close database connections
    from app.database import engine
    await engine.dispose()

    logger.info("Shutdown complete")


# ── Create FastAPI App ───────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    description="AI Educational Assistant for History and Geography Teachers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────

from app.api.router import api_router, webhook_router  # noqa: E402

app.include_router(api_router)
app.include_router(webhook_router)


# ── Health Check ─────────────────────────────────────────────

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "env": settings.app_env,
    }


# ── Global Exception Handler ────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return a friendly error."""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "حدث خطأ داخلي في الخادم. يرجى المحاولة لاحقاً.",
            "code": "INTERNAL_ERROR",
        },
    )
