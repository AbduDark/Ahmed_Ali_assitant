"""Hybrid retriever — vector search + keyword search with Reciprocal Rank Fusion."""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import get_logger
from app.models.chunk import ReferenceChunk
from app.models.correction import TeacherCorrection
from app.models.reference import Reference, ReferenceStatus
from app.rag.embedder import EmbeddingService

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    """A single retrieved chunk with its relevance score."""
    chunk_id: str
    content: str
    score: float
    reference_id: str
    reference_title: str = ""
    page_number: int | None = None
    section: str | None = None
    subject_id: str | None = None
    unit_id: str | None = None
    lesson_id: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """Result of a retrieval query."""
    chunks: list[RetrievedChunk]
    corrections: list[dict] = field(default_factory=list)
    query: str = ""


class HybridRetriever:
    """
    Hybrid retrieval using:
    1. Vector similarity search (pgvector cosine distance)
    2. Keyword search (PostgreSQL tsvector)
    3. Reciprocal Rank Fusion (RRF) to merge results
    4. Metadata filtering (subject, grade, unit, lesson)
    """

    RRF_K = 60  # RRF constant

    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service

    async def retrieve(
        self,
        query: str,
        db: AsyncSession,
        *,
        top_k: int | None = None,
        subject_id: str | None = None,
        unit_id: str | None = None,
        lesson_id: str | None = None,
        similarity_threshold: float | None = None,
    ) -> RetrievalResult:
        """
        Perform hybrid retrieval for a query.

        Combines vector search and keyword search results using RRF.
        """
        top_k = top_k or settings.rag_top_k
        threshold = similarity_threshold or settings.rag_similarity_threshold

        # Generate query embedding
        query_embedding = await self.embedding_service.embed_query(query)

        # Run both searches
        vector_results = await self._vector_search(
            query_embedding, db,
            top_k=top_k * 2,  # Get more candidates for RRF
            subject_id=subject_id,
            unit_id=unit_id,
            lesson_id=lesson_id,
        )

        keyword_results = await self._keyword_search(
            query, db,
            top_k=top_k * 2,
            subject_id=subject_id,
            unit_id=unit_id,
            lesson_id=lesson_id,
        )

        # Merge with RRF
        merged = self._reciprocal_rank_fusion(vector_results, keyword_results)

        # Apply threshold and limit
        filtered = [
            chunk for chunk in merged
            if chunk.score >= threshold
        ][:top_k]

        # Also check teacher corrections
        corrections = await self._find_corrections(
            query_embedding, db, top_k=3
        )

        logger.info(
            f"Retrieved {len(filtered)} chunks "
            f"(vector={len(vector_results)}, keyword={len(keyword_results)}, "
            f"corrections={len(corrections)})"
        )

        return RetrievalResult(
            chunks=filtered,
            corrections=corrections,
            query=query,
        )

    async def _vector_search(
        self,
        query_embedding: list[float],
        db: AsyncSession,
        *,
        top_k: int = 10,
        subject_id: str | None = None,
        unit_id: str | None = None,
        lesson_id: str | None = None,
    ) -> list[RetrievedChunk]:
        """Cosine similarity search using pgvector."""
        # Build the query with cosine distance
        distance_expr = ReferenceChunk.embedding.cosine_distance(query_embedding)

        query = (
            select(
                ReferenceChunk,
                (1 - distance_expr).label("similarity"),
                Reference.title.label("ref_title"),
                Reference.subject_id.label("ref_subject_id"),
                Reference.unit_id.label("ref_unit_id"),
                Reference.lesson_id.label("ref_lesson_id"),
            )
            .join(Reference, ReferenceChunk.reference_id == Reference.id)
            .where(
                Reference.status == ReferenceStatus.READY,
                Reference.deleted_at.is_(None),
                ReferenceChunk.embedding.isnot(None),
            )
            .order_by(distance_expr)
            .limit(top_k)
        )

        # Apply metadata filters
        if subject_id:
            query = query.where(Reference.subject_id == subject_id)
        if unit_id:
            query = query.where(Reference.unit_id == unit_id)
        if lesson_id:
            query = query.where(Reference.lesson_id == lesson_id)

        result = await db.execute(query)
        rows = result.all()

        chunks = []
        for row in rows:
            chunk = row[0]
            similarity = float(row[1])
            ref_title = row[2]
            ref_subject_id = row[3]
            ref_unit_id = row[4]
            ref_lesson_id = row[5]

            chunks.append(RetrievedChunk(
                chunk_id=chunk.id,
                content=chunk.content,
                score=similarity,
                reference_id=chunk.reference_id,
                reference_title=ref_title or "",
                page_number=chunk.page_number,
                section=chunk.section,
                subject_id=ref_subject_id,
                unit_id=ref_unit_id,
                lesson_id=ref_lesson_id,
                metadata=chunk.metadata_json or {},
            ))

        return chunks

    async def _keyword_search(
        self,
        query: str,
        db: AsyncSession,
        *,
        top_k: int = 10,
        subject_id: str | None = None,
        unit_id: str | None = None,
        lesson_id: str | None = None,
    ) -> list[RetrievedChunk]:
        """Full-text keyword search using PostgreSQL tsvector."""
        # Use plainto_tsquery for simple query parsing
        # Support both Arabic and English
        ts_query = func.plainto_tsquery("simple", query)

        query_stmt = (
            select(
                ReferenceChunk,
                func.ts_rank(
                    func.to_tsvector("simple", ReferenceChunk.content),
                    ts_query,
                ).label("rank"),
                Reference.title.label("ref_title"),
                Reference.subject_id.label("ref_subject_id"),
                Reference.unit_id.label("ref_unit_id"),
                Reference.lesson_id.label("ref_lesson_id"),
            )
            .join(Reference, ReferenceChunk.reference_id == Reference.id)
            .where(
                Reference.status == ReferenceStatus.READY,
                Reference.deleted_at.is_(None),
                func.to_tsvector("simple", ReferenceChunk.content).op("@@")(ts_query),
            )
            .order_by(text("rank DESC"))
            .limit(top_k)
        )

        if subject_id:
            query_stmt = query_stmt.where(Reference.subject_id == subject_id)
        if unit_id:
            query_stmt = query_stmt.where(Reference.unit_id == unit_id)
        if lesson_id:
            query_stmt = query_stmt.where(Reference.lesson_id == lesson_id)

        result = await db.execute(query_stmt)
        rows = result.all()

        chunks = []
        for row in rows:
            chunk = row[0]
            rank = float(row[1])
            ref_title = row[2]

            chunks.append(RetrievedChunk(
                chunk_id=chunk.id,
                content=chunk.content,
                score=rank,
                reference_id=chunk.reference_id,
                reference_title=ref_title or "",
                page_number=chunk.page_number,
                section=chunk.section,
                subject_id=row[3],
                unit_id=row[4],
                lesson_id=row[5],
                metadata=chunk.metadata_json or {},
            ))

        return chunks

    def _reciprocal_rank_fusion(
        self,
        vector_results: list[RetrievedChunk],
        keyword_results: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        """Merge results using Reciprocal Rank Fusion (RRF)."""
        scores: dict[str, float] = {}
        chunk_map: dict[str, RetrievedChunk] = {}

        # Score vector results
        for rank, chunk in enumerate(vector_results, start=1):
            rrf_score = 1.0 / (self.RRF_K + rank)
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0) + rrf_score
            chunk_map[chunk.chunk_id] = chunk

        # Score keyword results
        for rank, chunk in enumerate(keyword_results, start=1):
            rrf_score = 1.0 / (self.RRF_K + rank)
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0) + rrf_score
            if chunk.chunk_id not in chunk_map:
                chunk_map[chunk.chunk_id] = chunk

        # Sort by combined score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        results = []
        for chunk_id in sorted_ids:
            chunk = chunk_map[chunk_id]
            chunk.score = scores[chunk_id]
            results.append(chunk)

        return results

    async def _find_corrections(
        self,
        query_embedding: list[float],
        db: AsyncSession,
        *,
        top_k: int = 3,
    ) -> list[dict]:
        """Find relevant teacher corrections using vector similarity."""
        try:
            distance_expr = TeacherCorrection.question_embedding.cosine_distance(
                query_embedding
            )

            query = (
                select(
                    TeacherCorrection,
                    (1 - distance_expr).label("similarity"),
                )
                .where(TeacherCorrection.question_embedding.isnot(None))
                .order_by(distance_expr)
                .limit(top_k)
            )

            result = await db.execute(query)
            rows = result.all()

            corrections = []
            for row in rows:
                correction = row[0]
                similarity = float(row[1])

                if similarity > 0.8:  # High threshold for corrections
                    corrections.append({
                        "question": correction.question,
                        "correct_answer": correction.correct_answer,
                        "similarity": similarity,
                    })

            return corrections

        except Exception as e:
            logger.warning(f"Correction search failed: {e}")
            return []
