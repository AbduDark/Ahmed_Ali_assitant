"""Tests for the Arabic and multilingual text chunker."""

from __future__ import annotations

import pytest
from app.rag.chunker import TextChunker


def test_chunker_empty_input():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_text("")
    assert chunks == []


def test_chunker_arabic_text():
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    text = (
        "تقع جمهورية مصر العربية في الركن الشمالي الشرقي من قارة أفريقيا. "
        "يحدها من الشمال البحر المتوسط، ومن الشرق البحر الأحمر. "
        "يمتد نهر النيل من الجنوب إلى الشمال ليصب في البحر المتوسط مكوناً الدلتا الخصبة."
    )

    chunks = chunker.chunk_text(text, page_number=1, section="الموقع الجغرافي")
    assert len(chunks) >= 1
    assert all("content" in c for c in chunks)
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["section"] == "الموقع الجغرافي"


def test_chunker_pages_preserves_page_numbers():
    chunker = TextChunker(chunk_size=80, chunk_overlap=10)
    pages = [
        (1, "الصفحة الأولى تحتوي على معلومات تاريخية عن العصر الفرعوني."),
        (2, "الصفحة الثانية تتناول عصر الدولة القديمة وبناء الأهرامات في الجيزة."),
    ]

    all_chunks = chunker.chunk_pages(pages)
    assert len(all_chunks) == 2
    assert all_chunks[0]["page_number"] == 1
    assert all_chunks[1]["page_number"] == 2
