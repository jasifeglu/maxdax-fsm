"""Application configuration for production deployments."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = "maxdax-fsm"
    environment: str = Field(default="production")
    debug: bool = Field(default=False)

    cache_ttl_seconds: int = Field(default=60, ge=1, le=3600)
    cache_max_entries: int = Field(default=1024, ge=32, le=100_000)

    rate_limit_per_minute: int = Field(default=120, ge=10, le=10_000)
    allowed_origins: list[str] = Field(default_factory=lambda: ["https://example.com"])

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Memoize settings to avoid repeated environment parsing."""

    return Settings()
