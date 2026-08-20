"""Subject, Grade, Curriculum, Unit, and Lesson models."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, generate_uuid


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name_ar: Mapped[str] = mapped_column(String(255), index=True)
    name_en: Mapped[str | None] = mapped_column(String(255), default=None)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    units: Mapped[list["Unit"]] = relationship(
        back_populates="subject", lazy="selectin",
        order_by="Unit.order",
    )
    references: Mapped[list["Reference"]] = relationship(
        back_populates="subject", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Subject {self.name_ar}>"


class Grade(Base, TimestampMixin):
    __tablename__ = "grades"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name_ar: Mapped[str] = mapped_column(String(255))
    name_en: Mapped[str | None] = mapped_column(String(255), default=None)
    order: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<Grade {self.name_ar}>"


class Curriculum(Base, TimestampMixin):
    __tablename__ = "curricula"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name_ar: Mapped[str] = mapped_column(String(255))
    name_en: Mapped[str | None] = mapped_column(String(255), default=None)

    def __repr__(self) -> str:
        return f"<Curriculum {self.name_ar}>"


class Unit(Base, TimestampMixin):
    __tablename__ = "units"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    subject_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("subjects.id"), index=True,
    )
    name_ar: Mapped[str] = mapped_column(String(255))
    name_en: Mapped[str | None] = mapped_column(String(255), default=None)
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    subject: Mapped["Subject"] = relationship(back_populates="units")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="unit", lazy="selectin",
        order_by="Lesson.order",
    )

    def __repr__(self) -> str:
        return f"<Unit {self.name_ar}>"


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    unit_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("units.id"), index=True,
    )
    name_ar: Mapped[str] = mapped_column(String(255))
    name_en: Mapped[str | None] = mapped_column(String(255), default=None)
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    unit: Mapped["Unit"] = relationship(back_populates="lessons")

    def __repr__(self) -> str:
        return f"<Lesson {self.name_ar}>"


from app.models.reference import Reference  # noqa: E402, F401
