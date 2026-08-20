"""
Multi-platform message router.
Routes outgoing and incoming messages to the appropriate platform provider.
"""

from __future__ import annotations

from typing import Any
from app.core.logging import get_logger
from app.messaging.base import MessagingProvider
from app.messaging.telegram.bot import telegram_bot

logger = get_logger(__name__)


class MessageRouter:
    """
    Central dispatcher for multi-channel messaging (Telegram, WhatsApp, etc.).
    Keeps core business logic decoupled from transport protocols.
    """

    def __init__(self):
        self._providers: dict[str, MessagingProvider] = {}
        # Register default Telegram provider
        self.register_provider("telegram", telegram_bot)

    def register_provider(self, name: str, provider: MessagingProvider) -> None:
        """Register a messaging provider adapter."""
        self._providers[name.lower()] = provider
        logger.info(f"Registered messaging provider: {name}")

    def get_provider(self, name: str) -> MessagingProvider:
        """Get registered provider by name."""
        provider = self._providers.get(name.lower())
        if not provider:
            raise ValueError(f"Messaging provider '{name}' is not registered.")
        return provider

    async def send_message(
        self,
        platform: str,
        user_id: str | int,
        text: str,
        **kwargs: Any,
    ) -> None:
        """Send message across the requested platform."""
        provider = self.get_provider(platform)
        await provider.send_message(user_id=user_id, text=text, **kwargs)

    async def send_typing_action(self, platform: str, user_id: str | int) -> None:
        """Send typing status indicator across the requested platform."""
        provider = self.get_provider(platform)
        await provider.send_typing_action(user_id=user_id)


# Global singleton router
message_router = MessageRouter()
