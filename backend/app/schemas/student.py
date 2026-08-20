"""Student schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class StudentResponse(BaseModel):
    id: str
    telegram_user_id: int
    username: str | None = None
    first_name: str
    last_name: str | None = None
    grade: str | None = None
    preferred_language: str = "ar"
    school: str | None = None
    is_active: bool = True
    last_seen_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class StudentListResponse(BaseModel):
    students: list[StudentResponse]
    total: int


class StudentUpdateRequest(BaseModel):
    grade: str | None = None
    school: str | None = None
    is_active: bool | None = None
