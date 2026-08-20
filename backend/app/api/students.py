"""Student management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import NotFoundError
from app.database import get_async_session
from app.dependencies import CurrentUserId
from app.models.student import Student
from app.schemas.student import StudentListResponse, StudentResponse, StudentUpdateRequest

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=StudentListResponse)
async def list_students(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = None,
):
    """List all students with optional search."""
    query = select(Student)
    count_query = select(func.count(Student.id))

    if search:
        search_filter = Student.first_name.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    query = query.order_by(Student.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    students = list(result.scalars().all())

    total = await db.scalar(count_query) or 0

    return StudentListResponse(
        students=[StudentResponse.model_validate(s) for s in students],
        total=total,
    )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: str,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Get a student by ID."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise NotFoundError("الطالب")
    return StudentResponse.model_validate(student)


@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    data: StudentUpdateRequest,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Update a student's information."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise NotFoundError("الطالب")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    return StudentResponse.model_validate(student)
