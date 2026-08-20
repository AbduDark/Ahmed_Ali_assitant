"""Conversation API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import NotFoundError
from app.database import get_async_session
from app.dependencies import CurrentUserId
from app.models.conversation import Conversation, Message
from app.models.student import Student
from app.schemas.conversation import (
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageResponse,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    student_id: str | None = None,
):
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

    return ConversationListResponse(
        conversations=[ConversationResponse.model_validate(c) for c in conversations],
        total=total,
    )


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    user_id: str = Depends(CurrentUserId),
    db: AsyncSession = Depends(get_async_session),
):
    """
    Get conversation detail with all messages.

    Includes retrieved chunks and RAG metadata for debugging.
    """
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise NotFoundError("المحادثة")

    # Load messages
    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = list(msg_result.scalars().all())

    return ConversationDetailResponse(
        id=conversation.id,
        student_id=conversation.student_id,
        title=conversation.title,
        summary=conversation.summary,
        message_count=conversation.message_count,
        messages=[MessageResponse.model_validate(m) for m in messages],
        created_at=conversation.created_at,
    )
