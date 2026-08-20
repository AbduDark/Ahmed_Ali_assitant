"""Abstract base class for AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIMessage:
    """A single message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class AIResponse:
    """Response from an AI provider."""
    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    model: str = ""
    provider: str = ""
    finish_reason: str = ""
    latency_ms: int = 0
    raw_response: Any = None


@dataclass
class EmbeddingResponse:
    """Response from an embedding request."""
    embeddings: list[list[float]] = field(default_factory=list)
    model: str = ""
    provider: str = ""
    total_tokens: int = 0


class AIProvider(ABC):
    """
    Abstract base for all AI providers.

    Every provider must implement generate() and optionally embed().
    """

    name: str = "base"
    supports_embeddings: bool = False

    @abstractmethod
    async def generate(
        self,
        messages: list[AIMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> AIResponse:
        """Generate a text completion from a list of messages."""
        ...

    async def embed(self, text: str) -> list[float]:
        """Generate an embedding for a single text. Override if supported."""
        raise NotImplementedError(f"{self.name} does not support embeddings")

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts. Default: sequential calls."""
        results = []
        for text in texts:
            emb = await self.embed(text)
            results.append(emb)
        return results

    async def health_check(self) -> bool:
        """Check if the provider is reachable. Override for custom checks."""
        return True
