"""Text chunking with configurable size and overlap."""

from __future__ import annotations

from dataclasses import dataclass

import tiktoken

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ChunkMetadata:
    """Metadata for a single chunk."""
    page_number: int | None = None
    section: str | None = None
    chunk_index: int = 0


class TextChunker:
    """
    Split text into overlapping chunks of configurable token size.

    Respects sentence and paragraph boundaries when possible.
    """

    def __init__(
        self,
        chunk_size: int = 600,
        chunk_overlap: int = 75,
        encoding_name: str = "cl100k_base",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._encoder = tiktoken.get_encoding(encoding_name)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self._encoder.encode(text))

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences, respecting Arabic and English punctuation."""
        import re
        # Split on sentence-ending punctuation followed by whitespace
        sentences = re.split(r'(?<=[.!?،؟。])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_text(
        self,
        text: str,
        *,
        page_number: int | None = None,
        section: str | None = None,
    ) -> list[dict]:
        """
        Split text into overlapping chunks.

        Returns list of dicts with 'content', 'page_number', 'section', 'chunk_index'.
        """
        if not text or not text.strip():
            return []

        sentences = self._split_into_sentences(text)
        if not sentences:
            return []

        chunks: list[dict] = []
        current_chunk: list[str] = []
        current_tokens = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            # If a single sentence exceeds chunk_size, split it by words
            if sentence_tokens > self.chunk_size:
                # Flush current chunk first
                if current_chunk:
                    chunks.append({
                        "content": " ".join(current_chunk),
                        "page_number": page_number,
                        "section": section,
                        "chunk_index": chunk_index,
                    })
                    chunk_index += 1
                    current_chunk = []
                    current_tokens = 0

                # Split long sentence into word groups
                words = sentence.split()
                word_chunk: list[str] = []
                word_tokens = 0
                for word in words:
                    wt = self._count_tokens(word)
                    if word_tokens + wt > self.chunk_size and word_chunk:
                        chunks.append({
                            "content": " ".join(word_chunk),
                            "page_number": page_number,
                            "section": section,
                            "chunk_index": chunk_index,
                        })
                        chunk_index += 1
                        # Keep overlap
                        overlap_words = word_chunk[-max(1, len(word_chunk) // 4):]
                        word_chunk = overlap_words
                        word_tokens = self._count_tokens(" ".join(word_chunk))
                    word_chunk.append(word)
                    word_tokens += wt

                if word_chunk:
                    current_chunk = word_chunk
                    current_tokens = word_tokens
                continue

            # Check if adding this sentence exceeds the limit
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "content": " ".join(current_chunk),
                    "page_number": page_number,
                    "section": section,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1

                # Create overlap from end of current chunk
                overlap_chunk: list[str] = []
                overlap_tokens = 0
                for s in reversed(current_chunk):
                    st = self._count_tokens(s)
                    if overlap_tokens + st > self.chunk_overlap:
                        break
                    overlap_chunk.insert(0, s)
                    overlap_tokens += st

                current_chunk = overlap_chunk
                current_tokens = overlap_tokens

            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        # Don't forget the last chunk
        if current_chunk:
            chunks.append({
                "content": " ".join(current_chunk),
                "page_number": page_number,
                "section": section,
                "chunk_index": chunk_index,
            })

        return chunks

    def chunk_pages(
        self,
        pages: list[tuple[int, str]],
    ) -> list[dict]:
        """
        Chunk multiple pages, preserving page numbers.

        Args:
            pages: List of (page_number, text) tuples.

        Returns:
            Combined list of chunk dicts across all pages.
        """
        all_chunks: list[dict] = []
        global_index = 0

        for page_number, text in pages:
            page_chunks = self.chunk_text(
                text,
                page_number=page_number,
            )
            for chunk in page_chunks:
                chunk["chunk_index"] = global_index
                all_chunks.append(chunk)
                global_index += 1

        logger.info(f"Chunked {len(pages)} pages into {len(all_chunks)} chunks")
        return all_chunks
