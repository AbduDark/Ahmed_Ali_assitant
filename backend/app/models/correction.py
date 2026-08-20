"""TeacherCorrection model — teacher-approved answer corrections."""

from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, generate_uuid


class TeacherCorrection(Base, TimestampMixin):
    __tablename__ = "teacher_corrections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    teacher_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True,
    )
    question: Mapped[str] = mapped_column(Text)
    bad_answer: Mapped[str | None] = mapped_column(Text, default=None)
    correct_answer: Mapped[str] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(String(100), default=None)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), default=None)

    # Embedding for semantic matching during RAG
    question_embedding = mapped_column(Vector(768), nullable=True)

    # Relationships
    teacher: Mapped["User"] = relationship(back_populates="corrections")

    def __repr__(self) -> str:
        return f"<TeacherCorrection {self.id[:8]} subj={self.subject}>"


from app.models.user import User  # noqa: E402, F401
