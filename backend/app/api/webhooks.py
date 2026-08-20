"""Telegram webhook endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/telegram")
@router.post("/telegram/{secret}")
async def telegram_webhook(
    request: Request,
    secret: str | None = None,
) -> Response:
    """
    Receive Telegram webhook updates.

    Verifies secret via URL path or X-Telegram-Bot-Api-Secret-Token header.
    """
    header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    expected_secret = settings.telegram_webhook_secret

    # Verify secret from either path or header
    is_valid = (
        (secret and secret == expected_secret)
        or (header_secret and header_secret == expected_secret)
        or not expected_secret  # If no secret configured (dev only)
    )

    if not is_valid:
        logger.warning("Telegram webhook: unauthorized secret verification failed")
        return Response(status_code=403)

    try:
        from telegram import Update
        from app.messaging.telegram.bot import telegram_bot

        if not telegram_bot._app:
            logger.warning("Telegram bot not initialized")
            return Response(status_code=503)

        data = await request.json()
        update = Update.de_json(data=data, bot=telegram_bot.bot)

        if update:
            await telegram_bot.app.process_update(update)

        return Response(status_code=200)

    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return Response(status_code=200)  # Always return 200 to Telegram so it doesn't retry endlessly
