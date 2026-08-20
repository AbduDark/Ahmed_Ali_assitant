"""Telegram bot setup and lifecycle management."""

from __future__ import annotations

from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from app.config import settings
from app.core.logging import get_logger
from app.messaging.base import MessagingProvider
from app.messaging.telegram.handlers import (
    cancel_handler,
    help_handler,
    message_handler,
    start_handler,
    subjects_handler,
)

logger = get_logger(__name__)


class TelegramBot(MessagingProvider):
    """Telegram bot using python-telegram-bot v21."""

    name = "telegram"

    def __init__(self):
        self._app: Application | None = None
        self._bot: Bot | None = None

    @property
    def app(self) -> Application:
        if self._app is None:
            raise RuntimeError("Telegram bot not initialized")
        return self._app

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            raise RuntimeError("Telegram bot not initialized")
        return self._bot

    async def initialize(self) -> None:
        """Initialize the Telegram bot application."""
        if not settings.telegram_bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set — Telegram bot disabled")
            return

        self._app = (
            Application.builder()
            .token(settings.telegram_bot_token)
            .build()
        )
        self._bot = self._app.bot

        # Register handlers
        self._app.add_handler(CommandHandler("start", start_handler))
        self._app.add_handler(CommandHandler("help", help_handler))
        self._app.add_handler(CommandHandler("subjects", subjects_handler))
        self._app.add_handler(CommandHandler("cancel", cancel_handler))

        # Text message handler (must be last)
        self._app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
        )

        # Initialize the application
        await self._app.initialize()

        logger.info("Telegram bot initialized")

    async def start(self) -> None:
        """Start the bot (polling mode for development)."""
        if not self._app:
            return

        if settings.telegram_use_polling:
            logger.info("Starting Telegram bot in polling mode")
            await self._app.start()
            await self._app.updater.start_polling(drop_pending_updates=True)
        else:
            # Webhook mode — set webhook URL
            webhook_url = f"{settings.telegram_webhook_url}/webhooks/telegram/{settings.telegram_webhook_secret}"
            await self._app.start()
            await self._bot.set_webhook(
                url=webhook_url,
                secret_token=settings.telegram_webhook_secret,
            )
            logger.info(f"Telegram webhook set: {webhook_url}")

    async def stop(self) -> None:
        """Stop the bot gracefully."""
        if not self._app:
            return

        if settings.telegram_use_polling and self._app.updater:
            await self._app.updater.stop()

        await self._app.stop()
        await self._app.shutdown()
        logger.info("Telegram bot stopped")

    async def send_message(self, user_id: str | int, text: str, **kwargs) -> None:
        """Send a text message to a Telegram user."""
        if not self._bot:
            return
        await self._bot.send_message(
            chat_id=int(user_id),
            text=text,
            parse_mode=kwargs.get("parse_mode", "Markdown"),
        )

    async def send_typing_action(self, user_id: str | int) -> None:
        """Show typing indicator."""
        if not self._bot:
            return
        await self._bot.send_chat_action(
            chat_id=int(user_id),
            action="typing",
        )


# Global instance
telegram_bot = TelegramBot()
