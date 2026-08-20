"""Subject, Unit, Lesson schemas."""

from __future__ import annotations

from pydantic import BaseModel


# ── Subject ──────────────────────────────────────────────────

class SubjectCreate(BaseModel):
    name_ar: str
    name_en: str | None = None
    description: str | None = None


class SubjectUpdate(BaseModel):
    name_ar: str | None = None
    name_en: str | None = None
    description: str | None = None
    is_active: bool | None = None


class LessonResponse(BaseModel):
    id: str
    name_ar: str
    name_en: str | None = None
    order: int = 0

    class Config:
        from_attributes = True


class UnitResponse(BaseModel):
    id: str
    subject_id: str
    name_ar: str
    name_en: str | None = None
    order: int = 0
    lessons: list[LessonResponse] = []

    class Config:
        from_attributes = True


class SubjectResponse(BaseModel):
    id: str
    name_ar: str
    name_en: str | None = None
    description: str | None = None
    is_active: bool = True
    units: list[UnitResponse] = []

    class Config:
        from_attributes = True


# ── Unit ─────────────────────────────────────────────────────

class UnitCreate(BaseModel):
    subject_id: str
    name_ar: str
    name_en: str | None = None
    order: int = 0


class UnitUpdate(BaseModel):
    name_ar: str | None = None
    name_en: str | None = None
    order: int | None = None


# ── Lesson ───────────────────────────────────────────────────

class LessonCreate(BaseModel):
    unit_id: str
    name_ar: str
    name_en: str | None = None
    order: int = 0


class LessonUpdate(BaseModel):
    name_ar: str | None = None
    name_en: str | None = None
    order: int | None = None
