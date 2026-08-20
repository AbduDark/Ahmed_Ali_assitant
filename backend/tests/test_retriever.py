"""Tests for hybrid retriever and ranking fusion algorithms."""

from __future__ import annotations

import pytest
from app.rag.retriever import HybridRetriever, RetrievedChunk


def test_reciprocal_rank_fusion():
    """Verify RRF correctly prioritizes chunks found in both vector and keyword search."""
    retriever = HybridRetriever(embedding_service=None)  # type: ignore

    chunk_a = RetrievedChunk(chunk_id="chunk-1", content="Text A", score=0.9, reference_id="ref-1")
    chunk_b = RetrievedChunk(chunk_id="chunk-2", content="Text B", score=0.8, reference_id="ref-1")
    chunk_c = RetrievedChunk(chunk_id="chunk-3", content="Text C", score=0.7, reference_id="ref-2")

    vector_results = [chunk_a, chunk_b]
    keyword_results = [chunk_b, chunk_c]

    # chunk_b appears in both searches, so its RRF score should be boosted highest
    merged = retriever._reciprocal_rank_fusion(vector_results, keyword_results)

    assert len(merged) == 3
    # chunk-2 has 1/(60+2) + 1/(60+1) which is higher than chunk-1's 1/(60+1)
    assert merged[0].chunk_id == "chunk-2"
