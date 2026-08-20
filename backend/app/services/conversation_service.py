"""Conversation management service."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import NotFoundError
from app.models.conversation import Conversation, Message


class ConversationService:
    """Business logic for conversation history and messages."""

    @staticmethod
    async def list_conversations(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        student_id: str | None = None,
    ) -> tuple[list[Conversation], int]:
        """List conversations with optional student filter."""
        query = select(Conversation)
        count_query = select(func.count(Conversation.id))

        if student_id:
            query = query.where(Conversation.student_id == student_id)
            count_query = count_query.where(Conversation.student_id == student_id)

        query = query.order_by(Conversation.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        conversations = list(result.scalars().all())
        total = await db.scalar(count_query) or 0

        return conversations, total

    @staticmethod
    async def get_conversation_with_messages(
        conversation_id: str,
        db: AsyncSession,
    ) -> tuple[Conversation, list[Message]]:
        """Get conversation and all its messages."""
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise NotFoundError("المحادثة")

        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = list(msg_result.scalars().all())

        return conversation, messages
