"""TeacherInstruction model — custom AI behavior instructions."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, generate_uuid


class TeacherInstruction(Base, TimestampMixin):
    __tablename__ = "teacher_instructions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    teacher_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True,
    )
    content: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(255), default=None)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    teacher: Mapped["User"] = relationship(back_populates="instructions")

    def __repr__(self) -> str:
        return f"<TeacherInstruction {self.title or self.id[:8]}>"


from app.models.user import User  # noqa: E402, F401
