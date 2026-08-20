"""Student management service."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import NotFoundError
from app.models.student import Student
from app.schemas.student import StudentUpdateRequest


class StudentService:
    """Business logic for student administration."""

    @staticmethod
    async def list_students(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
    ) -> tuple[list[Student], int]:
        """List students with optional search filter."""
        query = select(Student)
        count_query = select(func.count(Student.id))

        if search:
            search_filter = (
                Student.first_name.ilike(f"%{search}%")
                | Student.last_name.ilike(f"%{search}%")
                | Student.username.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        query = query.order_by(Student.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        students = list(result.scalars().all())
        total = await db.scalar(count_query) or 0

        return students, total

    @staticmethod
    async def get_student(student_id: str, db: AsyncSession) -> Student:
        """Get student by ID."""
        result = await db.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()
        if not student:
            raise NotFoundError("الطالب")
        return student

    @staticmethod
    async def update_student(
        student_id: str,
        data: StudentUpdateRequest,
        db: AsyncSession,
    ) -> Student:
        """Update student details."""
        student = await StudentService.get_student(student_id, db)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(student, field, value)
        await db.commit()
        await db.refresh(student)
        return student
