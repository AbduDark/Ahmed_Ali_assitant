"""Analytics API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import CurrentUserId
from app.schemas.analytics import AIUsageStats
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=dict)
async def get_analytics(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
    days: int = Query(30, ge=1, le=365),
):
    """Get analytics overview."""
    stats = await AnalyticsService.get_dashboard_stats(db)
    return stats.model_dump()


@router.get("/ai-usage", response_model=AIUsageStats)
async def get_ai_usage(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
    days: int = Query(30, ge=1, le=365),
):
    """Get AI usage statistics."""
    return await AnalyticsService.get_ai_usage_stats(db, days=days)
