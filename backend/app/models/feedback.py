"""Feedback model — student ratings on AI answers."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, generate_uuid


class Feedback(Base, TimestampMixin):
    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    message_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("messages.id"), index=True,
    )
    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id"), index=True,
    )
    rating: Mapped[int] = mapped_column(Integer)  # 1 = positive, -1 = negative
    comment: Mapped[str | None] = mapped_column(Text, default=None)

    # Relationships
    message: Mapped["Message"] = relationship(back_populates="feedback")
    student: Mapped["Student"] = relationship(back_populates="feedback")

    def __repr__(self) -> str:
        return f"<Feedback msg={self.message_id[:8]} rating={self.rating}>"


from app.models.conversation import Message  # noqa: E402, F401
from app.models.student import Student  # noqa: E402, F401
