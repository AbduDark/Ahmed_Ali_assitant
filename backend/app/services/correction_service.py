"""Teacher corrections service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import NotFoundError
from app.models.correction import TeacherCorrection
from app.schemas.correction import CorrectionCreate, CorrectionUpdate


class CorrectionService:
    """Business logic for teacher answer corrections and fine-tuned knowledge."""

    @staticmethod
    async def list_corrections(db: AsyncSession) -> list[TeacherCorrection]:
        """List all corrections."""
        result = await db.execute(
            select(TeacherCorrection).order_by(TeacherCorrection.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_correction(
        data: CorrectionCreate,
        teacher_id: str,
        db: AsyncSession,
    ) -> TeacherCorrection:
        """Create a correction and compute its semantic embedding."""
        correction = TeacherCorrection(
            teacher_id=teacher_id,
            **data.model_dump(),
        )
        db.add(correction)
        await db.flush()

        try:
            from app.ai.router import get_embedding_provider
            provider = get_embedding_provider()
            embedding = await provider.embed(data.question)
            correction.question_embedding = embedding
        except Exception:
            pass

        await db.commit()
        await db.refresh(correction)
        return correction

    @staticmethod
    async def update_correction(
        correction_id: str,
        data: CorrectionUpdate,
        db: AsyncSession,
    ) -> TeacherCorrection:
        """Update a correction and refresh embedding if question changed."""
        result = await db.execute(
            select(TeacherCorrection).where(TeacherCorrection.id == correction_id)
        )
        correction = result.scalar_one_or_none()
        if not correction:
            raise NotFoundError("التصحيح")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(correction, field, value)

        if data.question:
            try:
                from app.ai.router import get_embedding_provider
                provider = get_embedding_provider()
                correction.question_embedding = await provider.embed(data.question)
            except Exception:
                pass

        await db.commit()
        await db.refresh(correction)
        return correction

    @staticmethod
    async def delete_correction(
        correction_id: str,
        db: AsyncSession,
    ) -> None:
        """Delete a correction."""
        result = await db.execute(
            select(TeacherCorrection).where(TeacherCorrection.id == correction_id)
        )
        correction = result.scalar_one_or_none()
        if not correction:
            raise NotFoundError("التصحيح")
        await db.delete(correction)
        await db.commit()
