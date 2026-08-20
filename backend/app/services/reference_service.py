"""Reference management service."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core import FileTooLargeError, NotFoundError, UnsupportedFileTypeError
from app.core.logging import get_logger
from app.models.reference import Reference, ReferenceStatus
from app.schemas.reference import ReferenceCreate

logger = get_logger(__name__)

ALLOWED_FILE_TYPES = {".pdf", ".docx", ".txt", ".md", ".pptx"}


class ReferenceService:
    """Reference management business logic."""

    @staticmethod
    async def create_reference(
        data: ReferenceCreate,
        file: UploadFile | None,
        user_id: str,
        db: AsyncSession,
    ) -> Reference:
        """Create a new reference with optional file upload."""
        file_path = None
        file_name = None
        file_type = None
        file_size = None

        if file:
            # Validate file type
            ext = Path(file.filename or "").suffix.lower()
            if ext not in ALLOWED_FILE_TYPES:
                raise UnsupportedFileTypeError(ext)

            # Read and validate file size
            content = await file.read()
            if len(content) > settings.max_file_size_bytes:
                raise FileTooLargeError(settings.max_file_size_mb)

            # Save file
            file_id = str(uuid.uuid4())
            upload_dir = Path(settings.upload_dir) / "references"
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path_obj = upload_dir / f"{file_id}{ext}"
            file_path_obj.write_bytes(content)

            file_path = str(file_path_obj)
            file_name = file.filename
            file_type = ext.lstrip(".")
            file_size = len(content)

        reference = Reference(
            title=data.title,
            description=data.description,
            subject_id=data.subject_id,
            grade_id=data.grade_id,
            unit_id=data.unit_id,
            lesson_id=data.lesson_id,
            academic_year=data.academic_year,
            language=data.language,
            source_url=data.source_url,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            status=ReferenceStatus.PENDING if (file_path or data.source_url) else ReferenceStatus.READY,
            created_by=user_id,
        )
        db.add(reference)
        await db.flush()

        logger.info(f"Reference created: {reference.title} ({reference.id})")
        return reference

    @staticmethod
    async def get_reference(reference_id: str, db: AsyncSession) -> Reference:
        """Get a reference by ID."""
        result = await db.execute(
            select(Reference).where(
                Reference.id == reference_id,
                Reference.deleted_at.is_(None),
            )
        )
        reference = result.scalar_one_or_none()
        if not reference:
            raise NotFoundError("المرجع")
        return reference

    @staticmethod
    async def list_references(
        db: AsyncSession,
        *,
        subject_id: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Reference], int]:
        """List references with optional filtering."""
        query = select(Reference).where(Reference.deleted_at.is_(None))
        count_query = select(func.count(Reference.id)).where(Reference.deleted_at.is_(None))

        if subject_id:
            query = query.where(Reference.subject_id == subject_id)
            count_query = count_query.where(Reference.subject_id == subject_id)

        if status:
            query = query.where(Reference.status == status)
            count_query = count_query.where(Reference.status == status)

        query = query.order_by(Reference.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        references = list(result.scalars().all())

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        return references, total

    @staticmethod
    async def delete_reference(reference_id: str, db: AsyncSession) -> None:
        """Soft-delete a reference."""
        result = await db.execute(
            select(Reference).where(Reference.id == reference_id)
        )
        reference = result.scalar_one_or_none()
        if not reference:
            raise NotFoundError("المرجع")

        from datetime import datetime, timezone
        reference.deleted_at = datetime.now(timezone.utc)

        # Delete file
        if reference.file_path and os.path.exists(reference.file_path):
            try:
                os.remove(reference.file_path)
            except OSError as e:
                logger.warning(f"Failed to delete file {reference.file_path}: {e}")

        logger.info(f"Reference deleted: {reference.title} ({reference.id})")
