"""Testy konfiguracji aplikacji z `src.core.config`."""

from __future__ import annotations

from src.core.config import Settings, get_settings


def test_settings_default_values(monkeypatch) -> None:
    # Izolacja od realnego .env / zmiennych środowiskowych systemu
    for var in (
        "APP_ENV",
        "LOG_LEVEL",
        "LLM_PROVIDER",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ):
        monkeypatch.delenv(var, raising=False)

    settings = Settings(_env_file=None)

    assert settings.app_env == "development"
    assert settings.llm_provider == "anthropic"
    assert settings.openai_api_key is None
    assert settings.hitl_approval_timeout_seconds == 3600


def test_settings_reads_environment_override(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-123")

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "openai"
    assert settings.openai_api_key == "sk-test-123"


def test_get_settings_returns_cached_singleton() -> None:
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()

    assert first is second
