"""Citation extraction and formatting."""

from __future__ import annotations

from app.rag.retriever import RetrievedChunk


def format_citations(chunks: list[RetrievedChunk]) -> str:
    """
    Format citations for display in Telegram messages.

    Only includes citations where we can confidently identify the source.
    Never fabricates page numbers.
    """
    if not chunks:
        return ""

    # Deduplicate by reference
    seen_refs: set[str] = set()
    unique_citations: list[dict] = []

    for chunk in chunks:
        ref_key = chunk.reference_id
        if ref_key in seen_refs:
            continue
        seen_refs.add(ref_key)

        citation: dict = {}
        if chunk.reference_title:
            citation["title"] = chunk.reference_title
        if chunk.page_number:
            citation["page"] = chunk.page_number
        if chunk.section:
            citation["section"] = chunk.section

        # Get unit/lesson from metadata
        meta = chunk.metadata or {}
        if meta.get("unit_name"):
            citation["unit"] = meta["unit_name"]
        if meta.get("lesson_name"):
            citation["lesson"] = meta["lesson_name"]

        if citation:
            unique_citations.append(citation)

    if not unique_citations:
        return ""

    # Format as text
    lines = ["\n📚 المصدر:"]
    for citation in unique_citations:
        parts = []
        if "title" in citation:
            parts.append(citation["title"])
        if "unit" in citation:
            parts.append(f"الوحدة: {citation['unit']}")
        if "lesson" in citation:
            parts.append(f"الدرس: {citation['lesson']}")
        if "page" in citation:
            parts.append(f"صفحة {citation['page']}")
        if "section" in citation:
            parts.append(f"القسم: {citation['section']}")

        lines.append("• " + " | ".join(parts))

    return "\n".join(lines)


def extract_citation_data(chunks: list[RetrievedChunk]) -> list[dict]:
    """
    Extract structured citation data for storage in the database.

    Returns list of dicts suitable for JSON storage.
    """
    citations = []
    seen: set[str] = set()

    for chunk in chunks:
        key = f"{chunk.reference_id}:{chunk.page_number}"
        if key in seen:
            continue
        seen.add(key)

        citations.append({
            "reference_id": chunk.reference_id,
            "reference_title": chunk.reference_title,
            "page_number": chunk.page_number,
            "section": chunk.section,
            "chunk_id": chunk.chunk_id,
            "score": round(chunk.score, 4),
        })

    return citations
