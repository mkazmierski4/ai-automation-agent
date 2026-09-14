"""Parser dokumentów: surowy tekst -> LLM (structured output) -> ExtractedDocument."""

from __future__ import annotations

import logging

from pydantic import ValidationError

from src.models.document import ExtractedDocument
from src.services.llm_client import BaseLLMClient, LLMExtractionError

logger = logging.getLogger(__name__)


class DocumentParsingError(Exception):
    """Ekstrakcja dokumentu nie powiodła się mimo ponowionych prób."""


class DocumentParser:
    """Zamienia surowy tekst dokumentu w zwalidowany `ExtractedDocument`."""

    def __init__(self, llm_client: BaseLLMClient, max_retries: int = 2) -> None:
        self._llm_client = llm_client
        self._max_retries = max_retries

    def parse(self, text: str) -> ExtractedDocument:
        """Ekstrahuje dane z `text`, ponawiając próbę przy niepoprawnej strukturze."""
        last_error: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                raw_data = self._llm_client.extract_structured_data(
                    text, ExtractedDocument
                )
                return ExtractedDocument.model_validate(raw_data)
            except (LLMExtractionError, ValidationError) as exc:
                last_error = exc
                logger.warning(
                    "Próba %d/%d ekstrakcji nieudana: %s", attempt, self._max_retries, exc
                )

        raise DocumentParsingError(
            f"Nie udało się wyekstrahować dokumentu po {self._max_retries} próbach"
        ) from last_error
