"""Reference model — uploaded educational documents."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, SoftDeleteMixin, generate_uuid


class ReferenceStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Reference(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "references"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text, default=None)

    # Curriculum hierarchy
    subject_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("subjects.id"), index=True, default=None,
    )
    grade_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("grades.id"), default=None,
    )
    unit_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("units.id"), default=None,
    )
    lesson_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("lessons.id"), default=None,
    )

    # File info
    file_path: Mapped[str | None] = mapped_column(String(500), default=None)
    file_name: Mapped[str | None] = mapped_column(String(255), default=None)
    file_type: Mapped[str | None] = mapped_column(String(50), default=None)
    file_size: Mapped[int | None] = mapped_column(Integer, default=None)

    # URL source
    source_url: Mapped[str | None] = mapped_column(String(2048), default=None)

    # Metadata
    language: Mapped[str] = mapped_column(String(10), default="ar")
    academic_year: Mapped[str | None] = mapped_column(String(20), default=None)
    status: Mapped[ReferenceStatus] = mapped_column(
        Enum(ReferenceStatus, name="reference_status"),
        default=ReferenceStatus.PENDING,
        index=True,
    )
    page_count: Mapped[int | None] = mapped_column(Integer, default=None)
    chunk_count: Mapped[int | None] = mapped_column(Integer, default=None)
    error_message: Mapped[str | None] = mapped_column(Text, default=None)

    # Who uploaded it
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), default=None,
    )

    # Relationships
    subject: Mapped["Subject | None"] = relationship(back_populates="references")
    grade: Mapped["Grade | None"] = relationship()
    unit: Mapped["Unit | None"] = relationship()
    lesson: Mapped["Lesson | None"] = relationship()
    chunks: Mapped[list["ReferenceChunk"]] = relationship(
        back_populates="reference",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Reference {self.title} status={self.status.value}>"


from app.models.subject import Subject, Grade, Unit, Lesson  # noqa: E402, F401
from app.models.chunk import ReferenceChunk  # noqa: E402, F401
