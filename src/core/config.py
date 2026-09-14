"""Konfiguracja aplikacji ładowana ze zmiennych środowiskowych (.env)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralne ustawienia aplikacji.

    Wartości są wczytywane z pliku `.env` (patrz `.env.example`), z możliwością
    nadpisania przez rzeczywiste zmienne środowiskowe systemu.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_env: str = "development"
    log_level: str = "INFO"

    llm_provider: str = "anthropic"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"

    hitl_approval_timeout_seconds: int = 3600


@lru_cache
def get_settings() -> Settings:
    """Zwraca współdzieloną, cache'owaną instancję ustawień aplikacji."""
    return Settings()
