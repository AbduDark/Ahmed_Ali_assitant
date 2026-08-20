"""Background tasks for conversation management and summarization."""

from __future__ import annotations

from sqlalchemy import select
from app.core.logging import get_logger

logger = get_logger(__name__)


async def summarize_conversation(ctx: dict, conversation_id: str) -> None:
    """
    Background job: generate a summary of a conversation using AI
    when message count exceeds a threshold.
    """
    from app.ai.router import create_failover_chain
    from app.models.conversation import Conversation, Message
    from app.rag.prompt_builder import PromptBuilder

    db_factory = ctx["db_factory"]
    async with db_factory() as db:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found for summarization")
            return

        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
        )
        messages = list(msg_result.scalars().all())
        if len(messages) < 4:
            return  # Not enough messages to summarize

        formatted_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]

        prompt_builder = PromptBuilder()
        ai_messages = prompt_builder.build_summary_prompt(formatted_messages)

        try:
            chain = create_failover_chain()
            response = await chain.generate(ai_messages, temperature=0.2, max_tokens=500)
            conversation.summary = response.content.strip()
            await db.commit()
            logger.info(f"Summarized conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Failed to summarize conversation {conversation_id}: {e}")
