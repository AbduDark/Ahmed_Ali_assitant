"""OpenAI-compatible AI provider."""

from __future__ import annotations

import time
from typing import Any

from openai import AsyncOpenAI

from app.ai.base import AIMessage, AIProvider, AIResponse
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI provider using the official async SDK."""

    name = "openai"
    supports_embeddings = True

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AIResponse:
        """Generate completion using OpenAI."""
        openai_messages = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

        start = time.monotonic()
        try:
            response = await self._client.chat.completions.create(
                model=settings.openai_model,
                messages=openai_messages,
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
                model=response.model or settings.openai_model,
                provider=self.name,
                finish_reason=choice.finish_reason or "",
                latency_ms=latency_ms,
                raw_response=response,
            )
        except Exception as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            logger.error(f"OpenAI generation failed: {e}", extra={"latency": latency_ms})
            raise

    async def embed(self, text: str) -> list[float]:
        """Generate embedding using OpenAI."""
        try:
            response = await self._client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise
