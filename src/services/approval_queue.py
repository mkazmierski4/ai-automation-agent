"""Kolejka akcji Human-in-the-Loop: przechowywanie i decyzje (approve/reject).

Storage jest wstrzykiwany przez interfejs `BaseApprovalStorage`, dzięki czemu
domyślną implementację in-memory można później podmienić na SQLite/Postgres
bez zmian w `ApprovalQueueService`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from src.core.config import Settings
from src.models.document import ApprovalRequest, ApprovalStatus, ExtractedDocument


class ApprovalRequestNotFoundError(Exception):
    """Nie znaleziono zadania o podanym `request_id`."""


class InvalidApprovalStateError(Exception):
    """Zadanie nie znajduje się w stanie `PENDING`, więc nie można go zdecydować."""


class BaseApprovalStorage(ABC):
    """Interfejs przechowywania zadań `ApprovalRequest`."""

    @abstractmethod
    def add(self, request: ApprovalRequest) -> None:
        """Zapisuje nowe zadanie."""

    @abstractmethod
    def get(self, request_id: str) -> ApprovalRequest | None:
        """Zwraca zadanie o danym id lub `None`, jeśli nie istnieje."""

    @abstractmethod
    def update(self, request: ApprovalRequest) -> None:
        """Zapisuje zaktualizowany stan istniejącego zadania."""

    @abstractmethod
    def list_all(self) -> list[ApprovalRequest]:
        """Zwraca wszystkie zadania."""


class InMemoryApprovalStorage(BaseApprovalStorage):
    """Domyślna implementacja storage'u trzymana w pamięci procesu."""

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def add(self, request: ApprovalRequest) -> None:
        self._requests[request.id] = request

    def get(self, request_id: str) -> ApprovalRequest | None:
        return self._requests.get(request_id)

    def update(self, request: ApprovalRequest) -> None:
        self._requests[request.id] = request

    def list_all(self) -> list[ApprovalRequest]:
        return list(self._requests.values())


class ApprovalQueueService:
    """Zarządza cyklem życia akcji wymagających zatwierdzenia człowieka."""

    def __init__(self, settings: Settings, storage: BaseApprovalStorage | None = None) -> None:
        self._settings = settings
        self._storage = storage or InMemoryApprovalStorage()

    def process_extraction(self, extraction: ExtractedDocument) -> ApprovalRequest:
        """Tworzy `ApprovalRequest` z ekstrakcji, auto-zatwierdzając wysoki confidence."""
        is_confident = extraction.confidence >= self._settings.hitl_auto_approve_threshold
        request = ApprovalRequest(
            document_type=extraction.document_type,
            proposed_action=self._build_proposed_action(extraction),
            extracted_data=extraction,
            status=ApprovalStatus.AUTO_APPROVED if is_confident else ApprovalStatus.PENDING,
        )
        if is_confident:
            request.decided_at = datetime.now(UTC)
            request.decided_by = "system"
            request.decision_notes = (
                f"Auto-approve: confidence {extraction.confidence:.2f} >= próg "
                f"{self._settings.hitl_auto_approve_threshold:.2f}"
            )
        self._storage.add(request)
        return request

    def list_pending(self) -> list[ApprovalRequest]:
        """Zwraca wyłącznie zadania oczekujące na decyzję człowieka."""
        return [
            r for r in self._storage.list_all() if r.status == ApprovalStatus.PENDING
        ]

    def get_request(self, request_id: str) -> ApprovalRequest | None:
        """Zwraca zadanie o danym id lub `None`."""
        return self._storage.get(request_id)

    def approve(
        self, request_id: str, reviewer: str, notes: str | None = None
    ) -> ApprovalRequest:
        """Zatwierdza zadanie `PENDING`, zapisując metadane audytowe."""
        request = self._require_pending(request_id)
        request.status = ApprovalStatus.APPROVED
        request.decided_by = reviewer
        request.decision_notes = notes
        request.decided_at = datetime.now(UTC)
        self._storage.update(request)
        return request

    def reject(self, request_id: str, reviewer: str, reason: str) -> ApprovalRequest:
        """Odrzuca zadanie `PENDING`, zapisując powód w logu audytowym."""
        request = self._require_pending(request_id)
        request.status = ApprovalStatus.REJECTED
        request.decided_by = reviewer
        request.decision_notes = reason
        request.decided_at = datetime.now(UTC)
        self._storage.update(request)
        return request

    def _require_pending(self, request_id: str) -> ApprovalRequest:
        request = self._storage.get(request_id)
        if request is None:
            raise ApprovalRequestNotFoundError(f"Brak zadania o id={request_id!r}")
        if request.status != ApprovalStatus.PENDING:
            raise InvalidApprovalStateError(
                f"Zadanie {request_id!r} ma status {request.status.value!r}, "
                "oczekiwano 'pending'"
            )
        return request

    @staticmethod
    def _build_proposed_action(extraction: ExtractedDocument) -> str:
        if extraction.invoice is not None:
            return f"Zaksięguj fakturę {extraction.invoice.invoice_number}"
        return f"Przetwórz dokument typu {extraction.document_type.value}"
