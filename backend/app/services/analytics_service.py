"""Analytics service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_usage import AIUsageLog
from app.models.conversation import Conversation, Message
from app.models.feedback import Feedback
from app.models.reference import Reference, ReferenceStatus
from app.models.student import Student
from app.schemas.analytics import AIUsageStats, DashboardStats


class AnalyticsService:
    """Analytics and dashboard statistics."""

    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
        """Get overview statistics for the dashboard."""
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        # Students
        total_students = await db.scalar(
            select(func.count(Student.id))
        ) or 0

        active_students = await db.scalar(
            select(func.count(Student.id)).where(
                Student.last_seen_at >= thirty_days_ago
            )
        ) or 0

        # Conversations
        total_conversations = await db.scalar(
            select(func.count(Conversation.id))
        ) or 0

        # References
        total_references = await db.scalar(
            select(func.count(Reference.id)).where(Reference.deleted_at.is_(None))
        ) or 0

        ready_references = await db.scalar(
            select(func.count(Reference.id)).where(
                Reference.status == ReferenceStatus.READY,
                Reference.deleted_at.is_(None),
            )
        ) or 0

        # AI Usage
        total_ai_requests = await db.scalar(
            select(func.count(AIUsageLog.id))
        ) or 0

        failed_ai_requests = await db.scalar(
            select(func.count(AIUsageLog.id)).where(AIUsageLog.status == "error")
        ) or 0

        avg_response = await db.scalar(
            select(func.avg(AIUsageLog.latency_ms)).where(AIUsageLog.status == "success")
        ) or 0.0

        total_tokens = await db.scalar(
            select(func.sum(AIUsageLog.total_tokens))
        ) or 0

        # Feedback
        positive = await db.scalar(
            select(func.count(Feedback.id)).where(Feedback.rating > 0)
        ) or 0

        negative = await db.scalar(
            select(func.count(Feedback.id)).where(Feedback.rating < 0)
        ) or 0

        return DashboardStats(
            total_students=total_students,
            active_students=active_students,
            total_conversations=total_conversations,
            total_references=total_references,
            ready_references=ready_references,
            total_ai_requests=total_ai_requests,
            failed_ai_requests=failed_ai_requests,
            avg_response_time_ms=float(avg_response),
            total_tokens_used=total_tokens,
            positive_feedback=positive,
            negative_feedback=negative,
        )

    @staticmethod
    async def get_ai_usage_stats(
        db: AsyncSession,
        *,
        days: int = 30,
    ) -> AIUsageStats:
        """Get AI usage statistics."""
        since = datetime.now(timezone.utc) - timedelta(days=days)

        base_query = select(AIUsageLog).where(AIUsageLog.created_at >= since)

        total_requests = await db.scalar(
            select(func.count(AIUsageLog.id)).where(AIUsageLog.created_at >= since)
        ) or 0

        total_input = await db.scalar(
            select(func.sum(AIUsageLog.input_tokens)).where(AIUsageLog.created_at >= since)
        ) or 0

        total_output = await db.scalar(
            select(func.sum(AIUsageLog.output_tokens)).where(AIUsageLog.created_at >= since)
        ) or 0

        total_tokens = await db.scalar(
            select(func.sum(AIUsageLog.total_tokens)).where(AIUsageLog.created_at >= since)
        ) or 0

        avg_latency = await db.scalar(
            select(func.avg(AIUsageLog.latency_ms)).where(
                AIUsageLog.created_at >= since,
                AIUsageLog.status == "success",
            )
        ) or 0.0

        error_count = await db.scalar(
            select(func.count(AIUsageLog.id)).where(
                AIUsageLog.created_at >= since,
                AIUsageLog.status == "error",
            )
        ) or 0

        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0.0

        # Requests by provider
        provider_rows = await db.execute(
            select(
                AIUsageLog.provider,
                func.count(AIUsageLog.id).label("count"),
            )
            .where(AIUsageLog.created_at >= since)
            .group_by(AIUsageLog.provider)
        )
        requests_by_provider = {row[0]: row[1] for row in provider_rows}

        # Requests by model
        model_rows = await db.execute(
            select(
                AIUsageLog.model,
                func.count(AIUsageLog.id).label("count"),
            )
            .where(AIUsageLog.created_at >= since)
            .group_by(AIUsageLog.model)
        )
        requests_by_model = {row[0]: row[1] for row in model_rows}

        return AIUsageStats(
            total_requests=total_requests,
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            total_tokens=total_tokens,
            avg_latency_ms=float(avg_latency),
            error_rate=error_rate,
            requests_by_provider=requests_by_provider,
            requests_by_model=requests_by_model,
        )
