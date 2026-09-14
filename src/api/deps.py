"""Zależności (dependency injection) współdzielone przez routery API."""

from __future__ import annotations

from functools import lru_cache

from src.core.config import get_settings
from src.services.approval_queue import ApprovalQueueService
from src.services.document_parser import DocumentParser
from src.services.llm_client import get_llm_client


@lru_cache
def get_approval_queue_service() -> ApprovalQueueService:
    """Zwraca współdzieloną (singleton) instancję kolejki zatwierdzeń."""
    return ApprovalQueueService(settings=get_settings())


@lru_cache
def get_document_parser() -> DocumentParser:
    """Zwraca współdzieloną (singleton) instancję parsera dokumentów."""
    settings = get_settings()
    return DocumentParser(llm_client=get_llm_client(settings))
