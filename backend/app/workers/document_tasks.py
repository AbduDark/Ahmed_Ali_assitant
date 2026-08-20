"""Background tasks for document processing."""

from __future__ import annotations

from app.core.logging import get_logger

logger = get_logger(__name__)


async def process_document(ctx: dict, reference_id: str) -> None:
    """
    Background job: process a reference document.
    Extracts text, generates embeddings, and saves chunks.
    """
    from app.document.processor import DocumentProcessor

    db_factory = ctx["db_factory"]
    async with db_factory() as db:
        processor = DocumentProcessor()
        logger.info(f"Worker started processing document: {reference_id}")
        await processor.process_reference(reference_id, db)
        await db.commit()
        logger.info(f"Worker finished processing document: {reference_id}")
