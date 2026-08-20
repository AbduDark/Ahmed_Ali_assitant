"""AI usage tracking model."""

from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class AIUsageLog(Base, TimestampMixin):
    __tablename__ = "ai_usage_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)

    # Provider info
    provider: Mapped[str] = mapped_column(String(50), index=True)
    model: Mapped[str] = mapped_column(String(100))

    # Token usage
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Cost
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0)

    # Performance
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="success", index=True)
    error: Mapped[str | None] = mapped_column(Text, default=None)

    # Context
    request_type: Mapped[str] = mapped_column(String(50), default="chat")
    student_id: Mapped[str | None] = mapped_column(String(36), default=None, index=True)
    conversation_id: Mapped[str | None] = mapped_column(String(36), default=None)

    def __repr__(self) -> str:
        return f"<AIUsageLog {self.provider}/{self.model} tokens={self.total_tokens}>"
