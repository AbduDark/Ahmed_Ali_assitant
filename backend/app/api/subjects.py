"""Subject, Unit, Lesson management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import NotFoundError
from app.database import get_async_session
from app.dependencies import CurrentUserId
from app.models.subject import Grade, Lesson, Subject, Unit
from app.schemas.subject import (
    LessonCreate,
    LessonResponse,
    SubjectCreate,
    SubjectResponse,
    SubjectUpdate,
    UnitCreate,
    UnitResponse,
)

router = APIRouter(prefix="/subjects", tags=["Subjects"])


# ── Subjects ─────────────────────────────────────────────────

@router.get("", response_model=list[SubjectResponse])
async def list_subjects(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """List all subjects with their units and lessons."""
    result = await db.execute(
        select(Subject).order_by(Subject.name_ar)
    )
    subjects = list(result.scalars().all())
    return [SubjectResponse.model_validate(s) for s in subjects]


@router.post("", response_model=SubjectResponse, status_code=201)
async def create_subject(
    data: SubjectCreate,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new subject."""
    subject = Subject(**data.model_dump())
    db.add(subject)
    await db.flush()
    return SubjectResponse.model_validate(subject)


@router.patch("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: str,
    data: SubjectUpdate,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Update a subject."""
    result = await db.execute(select(Subject).where(Subject.id == subject_id))
    subject = result.scalar_one_or_none()
    if not subject:
        raise NotFoundError("المادة")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)

    return SubjectResponse.model_validate(subject)


# ── Units ────────────────────────────────────────────────────

@router.post("/units", response_model=UnitResponse, status_code=201)
async def create_unit(
    data: UnitCreate,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new unit under a subject."""
    unit = Unit(**data.model_dump())
    db.add(unit)
    await db.flush()
    return UnitResponse.model_validate(unit)


# ── Lessons ──────────────────────────────────────────────────

@router.post("/lessons", response_model=LessonResponse, status_code=201)
async def create_lesson(
    data: LessonCreate,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new lesson under a unit."""
    lesson = Lesson(**data.model_dump())
    db.add(lesson)
    await db.flush()
    return LessonResponse.model_validate(lesson)


# ── Grades ───────────────────────────────────────────────────

@router.get("/grades", response_model=list[dict])
async def list_grades(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """List all grades."""
    result = await db.execute(select(Grade).order_by(Grade.order))
    grades = list(result.scalars().all())
    return [{"id": g.id, "name_ar": g.name_ar, "name_en": g.name_en} for g in grades]
