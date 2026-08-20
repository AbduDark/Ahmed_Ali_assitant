"""Reference management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.dependencies import CurrentUserId
from app.schemas.reference import ReferenceCreate, ReferenceListResponse, ReferenceResponse
from app.services.reference_service import ReferenceService

router = APIRouter(prefix="/references", tags=["References"])


@router.post("", response_model=ReferenceResponse, status_code=201)
async def create_reference(
    title: str = Form(...),
    description: str | None = Form(None),
    subject_id: str | None = Form(None),
    grade_id: str | None = Form(None),
    unit_id: str | None = Form(None),
    lesson_id: str | None = Form(None),
    academic_year: str | None = Form(None),
    language: str = Form("ar"),
    source_url: str | None = Form(None),
    file: UploadFile | None = File(None),
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Upload a new reference document."""
    data = ReferenceCreate(
        title=title,
        description=description,
        subject_id=subject_id,
        grade_id=grade_id,
        unit_id=unit_id,
        lesson_id=lesson_id,
        academic_year=academic_year,
        language=language,
        source_url=source_url,
    )

    reference = await ReferenceService.create_reference(data, file, user_id, db)

    # Enqueue document processing job if file or URL was provided
    if reference.file_path or reference.source_url:
        try:
            from app.dependencies import _redis_pool
            if _redis_pool:
                from arq import ArqRedis
                redis: ArqRedis = _redis_pool  # type: ignore
                await redis.enqueue_job("process_document", reference.id)
            else:
                # Direct background execution fallback
                import asyncio
                from app.document.processor import DocumentProcessor
                from app.database import async_session_factory
                async def _bg_task(ref_id: str):
                    async with async_session_factory() as s:
                        p = DocumentProcessor()
                        await p.process_reference(ref_id, s)
                asyncio.create_task(_bg_task(reference.id))
        except Exception:
            pass

    return ReferenceResponse.model_validate(reference)


@router.get("", response_model=ReferenceListResponse)
async def list_references(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
    subject_id: str | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List references with optional filtering."""
    references, total = await ReferenceService.list_references(
        db, subject_id=subject_id, status=status, skip=skip, limit=limit,
    )
    return ReferenceListResponse(
        references=[ReferenceResponse.model_validate(r) for r in references],
        total=total,
    )


@router.get("/{reference_id}", response_model=ReferenceResponse)
async def get_reference(
    reference_id: str,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Get a reference by ID."""
    reference = await ReferenceService.get_reference(reference_id, db)
    return ReferenceResponse.model_validate(reference)


@router.delete("/{reference_id}", status_code=204)
async def delete_reference(
    reference_id: str,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Delete a reference (soft-delete)."""
    await ReferenceService.delete_reference(reference_id, db)


@router.post("/{reference_id}/reprocess", response_model=ReferenceResponse)
async def reprocess_reference(
    reference_id: str,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """Trigger reprocessing of a reference document."""
    reference = await ReferenceService.get_reference(reference_id, db)

    from app.models.reference import ReferenceStatus
    reference.status = ReferenceStatus.PENDING

    # Enqueue processing
    try:
        from app.dependencies import _redis_pool
        if _redis_pool:
            from arq import ArqRedis
            redis: ArqRedis = _redis_pool  # type: ignore
            await redis.enqueue_job("process_document", reference.id)
    except Exception:
        pass

    return ReferenceResponse.model_validate(reference)
