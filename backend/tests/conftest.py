"""Pytest fixtures and test setup."""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient

from app.ai.base import AIMessage, AIProvider, AIResponse
from app.config import settings
from app.main import app


class MockAIProvider(AIProvider):
    """Mock AI Provider for deterministic testing."""

    name = "mock_ai"
    supports_embeddings = True

    async def generate(
        self,
        messages: list[AIMessage],
        *,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AIResponse:
        last_msg = messages[-1].content if messages else ""
        return AIResponse(
            content=f"إجابة اختبارية مبنية على المراجع: {last_msg[:50]}",
            input_tokens=25,
            output_tokens=30,
            total_tokens=55,
            model="mock-model",
            provider="mock_ai",
            latency_ms=120,
        )

    async def embed(self, text: str) -> list[float]:
        # Return 768-dim mock vector
        return [0.1] * 768

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 768 for _ in texts]


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_ai_provider() -> MockAIProvider:
    return MockAIProvider()


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async test client for FastAPI routes."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
