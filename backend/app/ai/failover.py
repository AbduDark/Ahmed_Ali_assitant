"""AI provider failover chain — automatic fallback on errors."""

from __future__ import annotations

import httpx

from app.ai.base import AIMessage, AIProvider, AIResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

# Errors that trigger failover
RETRIABLE_EXCEPTIONS = (
    httpx.HTTPStatusError,
    TimeoutError,
    ConnectionError,
    RuntimeError,
)


class FailoverChain:
    """
    Tries AI providers in order, falling through to the next on failure.

    Example:
        chain = FailoverChain([gemini, groq, openrouter])
        response = await chain.generate(messages)
    """

    def __init__(self, providers: list[AIProvider]):
        if not providers:
            raise ValueError("At least one AI provider is required")
        self.providers = providers

    async def generate(
        self,
        messages: list[AIMessage],
        **kwargs,
    ) -> AIResponse:
        """Try each provider in order until one succeeds."""
        last_error: Exception | None = None

        for provider in self.providers:
            try:
                logger.info(f"Trying AI provider: {provider.name}")
                response = await provider.generate(messages, **kwargs)
                logger.info(
                    f"AI provider {provider.name} succeeded "
                    f"(tokens={response.total_tokens}, latency={response.latency_ms}ms)"
                )
                return response

            except RETRIABLE_EXCEPTIONS as e:
                last_error = e
                logger.warning(
                    f"AI provider {provider.name} failed, trying next: {type(e).__name__}: {e}"
                )
                continue

            except Exception as e:
                # Non-retriable error — still try next provider but log as error
                last_error = e
                logger.error(
                    f"AI provider {provider.name} unexpected error: {type(e).__name__}: {e}"
                )
                continue

        # All providers failed
        from app.core import AIProviderError
        error_msg = f"All {len(self.providers)} AI providers failed"
        if last_error:
            error_msg += f". Last error: {type(last_error).__name__}: {last_error}"
        logger.error(error_msg)
        raise AIProviderError(error_msg)

    def get_embedding_provider(self) -> AIProvider | None:
        """Return the first provider that supports embeddings."""
        for provider in self.providers:
            if provider.supports_embeddings:
                return provider
        return None
