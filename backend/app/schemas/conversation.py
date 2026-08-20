"""Conversation schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    retrieved_chunks: list[dict[str, Any]] | None = None
    citations: list[dict[str, Any]] | None = None
    response_time_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    ai_provider: str | None = None
    ai_model: str | None = None
    confidence_score: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: str
    student_id: str
    title: str | None = None
    summary: str | None = None
    is_active: bool = True
    message_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    id: str
    student_id: str
    title: str | None = None
    summary: str | None = None
    message_count: int = 0
    messages: list[MessageResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
