"""Abstract messaging provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class MessagingProvider(ABC):
    """
    Abstract interface for messaging platforms.

    Implement for each platform (Telegram, WhatsApp, etc.)
    to keep core logic platform-agnostic.
    """

    name: str = "base"

    @abstractmethod
    async def send_message(self, user_id: str | int, text: str, **kwargs) -> None:
        """Send a text message to a user."""
        ...

    @abstractmethod
    async def send_typing_action(self, user_id: str | int) -> None:
        """Show typing indicator."""
        ...

    async def send_file(
        self,
        user_id: str | int,
        file_data: bytes,
        filename: str,
        caption: str | None = None,
    ) -> None:
        """Send a file to a user. Optional — not all platforms support this."""
        raise NotImplementedError
