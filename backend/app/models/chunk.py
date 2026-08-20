"""ReferenceChunk model — document chunks with vector embeddings."""

from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, generate_uuid


class ReferenceChunk(Base, TimestampMixin):
    __tablename__ = "reference_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    reference_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("references.id", ondelete="CASCADE"), index=True,
    )

    # Content
    content: Mapped[str] = mapped_column(Text)

    # Vector embedding (768 dimensions for Gemini text-embedding-004)
    embedding = mapped_column(Vector(768), nullable=True)

    # Full-text search vector
    content_tsvector = mapped_column(TSVECTOR, nullable=True)

    # Source location
    page_number: Mapped[int | None] = mapped_column(Integer, default=None)
    section: Mapped[str | None] = mapped_column(String(500), default=None)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)

    # Rich metadata for filtering
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, default=None)

    # Relationships
    reference: Mapped["Reference"] = relationship(back_populates="chunks")

    # Indexes for hybrid search
    __table_args__ = (
        Index(
            "ix_reference_chunks_embedding_hnsw",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index(
            "ix_reference_chunks_content_tsvector",
            content_tsvector,
            postgresql_using="gin",
        ),
    )

    def __repr__(self) -> str:
        return f"<ReferenceChunk ref={self.reference_id} page={self.page_number}>"


from app.models.reference import Reference  # noqa: E402, F401
