"""Conversation and Message models."""

from __future__ import annotations

import enum

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, generate_uuid


class MessageRole(str, enum.Enum):
    STUDENT = "student"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    student_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("students.id"), index=True,
    )
    subject_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("subjects.id"), default=None,
    )
    title: Mapped[str | None] = mapped_column(String(500), default=None)
    summary: Mapped[str | None] = mapped_column(Text, default=None)
    is_active: Mapped[bool] = mapped_column(default=True)
    message_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        lazy="selectin",
        order_by="Message.created_at",
    )

    def __repr__(self) -> str:
        return f"<Conversation {self.id[:8]} student={self.student_id[:8]}>"


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), index=True,
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole, name="message_role", values_callable=lambda x: [e.value for e in x])
    )
    content: Mapped[str] = mapped_column(Text)

    # RAG metadata (only for assistant messages)
    retrieved_chunks: Mapped[list | None] = mapped_column(JSONB, default=None)
    citations: Mapped[list | None] = mapped_column(JSONB, default=None)

    # Performance metadata
    response_time_ms: Mapped[int | None] = mapped_column(Integer, default=None)
    input_tokens: Mapped[int | None] = mapped_column(Integer, default=None)
    output_tokens: Mapped[int | None] = mapped_column(Integer, default=None)
    ai_provider: Mapped[str | None] = mapped_column(String(50), default=None)
    ai_model: Mapped[str | None] = mapped_column(String(100), default=None)
    confidence_score: Mapped[float | None] = mapped_column(Float, default=None)

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    feedback: Mapped[list["Feedback"]] = relationship(
        back_populates="message", lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Message {self.role.value} conv={self.conversation_id[:8]}>"


from app.models.student import Student  # noqa: E402, F401
from app.models.feedback import Feedback  # noqa: E402, F401
