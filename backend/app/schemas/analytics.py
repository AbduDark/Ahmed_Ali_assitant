"""Analytics schemas."""

from __future__ import annotations

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_students: int = 0
    active_students: int = 0
    total_conversations: int = 0
    total_references: int = 0
    ready_references: int = 0
    total_ai_requests: int = 0
    failed_ai_requests: int = 0
    avg_response_time_ms: float = 0.0
    total_tokens_used: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0


class AIUsageStats(BaseModel):
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    requests_by_provider: dict[str, int] = {}
    requests_by_model: dict[str, int] = {}


class QuestionsPerDay(BaseModel):
    date: str
    count: int


class SubjectDistribution(BaseModel):
    subject: str
    count: int
    percentage: float
