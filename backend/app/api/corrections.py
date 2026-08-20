"""Teacher corrections API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import NotFoundError
from app.database import get_async_session
from app.dependencies import CurrentUserId
from app.models.correction import TeacherCorrection
from app.schemas.correction import CorrectionCreate, CorrectionResponse, CorrectionUpdate

router = APIRouter(prefix="/corrections", tags=["Corrections"])


@router.get("", response_model=list[CorrectionResponse])
async def list_corrections(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """List all teacher corrections."""
    result = await db.execute(
        select(TeacherCorrection).order_by(TeacherCorrection.created_at.desc())
    )
    corrections = list(result.scalars().all())
    return [CorrectionResponse.model_validate(c) for c in corrections]


@router.post("", response_model=CorrectionResponse, status_code=201)
async def create_correction(
    data: CorrectionCreate,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Create a new teacher correction."""
    correction = TeacherCorrection(
        teacher_id=user_id,
        **data.model_dump(),
    )
    db.add(correction)
    await db.flush()

    # Generate embedding for the question (background, non-blocking)
    try:
        from app.ai.router import get_embedding_provider
        provider = get_embedding_provider()
        embedding = await provider.embed(data.question)
        correction.question_embedding = embedding
    except Exception:
        pass  # Embedding will be generated later

    return CorrectionResponse.model_validate(correction)


@router.patch("/{correction_id}", response_model=CorrectionResponse)
async def update_correction(
    correction_id: str,
    data: CorrectionUpdate,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Update a teacher correction."""
    result = await db.execute(
        select(TeacherCorrection).where(TeacherCorrection.id == correction_id)
    )
    correction = result.scalar_one_or_none()
    if not correction:
        raise NotFoundError("التصحيح")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(correction, field, value)

    # Re-generate embedding if question changed
    if data.question:
        try:
            from app.ai.router import get_embedding_provider
            provider = get_embedding_provider()
            correction.question_embedding = await provider.embed(data.question)
        except Exception:
            pass

    return CorrectionResponse.model_validate(correction)


@router.delete("/{correction_id}", status_code=204)
async def delete_correction(
    correction_id: str,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Delete a teacher correction."""
    result = await db.execute(
        select(TeacherCorrection).where(TeacherCorrection.id == correction_id)
    )
    correction = result.scalar_one_or_none()
    if not correction:
        raise NotFoundError("التصحيح")
    await db.delete(correction)
