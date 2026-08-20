"""Embedding generation service."""

from __future__ import annotations

from app.ai.base import AIProvider
from app.core.logging import get_logger

logger = get_logger(__name__)

# Batch size for embedding requests
EMBED_BATCH_SIZE = 50


class EmbeddingService:
    """Generate embeddings using the configured AI provider."""

    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        if not self.provider or not text or not text.strip():
            return [0.0] * 768  # Zero vector for empty text or no provider

        try:
            return await self.provider.embed(text)
        except Exception as e:
            logger.warning(f"Embedding failed: {e}")
            return [0.0] * 768

    async def embed_query(self, text: str) -> list[float]:
        """Generate embedding optimized for query retrieval."""
        if not self.provider or not text or not text.strip():
            return [0.0] * 768

        try:
            # Use query-specific embedding if available (Gemini supports this)
            if hasattr(self.provider, "embed_query"):
                return await self.provider.embed_query(text)
            return await self.provider.embed(text)
        except Exception as e:
            logger.warning(f"Query embedding failed: {e}")
            return [0.0] * 768

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts with batching.

        Handles rate limiting by processing in batches.
        """
        if not texts:
            return []

        all_embeddings: list[list[float]] = []

        # Process in batches
        for i in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[i : i + EMBED_BATCH_SIZE]

            # Filter empty texts
            valid_batch = [t if t.strip() else "." for t in batch]

            try:
                batch_embeddings = await self.provider.embed_batch(valid_batch)
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.warning(f"Batch embedding failed, falling back to sequential: {e}")
                # Fallback: embed one by one
                for text in valid_batch:
                    try:
                        emb = await self.provider.embed(text)
                        all_embeddings.append(emb)
                    except Exception as inner_e:
                        logger.error(f"Single embedding failed: {inner_e}")
                        all_embeddings.append([0.0] * 768)

            logger.info(
                f"Embedded batch {i // EMBED_BATCH_SIZE + 1}/"
                f"{(len(texts) + EMBED_BATCH_SIZE - 1) // EMBED_BATCH_SIZE}"
            )

        return all_embeddings
