"""Teacher correction schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CorrectionCreate(BaseModel):
    question: str
    bad_answer: str | None = None
    correct_answer: str
    subject: str | None = None
    tags: list[str] | None = None


class CorrectionUpdate(BaseModel):
    question: str | None = None
    bad_answer: str | None = None
    correct_answer: str | None = None
    subject: str | None = None
    tags: list[str] | None = None


class CorrectionResponse(BaseModel):
    id: str
    teacher_id: str
    question: str
    bad_answer: str | None = None
    correct_answer: str
    subject: str | None = None
    tags: list[str] | None = None
    created_at: datetime

    class Config:
        from_attributes = True
