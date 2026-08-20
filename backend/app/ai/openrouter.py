"""OpenRouter AI provider — access multiple models via one API."""

from __future__ import annotations

import time
from typing import Any

import httpx

from app.ai.base import AIMessage, AIProvider, AIResponse
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterProvider(AIProvider):
    """OpenRouter provider — routes to multiple model providers."""

    name = "openrouter"
    supports_embeddings = False

    def __init__(self):
        self._api_key = settings.openrouter_api_key
        self._model = settings.openrouter_model

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AIResponse:
        """Generate completion via OpenRouter HTTP API."""
        openrouter_messages = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.app_url,
            "X-Title": settings.app_name,
        }

        payload = {
            "model": kwargs.get("model", self._model),
            "messages": openrouter_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        start = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    OPENROUTER_API_URL,
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()

            latency_ms = int((time.monotonic() - start) * 1000)

            choice = data["choices"][0]
            usage = data.get("usage", {})

            return AIResponse(
                content=choice["message"]["content"],
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                model=data.get("model", self._model),
                provider=self.name,
                finish_reason=choice.get("finish_reason", ""),
                latency_ms=latency_ms,
                raw_response=data,
            )
        except httpx.HTTPStatusError as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            logger.error(
                f"OpenRouter HTTP error {e.response.status_code}: {e.response.text}",
                extra={"latency": latency_ms},
            )
            raise
        except Exception as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            logger.error(f"OpenRouter generation failed: {e}", extra={"latency": latency_ms})
            raise
