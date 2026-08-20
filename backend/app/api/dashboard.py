"""Dashboard API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import CurrentUserId
from app.schemas.analytics import DashboardStats
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardStats)
async def get_dashboard(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Get dashboard overview statistics."""
    return await AnalyticsService.get_dashboard_stats(db)
