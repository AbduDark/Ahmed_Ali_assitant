"""Tests for RAG prompt builder, validator, and citation formatting."""

from __future__ import annotations

import pytest
from app.rag.citation import format_citations
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import RetrievedChunk
from app.rag.validator import AnswerValidator, LOW_CONFIDENCE_MSG_AR


def test_prompt_builder():
    """Verify prompt builder builds structured messages with citations and rules."""
    builder = PromptBuilder()

    chunks = [
        RetrievedChunk(
            chunk_id="c1",
            content="بنى الملك خوفو الهرم الأكبر في الجيزة.",
            score=0.92,
            reference_id="r1",
            reference_title="كتاب التاريخ للصف الأول الثانوي",
            page_number=45,
            section="عصر بناة الأهرام",
        )
    ]

    messages = builder.build(
        question="من بنى الهرم الأكبر؟",
        retrieved_chunks=chunks,
        teacher_instructions=["اشرح بأسلوب مبسط وشجع الطالب دائماً."],
    )

    assert len(messages) == 2
    assert messages[0].role == "system"
    assert "أنت مساعد تعليمي ذكي" in messages[0].content
    assert "اشرح بأسلوب مبسط" in messages[0].content
    assert messages[1].role == "user"
    assert "بنى الملك خوفو الهرم الأكبر" in messages[1].content
    assert "سؤال الطالب: من بنى الهرم الأكبر؟" in messages[1].content


def test_answer_validator_no_chunks():
    """Verify ungrounded queries return polite fallback message."""
    validator = AnswerValidator(confidence_threshold=0.5)
    answer, confidence, is_grounded = validator.validate(
        answer="إجابة تم إنشاؤها بدون مراجع",
        retrieved_chunks=[],
        question="سؤال خارج المنهج",
    )

    assert is_grounded is False
    assert confidence == 0.0
    assert answer == LOW_CONFIDENCE_MSG_AR


def test_citation_formatting():
    """Verify clean Arabic citation generation without duplicate references."""
    chunks = [
        RetrievedChunk(
            chunk_id="c1",
            content="نص 1",
            score=0.88,
            reference_id="r1",
            reference_title="كتاب الجغرافيا العامة",
            page_number=12,
        ),
        RetrievedChunk(
            chunk_id="c2",
            content="نص 2",
            score=0.82,
            reference_id="r1",  # Duplicate ref id, should deduplicate
            reference_title="كتاب الجغرافيا العامة",
            page_number=12,
        ),
    ]

    formatted = format_citations(chunks)
    assert "📚 المصدر:" in formatted
    assert "كتاب الجغرافيا العامة" in formatted
    assert "صفحة 12" in formatted
    assert formatted.count("كتاب الجغرافيا العامة") == 1
