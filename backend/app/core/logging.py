"""Structured JSON logging configuration."""

from __future__ import annotations

import logging
import sys
from typing import Any

from app.config import settings


class JSONFormatter(logging.Formatter):
    """Outputs log records as JSON lines for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime, timezone

        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        for key in ("request_id", "user_id", "telegram_user_id", "endpoint",
                     "provider", "model", "latency", "status_code"):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        if record.exc_info and record.exc_info[1]:
            log_data["exception"] = {
                "type": type(record.exc_info[1]).__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging() -> None:
    """Configure application logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.app_log_level))

    # Clear existing handlers
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if settings.is_production:
        handler.setFormatter(JSONFormatter())
    else:
        # Human-readable format for development
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))

    root_logger.addHandler(handler)

    # Reduce noise from third-party libraries
    for logger_name in ("uvicorn.access", "sqlalchemy.engine", "httpx", "httpcore"):
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
