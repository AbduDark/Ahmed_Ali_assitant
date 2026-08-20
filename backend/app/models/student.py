"""Student model — students interact via Telegram."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, generate_uuid


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), default=None)
    first_name: Mapped[str] = mapped_column(String(255), default="")
    last_name: Mapped[str | None] = mapped_column(String(255), default=None)
    grade: Mapped[str | None] = mapped_column(String(100), default=None)
    preferred_language: Mapped[str] = mapped_column(String(10), default="ar")
    school: Mapped[str | None] = mapped_column(String(255), default=None)
    curriculum: Mapped[str | None] = mapped_column(String(255), default=None)
    academic_year: Mapped[str | None] = mapped_column(String(20), default=None)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(default=None)

    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="student", lazy="selectin",
    )
    feedback: Mapped[list["Feedback"]] = relationship(
        back_populates="student", lazy="selectin",
    )

    @property
    def display_name(self) -> str:
        parts = [self.first_name]
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) or self.username or str(self.telegram_user_id)

    def __repr__(self) -> str:
        return f"<Student {self.display_name} tg={self.telegram_user_id}>"


from app.models.conversation import Conversation  # noqa: E402, F401
from app.models.feedback import Feedback  # noqa: E402, F401
