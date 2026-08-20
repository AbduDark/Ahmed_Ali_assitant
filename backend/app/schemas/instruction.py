"""Teacher instruction schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class InstructionCreate(BaseModel):
    content: str
    title: str | None = None
    priority: int = 0
    is_active: bool = True


class InstructionUpdate(BaseModel):
    content: str | None = None
    title: str | None = None
    priority: int | None = None
    is_active: bool | None = None


class InstructionResponse(BaseModel):
    id: str
    teacher_id: str
    content: str
    title: str | None = None
    priority: int = 0
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True
