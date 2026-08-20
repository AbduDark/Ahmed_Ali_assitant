"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration — all values come from .env or environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ─────────────────────────────────────────
    app_env: str = "development"
    app_name: str = "AI Teacher Assistant"
    app_url: str = "http://localhost:8000"
    app_debug: bool = False
    app_log_level: str = "INFO"

    # ── Database ────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://teacher_ai:teacher_ai_pass@postgres:5432/teacher_ai_db"

    # ── Redis ───────────────────────────────────────────────
    redis_url: str = "redis://redis:6379/0"

    # ── JWT ─────────────────────────────────────────────────
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7

    # ── Telegram ────────────────────────────────────────────
    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""
    telegram_webhook_secret: str = "change-me"
    telegram_use_polling: bool = True

    # ── AI Providers ────────────────────────────────────────
    ai_primary_provider: str = "gemini"
    ai_fallback_providers: str = "groq,openrouter"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_embedding_model: str = "text-embedding-004"

    # Groq
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemini-2.0-flash-exp:free"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # ── RAG ─────────────────────────────────────────────────
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.70
    rag_chunk_size: int = 600
    rag_chunk_overlap: int = 75

    # ── Rate Limiting ───────────────────────────────────────
    rate_limit_student_per_minute: int = 10
    rate_limit_global_per_minute: int = 100

    # ── File Upload ─────────────────────────────────────────
    max_file_size_mb: int = 100
    upload_dir: str = "./uploads"

    # ── CORS ────────────────────────────────────────────────
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # ── Computed Properties ─────────────────────────────────

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def fallback_providers_list(self) -> list[str]:
        return [p.strip() for p in self.ai_fallback_providers.split(",") if p.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @field_validator("app_log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid}")
        return upper


# Singleton
settings = Settings()
