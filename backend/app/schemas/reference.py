"""Reference schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ReferenceCreate(BaseModel):
    title: str
    description: str | None = None
    subject_id: str | None = None
    grade_id: str | None = None
    unit_id: str | None = None
    lesson_id: str | None = None
    academic_year: str | None = None
    language: str = "ar"
    source_url: str | None = None


class ReferenceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    subject_id: str | None = None
    grade_id: str | None = None
    unit_id: str | None = None
    lesson_id: str | None = None
    academic_year: str | None = None


class ReferenceResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    subject_id: str | None = None
    grade_id: str | None = None
    unit_id: str | None = None
    lesson_id: str | None = None
    file_name: str | None = None
    file_type: str | None = None
    file_size: int | None = None
    source_url: str | None = None
    language: str = "ar"
    academic_year: str | None = None
    status: str
    page_count: int | None = None
    chunk_count: int | None = None
    error_message: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReferenceListResponse(BaseModel):
    references: list[ReferenceResponse]
    total: int
