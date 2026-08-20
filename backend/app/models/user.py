"""User model — teachers and admins."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, SoftDeleteMixin, generate_uuid


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    TEACHER = "teacher"
    ASSISTANT = "assistant"


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.TEACHER,
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    instructions: Mapped[list["TeacherInstruction"]] = relationship(
        back_populates="teacher", lazy="selectin",
    )
    corrections: Mapped[list["TeacherCorrection"]] = relationship(
        back_populates="teacher", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role.value}>"


# Avoid circular import — these are imported at runtime by SQLAlchemy
from app.models.instruction import TeacherInstruction  # noqa: E402, F401
from app.models.correction import TeacherCorrection  # noqa: E402, F401
