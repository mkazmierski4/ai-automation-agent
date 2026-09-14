"""Klienci LLM realizujący ekstrakcję ustrukturyzowanych danych (Structured Outputs).

Każdy klient implementuje wspólny interfejs `BaseLLMClient`, dzięki czemu
warstwa wyższa (`DocumentParser`) nie zależy od konkretnego dostawcy LLM.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from src.core.config import Settings


class LLMExtractionError(Exception):
    """Klient LLM nie zwrócił poprawnych, ustrukturyzowanych danych."""


class BaseLLMClient(ABC):
    """Wspólny interfejs dla klientów LLM wymuszających structured output."""

    @abstractmethod
    def extract_structured_data(
        self, text: str, schema: type[BaseModel]
    ) -> dict[str, Any]:
        """Zwraca dane wyekstrahowane z `text`, zgodne z JSON Schema `schema`."""
        raise NotImplementedError


class OpenAIClient(BaseLLMClient):
    """Klient OpenAI wykorzystujący natywne Structured Outputs (`response_format`)."""

    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model = model

    def extract_structured_data(
        self, text: str, schema: type[BaseModel]
    ) -> dict[str, Any]:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": "Wyekstrahuj dane z dokumentu zgodnie ze schematem.",
                },
                {"role": "user", "content": text},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "schema": schema.model_json_schema(),
                    "strict": True,
                },
            },
        )
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except (TypeError, json.JSONDecodeError) as exc:
            raise LLMExtractionError(f"OpenAI zwrócił niepoprawny JSON: {exc}") from exc


class AnthropicClient(BaseLLMClient):
    """Klient Anthropic wymuszający JSON Schema przez mechanizm Tool Use."""

    def __init__(self, api_key: str, model: str) -> None:
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def extract_structured_data(
        self, text: str, schema: type[BaseModel]
    ) -> dict[str, Any]:
        tool_name = f"extract_{schema.__name__.lower()}"
        response = self._client.messages.create(
            model=self._model,
            max_tokens=2048,
            tools=[
                {
                    "name": tool_name,
                    "description": f"Zapisz dane wyekstrahowane jako {schema.__name__}.",
                    "input_schema": schema.model_json_schema(),
                }
            ],
            tool_choice={"type": "tool", "name": tool_name},
            messages=[{"role": "user", "content": text}],
        )
        for block in response.content:
            if getattr(block, "type", None) == "tool_use" and block.name == tool_name:
                return block.input
        raise LLMExtractionError("Anthropic nie zwrócił oczekiwanego bloku tool_use.")


def get_llm_client(settings: Settings) -> BaseLLMClient:
    """Fabryka klienta LLM na podstawie `settings.llm_provider`."""
    provider = settings.llm_provider.lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("Brak OPENAI_API_KEY w konfiguracji.")
        return OpenAIClient(api_key=settings.openai_api_key, model=settings.openai_model)

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("Brak ANTHROPIC_API_KEY w konfiguracji.")
        return AnthropicClient(
            api_key=settings.anthropic_api_key, model=settings.anthropic_model
        )

    raise ValueError(f"Nieobsługiwany LLM_PROVIDER: {settings.llm_provider!r}")
