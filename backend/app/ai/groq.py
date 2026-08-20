"""Groq AI provider."""

from __future__ import annotations

import time
from typing import Any

from groq import AsyncGroq

from app.ai.base import AIMessage, AIProvider, AIResponse
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GroqProvider(AIProvider):
    """Groq provider — fast inference for open-source models."""

    name = "groq"
    supports_embeddings = False

    def __init__(self):
        self._client = AsyncGroq(api_key=settings.groq_api_key)

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AIResponse:
        """Generate completion using Groq."""
        groq_messages = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

        start = time.monotonic()
        try:
            response = await self._client.chat.completions.create(
                model=settings.groq_model,
                messages=groq_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            latency_ms = int((time.monotonic() - start) * 1000)

            choice = response.choices[0]
            usage = response.usage

            return AIResponse(
                content=choice.message.content or "",
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
                model=response.model or settings.groq_model,
                provider=self.name,
                finish_reason=choice.finish_reason or "",
                latency_ms=latency_ms,
                raw_response=response,
            )
        except Exception as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            logger.error(f"Groq generation failed: {e}", extra={"latency": latency_ms})
            raise
