"""Telegram bot command and message handlers with real-time typing and interactive UX."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
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


# Persistent Quick Reply Keyboard
QUICK_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📚 المواد المتاحة"), KeyboardButton("❓ مساعدة")],
        [KeyboardButton("🔄 محادثة جديدة")],
    ],
    resize_keyboard=True,
    is_persistent=True,
)


def get_answer_inline_keyboard() -> InlineKeyboardMarkup:
    """Create interactive feedback and action buttons for AI answers."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👍 إجابة ممتازة", callback_data="feedback_good"),
            InlineKeyboardButton("👎 تحتاج توضيح", callback_data="feedback_bad"),
        ],
        [
            InlineKeyboardButton("📚 المواد الدراسية", callback_data="btn_subjects"),
            InlineKeyboardButton("❓ مساعدة", callback_data="btn_help"),
        ],
    ])


async def _keep_typing(chat, stop_event: asyncio.Event) -> None:
    """Continuously send typing action every 3.5 seconds until stop_event is set."""
    while not stop_event.is_set():
        try:
            await chat.send_action(ChatAction.TYPING)
        except Exception:
            pass
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=3.5)
        except asyncio.TimeoutError:
            pass


# ── Command Handlers ─────────────────────────────────────────


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command — register student and send welcome."""
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    async with async_session_factory() as db:
        student = await _get_or_create_student(db, user)
        await db.commit()

    welcome_text = format_welcome_message(user.first_name or "طالب")
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=QUICK_MENU_KEYBOARD,
    )
    logger.info(f"Student started bot: {user.id} ({user.first_name})")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    if not update.message:
        return
    await update.message.reply_text(
        format_help_message(),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=QUICK_MENU_KEYBOARD,
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
        await update.message.reply_text(
            "📚 **المواد الدراسية:**\n\nلا توجد مواد مضافة حالياً في النظام.\nيمكنك طرح سؤالك في التاريخ أو الجغرافيا مباشرة وسأساعدك! 🎓",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=QUICK_MENU_KEYBOARD,
        )
        return

    text = "📚 **المواد الدراسية المتاحة:**\n\n"
    for subj in subjects:
        text += f"• **{subj.name_ar}**"
        if subj.name_en:
            text += f" ({subj.name_en})"
        if subj.description:
            text += f" - {subj.description}"
        text += "\n"

    text += "\n💡 *اكتب سؤالك عن أي درس أو مفهوم وسأجيبك فوراً!*"
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=QUICK_MENU_KEYBOARD,
    )


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel or starting fresh conversation."""
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    async with async_session_factory() as db:
        student = await _get_or_create_student(db, user)
        # Archive current conversation
        result = await db.execute(
            select(Conversation)
            .where(Conversation.student_id == student.id, Conversation.is_active.is_(True))
        )
        for conv in result.scalars().all():
            conv.is_active = False
        await db.commit()

    await update.message.reply_text(
        "✨ تم بدء جلسة محادثة جديدة بنجاح! تفضل بطرح سؤالك الجديد. 🎓",
        reply_markup=QUICK_MENU_KEYBOARD,
    )


# ── Callback Query Handler (Interactive Buttons) ────────────


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button reactions and navigation."""
    query = update.callback_query
    if not query:
        return

    await query.answer()
    data = query.data

    if data == "feedback_good":
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ شكراً لتقييمك الإيجابي! سعداء بمساعدتك 🎓", callback_data="noop")]
            ])
        )
    elif data == "feedback_bad":
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 تم تسجيل ملاحظتك وسنعمل على تحسين الشرح", callback_data="noop")]
            ])
        )
    elif data == "btn_subjects":
        # Send subjects list
        async with async_session_factory() as db:
            result = await db.execute(select(Subject).where(Subject.is_active.is_(True)))
            subjects = result.scalars().all()

        if not subjects:
            await query.message.reply_text("📚 لا توجد مواد مضافة حالياً. يمكنك طرح سؤالك مباشرة!")
            return

        text = "📚 **المواد الدراسية المتاحة:**\n\n"
        for subj in subjects:
            text += f"• **{subj.name_ar}**\n"
        text += "\nاكتب سؤالك وسأساعدك!"
        await query.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    elif data == "btn_help":
        await query.message.reply_text(format_help_message(), parse_mode=ParseMode.MARKDOWN)


# ── Message Handler ──────────────────────────────────────────


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages with real-time typing and AI RAG processing."""
    if not update.effective_user or not update.message or not update.message.text:
        return

    user = update.effective_user
    question = update.message.text.strip()

    if not question:
        return

    # Handle quick keyboard buttons
    if question in ("📚 المواد المتاحة", "المواد المتاحة", "المواد"):
        await subjects_handler(update, context)
        return
    elif question in ("❓ مساعدة", "مساعدة", "تعليمات"):
        await help_handler(update, context)
        return
    elif question in ("🔄 محادثة جديدة", "محادثة جديدة", "مسح المحادثة"):
        await cancel_handler(update, context)
        return

    logger.info(f"Question from {user.id}: {question[:100]}...")

    # Start background continuous typing indicator
    stop_typing_event = asyncio.Event()
    typing_task = asyncio.create_task(_keep_typing(update.message.chat, stop_typing_event))

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
                    stop_typing_event.set()
                    await typing_task
                    await update.message.reply_text(format_error_message("rate_limit"))
                    return
                logger.warning(f"Rate limit check failed: {rate_err}")

            # Get or create active conversation
            conversation = await _get_or_create_conversation(db, student.id)

            # Load recent conversation history
            conv_history = await _load_conversation_history(db, conversation.id)

            # Save student message
            student_msg = Message(
                conversation_id=conversation.id,
                role="student",
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

            # Stop typing task
            stop_typing_event.set()
            await typing_task

            # Build full response text
            full_response = response.answer
            if response.citations_text:
                full_response += "\n\n" + response.citations_text

            # Save assistant message
            assistant_msg = Message(
                conversation_id=conversation.id,
                role="assistant",
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

            # Send response with interactive inline keyboard
            await update.message.reply_text(
                truncate_message(full_response),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_answer_inline_keyboard(),
            )

        except Exception as e:
            stop_typing_event.set()
            await typing_task
            logger.error(f"Error processing message from {user.id}: {e}")
            try:
                await db.rollback()
            except Exception:
                pass
            await update.message.reply_text(
                format_error_message("general"),
                reply_markup=QUICK_MENU_KEYBOARD,
            )


# ── Helper Functions ─────────────────────────────────────────


async def _get_or_create_student(db: AsyncSession, tg_user) -> Student:
    """Get existing student or create a new one from Telegram user info."""
    result = await db.execute(
        select(Student).where(Student.telegram_user_id == tg_user.id)
    )
    student = result.scalar_one_or_none()

    if student:
        student.username = tg_user.username
        student.first_name = tg_user.first_name or ""
        student.last_name = tg_user.last_name
        student.last_seen_at = datetime.now(timezone.utc)
        return student

    student = Student(
        telegram_user_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name or "",
        last_name=tg_user.last_name,
        preferred_language=tg_user.language_code or "ar",
    )
    db.add(student)
    await db.flush()

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

    return [
        {
            "role": "user" if msg.role in ("student", MessageRole.STUDENT, "STUDENT") else "assistant",
            "content": msg.content,
        }
        for msg in reversed(messages)
    ]
