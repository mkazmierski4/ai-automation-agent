"""Testy serwisów LLM: fabryka klientów i `DocumentParser` (bez wywołań sieciowych)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.core.config import Settings
from src.models.document import DocumentType, ExtractedDocument
from src.services.document_parser import DocumentParser, DocumentParsingError
from src.services.llm_client import (
    AnthropicClient,
    LLMExtractionError,
    OpenAIClient,
    get_llm_client,
)


def _settings(**overrides) -> Settings:
    base: dict = {
        "llm_provider": "anthropic",
        "openai_api_key": "sk-test",
        "anthropic_api_key": "sk-ant-test",
    }
    base.update(overrides)
    return Settings(_env_file=None, **base)


def test_get_llm_client_returns_openai_client() -> None:
    client = get_llm_client(_settings(llm_provider="openai"))
    assert isinstance(client, OpenAIClient)


def test_get_llm_client_returns_anthropic_client() -> None:
    client = get_llm_client(_settings(llm_provider="anthropic"))
    assert isinstance(client, AnthropicClient)


def test_get_llm_client_missing_api_key_raises() -> None:
    with pytest.raises(ValueError):
        get_llm_client(_settings(llm_provider="openai", openai_api_key=None))


def test_get_llm_client_unsupported_provider_raises() -> None:
    with pytest.raises(ValueError):
        get_llm_client(_settings(llm_provider="mistral"))


def _valid_extracted_payload() -> dict:
    return {
        "document_type": DocumentType.INVOICE.value,
        "confidence": 0.95,
        "invoice": None,
        "raw_text_excerpt": "Faktura nr 1",
    }


def test_document_parser_succeeds_on_first_attempt() -> None:
    mock_client = MagicMock()
    mock_client.extract_structured_data.return_value = _valid_extracted_payload()

    parser = DocumentParser(llm_client=mock_client)
    result = parser.parse("treść dokumentu")

    assert isinstance(result, ExtractedDocument)
    assert result.document_type == DocumentType.INVOICE
    mock_client.extract_structured_data.assert_called_once()


def test_document_parser_retries_on_extraction_error_then_succeeds() -> None:
    mock_client = MagicMock()
    mock_client.extract_structured_data.side_effect = [
        LLMExtractionError("zły JSON"),
        _valid_extracted_payload(),
    ]

    parser = DocumentParser(llm_client=mock_client, max_retries=2)
    result = parser.parse("treść dokumentu")

    assert result.confidence == pytest.approx(0.95)
    assert mock_client.extract_structured_data.call_count == 2


def test_document_parser_retries_on_validation_error_then_succeeds() -> None:
    mock_client = MagicMock()
    mock_client.extract_structured_data.side_effect = [
        {"document_type": "not-a-valid-type", "confidence": 2.0},  # niepoprawne dane
        _valid_extracted_payload(),
    ]

    parser = DocumentParser(llm_client=mock_client, max_retries=2)
    result = parser.parse("treść dokumentu")

    assert result.document_type == DocumentType.INVOICE
    assert mock_client.extract_structured_data.call_count == 2


def test_document_parser_raises_after_exhausting_retries() -> None:
    mock_client = MagicMock()
    mock_client.extract_structured_data.side_effect = LLMExtractionError("zawsze źle")

    parser = DocumentParser(llm_client=mock_client, max_retries=2)

    with pytest.raises(DocumentParsingError):
        parser.parse("treść dokumentu")

    assert mock_client.extract_structured_data.call_count == 2
