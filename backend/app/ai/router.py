"""AI provider router — creates and manages provider instances."""

from __future__ import annotations

from app.ai.base import AIProvider
from app.ai.failover import FailoverChain
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Provider registry
_PROVIDER_MAP: dict[str, type] = {}


def _register_providers() -> None:
    """Lazy-register providers to avoid import errors for missing API keys."""
    global _PROVIDER_MAP
    if _PROVIDER_MAP:
        return

    from app.ai.gemini import GeminiProvider
    from app.ai.groq import GroqProvider
    from app.ai.openrouter import OpenRouterProvider
    from app.ai.openai_provider import OpenAIProvider

    _PROVIDER_MAP = {
        "gemini": GeminiProvider,
        "groq": GroqProvider,
        "openrouter": OpenRouterProvider,
        "openai": OpenAIProvider,
    }


def _create_provider(name: str) -> AIProvider | None:
    """Create a provider instance if its API key is configured."""
    _register_providers()

    provider_class = _PROVIDER_MAP.get(name)
    if not provider_class:
        logger.warning(f"Unknown AI provider: {name}")
        return None

    # Check if API key is configured
    key_map = {
        "gemini": settings.gemini_api_key,
        "groq": settings.groq_api_key,
        "openrouter": settings.openrouter_api_key,
        "openai": settings.openai_api_key,
    }

    if not key_map.get(name):
        logger.warning(f"AI provider {name} has no API key configured, skipping")
        return None

    try:
        return provider_class()
    except Exception as e:
        logger.error(f"Failed to initialize AI provider {name}: {e}")
        return None


def create_failover_chain() -> FailoverChain:
    """
    Build the failover chain from settings.

    Order: primary provider → fallback providers (in order).
    """
    providers: list[AIProvider] = []

    # Primary provider
    primary = _create_provider(settings.ai_primary_provider)
    if primary:
        providers.append(primary)
    else:
        logger.warning(f"Primary AI provider '{settings.ai_primary_provider}' unavailable")

    # Fallback providers
    for name in settings.fallback_providers_list:
        provider = _create_provider(name)
        if provider:
            providers.append(provider)

    if not providers:
        raise RuntimeError(
            "No AI providers available. Configure at least one provider API key in .env"
        )

    logger.info(f"AI failover chain: {' → '.join(p.name for p in providers)}")
    return FailoverChain(providers)


def get_embedding_provider() -> AIProvider:
    """Get the provider to use for embeddings (prefers Gemini for cost)."""
    # Try Gemini first (free tier)
    if settings.gemini_api_key:
        provider = _create_provider("gemini")
        if provider and provider.supports_embeddings:
            return provider

    # Then OpenAI
    if settings.openai_api_key:
        provider = _create_provider("openai")
        if provider and provider.supports_embeddings:
            return provider

    raise RuntimeError(
        "No embedding provider available. Configure GEMINI_API_KEY or OPENAI_API_KEY."
    )
