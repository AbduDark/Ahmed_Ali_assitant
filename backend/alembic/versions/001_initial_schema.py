"""Initial database schema with pgvector and all tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("super_admin", "teacher", "assistant", "viewer", name="user_role"), nullable=False, default="teacher"),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Students
    op.create_table(
        "students",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("telegram_user_id", sa.BigInteger(), unique=True, nullable=False, index=True),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=False),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("grade", sa.String(100), nullable=True),
        sa.Column("preferred_language", sa.String(10), default="ar"),
        sa.Column("school", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Subjects
    op.create_table(
        "subjects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name_ar", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Grades
    op.create_table(
        "grades",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name_ar", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("order", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Units
    op.create_table(
        "units",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("subject_id", sa.String(36), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name_ar", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("order", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Lessons
    op.create_table(
        "lessons",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("unit_id", sa.String(36), sa.ForeignKey("units.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name_ar", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("order", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # References
    op.create_table(
        "references",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("subject_id", sa.String(36), sa.ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("grade_id", sa.String(36), sa.ForeignKey("grades.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("unit_id", sa.String(36), sa.ForeignKey("units.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("lesson_id", sa.String(36), sa.ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("file_path", sa.String(1000), nullable=True),
        sa.Column("file_name", sa.String(500), nullable=True),
        sa.Column("file_type", sa.String(50), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("source_url", sa.String(2000), nullable=True),
        sa.Column("language", sa.String(10), default="ar"),
        sa.Column("academic_year", sa.String(50), nullable=True),
        sa.Column("status", sa.Enum("pending", "processing", "ready", "failed", name="reference_status"), default="pending", nullable=False, index=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("chunk_count", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Reference Chunks
    op.create_table(
        "reference_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("reference_id", sa.String(36), sa.ForeignKey("references.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("section", sa.String(500), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Conversations
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("message_count", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Messages
    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("conversation_id", sa.String(36), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("role", sa.Enum("student", "assistant", "teacher", "system", name="message_role"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("retrieved_chunks", sa.JSON(), nullable=True),
        sa.Column("citations", sa.JSON(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("ai_provider", sa.String(50), nullable=True),
        sa.Column("ai_model", sa.String(100), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Teacher Instructions
    op.create_table(
        "teacher_instructions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("teacher_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), default=0),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Teacher Corrections
    op.create_table(
        "teacher_corrections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("teacher_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("question_embedding", Vector(768), nullable=True),
        sa.Column("bad_answer", sa.Text(), nullable=True),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # AI Usage Logs
    op.create_table(
        "ai_usage_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(50), nullable=False, index=True),
        sa.Column("model", sa.String(100), nullable=False, index=True),
        sa.Column("input_tokens", sa.Integer(), default=0),
        sa.Column("output_tokens", sa.Integer(), default=0),
        sa.Column("total_tokens", sa.Integer(), default=0),
        sa.Column("latency_ms", sa.Integer(), default=0),
        sa.Column("status", sa.String(50), default="success", index=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("request_type", sa.String(50), default="chat"),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("students.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Feedback
    op.create_table(
        "feedbacks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("message_id", sa.String(36), sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("student_id", sa.String(36), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("feedbacks")
    op.drop_table("ai_usage_logs")
    op.drop_table("teacher_corrections")
    op.drop_table("teacher_instructions")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("reference_chunks")
    op.drop_table("references")
    op.drop_table("lessons")
    op.drop_table("units")
    op.drop_table("grades")
    op.drop_table("subjects")
    op.drop_table("students")
    op.drop_table("users")
