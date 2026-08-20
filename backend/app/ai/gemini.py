"""Google Gemini AI provider."""

from __future__ import annotations

import time
from typing import Any

import google.generativeai as genai

from app.ai.base import AIMessage, AIProvider, AIResponse
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiProvider(AIProvider):
    """Google Gemini provider using the official SDK."""

    name = "gemini"
    supports_embeddings = True

    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(settings.gemini_model)
        self._embedding_model = settings.gemini_embedding_model

    def _convert_messages(self, messages: list[AIMessage]) -> tuple[str | None, list[dict]]:
        """Convert AIMessage list to Gemini format, extracting system instruction."""
        system_instruction = None
        history = []

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            elif msg.role == "user":
                history.append({"role": "user", "parts": [msg.content]})
            elif msg.role == "assistant":
                history.append({"role": "model", "parts": [msg.content]})

        return system_instruction, history

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AIResponse:
        """Generate completion using Gemini."""
        system_instruction, history = self._convert_messages(messages)

        # Create model with system instruction if provided
        model = genai.GenerativeModel(
            settings.gemini_model,
            system_instruction=system_instruction,
        )

        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        start = time.monotonic()
        try:
            # The last message is the current user message
            # Previous messages form the chat history
            if len(history) > 1:
                chat = model.start_chat(history=history[:-1])
                response = await chat.send_message_async(
                    history[-1]["parts"][0],
                    generation_config=generation_config,
                )
            else:
                response = await model.generate_content_async(
                    history[-1]["parts"][0] if history else "",
                    generation_config=generation_config,
                )

            latency_ms = int((time.monotonic() - start) * 1000)

            # Extract token counts
            usage = getattr(response, "usage_metadata", None)
            input_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
            output_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0

            return AIResponse(
                content=response.text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                model=settings.gemini_model,
                provider=self.name,
                finish_reason=str(getattr(response.candidates[0], "finish_reason", ""))
                if response.candidates else "",
                latency_ms=latency_ms,
                raw_response=response,
            )
        except Exception as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            logger.error(f"Gemini generation failed: {e}", extra={"latency": latency_ms})
            raise

    async def embed(self, text: str) -> list[float]:
        """Generate embedding using Gemini text-embedding-004."""
        try:
            result = genai.embed_content(
                model=f"models/{self._embedding_model}",
                content=text,
                task_type="retrieval_document",
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Gemini embedding failed: {e}")
            raise

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Batch embedding with Gemini."""
        try:
            result = genai.embed_content(
                model=f"models/{self._embedding_model}",
                content=texts,
                task_type="retrieval_document",
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Gemini batch embedding failed: {e}")
            raise

    async def embed_query(self, text: str) -> list[float]:
        """Generate embedding optimized for query retrieval."""
        try:
            result = genai.embed_content(
                model=f"models/{self._embedding_model}",
                content=text,
                task_type="retrieval_query",
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Gemini query embedding failed: {e}")
            raise
