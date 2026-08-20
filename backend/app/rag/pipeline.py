"""Main RAG pipeline orchestrator."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import AIMessage, FailoverChain, create_failover_chain, get_embedding_provider
from app.config import settings
from app.core.logging import get_logger
from app.models.ai_usage import AIUsageLog
from app.models.instruction import TeacherInstruction
from app.rag.citation import extract_citation_data, format_citations
from app.rag.embedder import EmbeddingService
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import HybridRetriever, RetrievedChunk
from app.rag.validator import AnswerValidator

logger = get_logger(__name__)


@dataclass
class RAGResponse:
    """Complete response from the RAG pipeline."""
    answer: str
    citations_text: str = ""
    citations_data: list[dict] = field(default_factory=list)
    retrieved_chunks: list[dict] = field(default_factory=list)
    confidence: float = 0.0
    is_grounded: bool = False
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    provider: str = ""
    model: str = ""
    latency_ms: int = 0


class RAGPipeline:
    """
    Main RAG orchestrator.

    Flow:
    1. Retrieve relevant chunks (hybrid search)
    2. Load teacher instructions & corrections
    3. Build prompt
    4. Generate answer (with failover)
    5. Validate answer
    6. Format citations
    7. Log AI usage
    """

    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.validator = AnswerValidator()
        self._failover_chain: FailoverChain | None = None
        self._retriever: HybridRetriever | None = None

    def _get_failover_chain(self) -> FailoverChain:
        if self._failover_chain is None:
            self._failover_chain = create_failover_chain()
        return self._failover_chain

    def _get_retriever(self) -> HybridRetriever:
        if self._retriever is None:
            embedding_service = EmbeddingService(get_embedding_provider())
            self._retriever = HybridRetriever(embedding_service)
        return self._retriever

    async def answer(
        self,
        question: str,
        db: AsyncSession,
        *,
        student_id: str | None = None,
        conversation_history: list[dict] | None = None,
        conversation_summary: str | None = None,
        subject_id: str | None = None,
        unit_id: str | None = None,
        lesson_id: str | None = None,
    ) -> RAGResponse:
        """Process a student question through the full RAG pipeline."""
        start_time = time.monotonic()

        try:
            # Step 1: Retrieve relevant chunks
            retriever = self._get_retriever()
            retrieval_result = await retriever.retrieve(
                question, db,
                subject_id=subject_id,
                unit_id=unit_id,
                lesson_id=lesson_id,
            )

            # Step 2: Load teacher instructions
            teacher_instructions = await self._load_instructions(db)

            # Step 3: Build prompt
            messages = self.prompt_builder.build(
                question,
                retrieved_chunks=retrieval_result.chunks,
                teacher_instructions=teacher_instructions,
                teacher_corrections=retrieval_result.corrections,
                conversation_history=conversation_history,
                conversation_summary=conversation_summary,
            )

            # Step 4: Generate answer
            chain = self._get_failover_chain()
            ai_response = await chain.generate(messages, temperature=0.3, max_tokens=2048)

            # Step 5: Validate answer
            validated_answer, confidence, is_grounded = self.validator.validate(
                ai_response.content,
                retrieval_result.chunks,
                question,
            )

            # Step 6: Format citations
            citations_text = format_citations(retrieval_result.chunks) if is_grounded else ""
            citations_data = extract_citation_data(retrieval_result.chunks) if is_grounded else []

            # Step 7: Prepare retrieved chunks data for storage
            retrieved_chunks_data = [
                {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content[:500],  # Truncate for storage
                    "score": round(chunk.score, 4),
                    "reference_title": chunk.reference_title,
                    "page_number": chunk.page_number,
                }
                for chunk in retrieval_result.chunks
            ]

            latency_ms = int((time.monotonic() - start_time) * 1000)

            # Step 8: Log AI usage
            await self._log_usage(
                db,
                provider=ai_response.provider,
                model=ai_response.model,
                input_tokens=ai_response.input_tokens,
                output_tokens=ai_response.output_tokens,
                latency_ms=latency_ms,
                student_id=student_id,
                status="success",
            )

            return RAGResponse(
                answer=validated_answer,
                citations_text=citations_text,
                citations_data=citations_data,
                retrieved_chunks=retrieved_chunks_data,
                confidence=confidence,
                is_grounded=is_grounded,
                input_tokens=ai_response.input_tokens,
                output_tokens=ai_response.output_tokens,
                total_tokens=ai_response.total_tokens,
                provider=ai_response.provider,
                model=ai_response.model,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            logger.error(f"RAG pipeline failed: {e}")

            # Log the failure
            await self._log_usage(
                db,
                provider="unknown",
                model="unknown",
                input_tokens=0,
                output_tokens=0,
                latency_ms=latency_ms,
                student_id=student_id,
                status="error",
                error=str(e),
            )

            # Return friendly error message
            return RAGResponse(
                answer="عذراً، حدث خطأ أثناء معالجة سؤالك. يرجى المحاولة مرة أخرى.",
                latency_ms=latency_ms,
            )

    async def _load_instructions(self, db: AsyncSession) -> list[str]:
        """Load active teacher instructions."""
        result = await db.execute(
            select(TeacherInstruction)
            .where(TeacherInstruction.is_active.is_(True))
            .order_by(TeacherInstruction.priority.desc())
        )
        instructions = result.scalars().all()
        return [inst.content for inst in instructions]

    async def _log_usage(
        self,
        db: AsyncSession,
        *,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        student_id: str | None = None,
        status: str = "success",
        error: str | None = None,
    ) -> None:
        """Log AI usage to the database."""
        try:
            log = AIUsageLog(
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                latency_ms=latency_ms,
                status=status,
                error=error,
                request_type="chat",
                student_id=student_id,
            )
            db.add(log)
            # Don't commit here — let the caller's session handle it
        except Exception as e:
            logger.warning(f"Failed to log AI usage: {e}")
