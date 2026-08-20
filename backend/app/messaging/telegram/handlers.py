"""Telegram bot command and message handlers."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from app.core.logging import get_logger
from app.core.rate_limiter import RateLimiter
from app.database import async_session_factory
from app.messaging.telegram.formatter import (
    format_error_message,
    format_help_message,
    format_welcome_message,
    truncate_message,
)
from app.models.conversation import Conversation, Message, MessageRole
from app.models.student import Student
from app.models.subject import Subject
from app.rag.pipeline import RAGPipeline

logger = get_logger(__name__)

# Shared RAG pipeline instance
_rag_pipeline: RAGPipeline | None = None


def get_rag_pipeline() -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline


# ── Command Handlers ─────────────────────────────────────────


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command — register student and send welcome."""
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    async with async_session_factory() as db:
        student = await _get_or_create_student(db, user)
        await db.commit()

    await update.message.reply_text(
        format_welcome_message(user.first_name or "طالب"),
        parse_mode=ParseMode.MARKDOWN,
    )
    logger.info(f"Student started bot: {user.id} ({user.first_name})")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    if not update.message:
        return
    await update.message.reply_text(
        format_help_message(),
        parse_mode=ParseMode.MARKDOWN,
    )


async def subjects_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /subjects command — list available subjects."""
    if not update.message:
        return

    async with async_session_factory() as db:
        result = await db.execute(
            select(Subject).where(Subject.is_active.is_(True))
        )
        subjects = result.scalars().all()

    if not subjects:
        await update.message.reply_text("لا توجد مواد متاحة حالياً. 📭")
        return

    text = "📚 **المواد المتاحة:**\n\n"
    for subj in subjects:
        text += f"• {subj.name_ar}"
        if subj.name_en:
            text += f" ({subj.name_en})"
        text += "\n"

    text += "\nاكتب سؤالك عن أي مادة وسأساعدك! 🎓"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel command."""
    if not update.message:
        return
    await update.message.reply_text("تم إلغاء العملية. يمكنك طرح سؤال جديد. ✅")


# ── Message Handler ──────────────────────────────────────────


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages — the main question-answering flow."""
    if not update.effective_user or not update.message or not update.message.text:
        return

    user = update.effective_user
    question = update.message.text.strip()

    if not question:
        return

    logger.info(f"Question from {user.id}: {question[:100]}...")

    async with async_session_factory() as db:
        try:
            # Get or create student
            student = await _get_or_create_student(db, user)

            # Check rate limit
            try:
                from app.dependencies import _redis_pool
                if _redis_pool:
                    rate_limiter = RateLimiter(_redis_pool)
                    await rate_limiter.check_student_limit(student.id)
            except Exception as rate_err:
                if "429" in str(type(rate_err).__name__) or "RateLimit" in str(type(rate_err).__name__):
                    await update.message.reply_text(format_error_message("rate_limit"))
                    return
                # Don't fail the request if rate limiting itself fails
                logger.warning(f"Rate limit check failed: {rate_err}")

            # Send typing indicator
            await update.message.chat.send_action(ChatAction.TYPING)

            # Get or create active conversation
            conversation = await _get_or_create_conversation(db, student.id)

            # Load recent conversation history
            conv_history = await _load_conversation_history(db, conversation.id)

            # Save student message
            student_msg = Message(
                conversation_id=conversation.id,
                role=MessageRole.STUDENT,
                content=question,
            )
            db.add(student_msg)

            # Run RAG pipeline
            rag = get_rag_pipeline()
            response = await rag.answer(
                question,
                db,
                student_id=student.id,
                conversation_history=conv_history,
                conversation_summary=conversation.summary,
            )

            # Build full response text
            full_response = response.answer
            if response.citations_text:
                full_response += "\n" + response.citations_text

            # Save assistant message
            assistant_msg = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=response.answer,
                retrieved_chunks=response.retrieved_chunks,
                citations=response.citations_data,
                response_time_ms=response.latency_ms,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                ai_provider=response.provider,
                ai_model=response.model,
                confidence_score=response.confidence,
            )
            db.add(assistant_msg)

            # Update conversation
            conversation.message_count += 2
            if not conversation.title:
                conversation.title = question[:100]

            # Update student last seen
            student.last_seen_at = datetime.now(timezone.utc)

            await db.commit()

            # Send response (truncate if needed)
            await update.message.reply_text(
                truncate_message(full_response),
                parse_mode=ParseMode.MARKDOWN,
            )

        except Exception as e:
            logger.error(f"Error processing message from {user.id}: {e}")
            await update.message.reply_text(format_error_message("general"))


# ── Feedback Handler ─────────────────────────────────────────


async def feedback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle feedback reactions (👍/👎)."""
    # This will be implemented with inline keyboard callbacks
    pass


# ── Helper Functions ─────────────────────────────────────────


async def _get_or_create_student(db: AsyncSession, tg_user) -> Student:
    """Get existing student or create a new one from Telegram user info."""
    result = await db.execute(
        select(Student).where(Student.telegram_user_id == tg_user.id)
    )
    student = result.scalar_one_or_none()

    if student:
        # Update info if changed
        student.username = tg_user.username
        student.first_name = tg_user.first_name or ""
        student.last_name = tg_user.last_name
        student.last_seen_at = datetime.now(timezone.utc)
        return student

    # Create new student
    student = Student(
        telegram_user_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name or "",
        last_name=tg_user.last_name,
        preferred_language=tg_user.language_code or "ar",
    )
    db.add(student)
    await db.flush()  # Get the ID

    logger.info(f"New student registered: {student.display_name} (tg={tg_user.id})")
    return student


async def _get_or_create_conversation(db: AsyncSession, student_id: str) -> Conversation:
    """Get the student's active conversation or create a new one."""
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.student_id == student_id,
            Conversation.is_active.is_(True),
        )
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    conversation = result.scalar_one_or_none()

    if conversation:
        return conversation

    # Create new conversation
    conversation = Conversation(
        student_id=student_id,
        is_active=True,
    )
    db.add(conversation)
    await db.flush()
    return conversation


async def _load_conversation_history(
    db: AsyncSession, conversation_id: str, limit: int = 6
) -> list[dict]:
    """Load recent messages from a conversation for context."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    # Reverse to chronological order
    return [
        {
            "role": "user" if msg.role == MessageRole.STUDENT else "assistant",
            "content": msg.content,
        }
        for msg in reversed(messages)
    ]
