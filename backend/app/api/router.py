"""Main API router — aggregates all sub-routers."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.conversations import router as conversations_router
from app.api.corrections import router as corrections_router
from app.api.dashboard import router as dashboard_router
from app.api.instructions import router as instructions_router
from app.api.references import router as references_router
from app.api.students import router as students_router
from app.api.subjects import router as subjects_router
from app.api.webhooks import router as webhooks_router

api_router = APIRouter(prefix="/api")

# Auth (no prefix needed — already has /auth)
api_router.include_router(auth_router)

# Dashboard
api_router.include_router(dashboard_router)

# Resources
api_router.include_router(students_router)
api_router.include_router(conversations_router)
api_router.include_router(references_router)
api_router.include_router(subjects_router)
api_router.include_router(instructions_router)
api_router.include_router(corrections_router)

# Analytics
api_router.include_router(analytics_router)

# Webhooks (outside /api prefix)
webhook_router = webhooks_router
