"""Testy kolejki Human-in-the-Loop (`ApprovalQueueService`)."""

from __future__ import annotations

import pytest

from src.core.config import Settings
from src.models.document import ApprovalStatus, DocumentType, ExtractedDocument
from src.services.approval_queue import (
    ApprovalQueueService,
    ApprovalRequestNotFoundError,
    InvalidApprovalStateError,
)


def _settings(threshold: float = 0.9) -> Settings:
    return Settings(_env_file=None, hitl_auto_approve_threshold=threshold)


def _extraction(confidence: float) -> ExtractedDocument:
    return ExtractedDocument(document_type=DocumentType.EMAIL, confidence=confidence)


def test_high_confidence_extraction_is_auto_approved() -> None:
    queue = ApprovalQueueService(settings=_settings(threshold=0.9))

    request = queue.process_extraction(_extraction(0.95))

    assert request.status == ApprovalStatus.AUTO_APPROVED
    assert request.decided_by == "system"
    assert request.decided_at is not None
    assert queue.list_pending() == []


def test_low_confidence_extraction_stays_pending() -> None:
    queue = ApprovalQueueService(settings=_settings(threshold=0.9))

    request = queue.process_extraction(_extraction(0.5))

    assert request.status == ApprovalStatus.PENDING
    assert request.decided_at is None
    assert queue.list_pending() == [request]


def test_get_request_returns_none_for_unknown_id() -> None:
    queue = ApprovalQueueService(settings=_settings())
    assert queue.get_request("does-not-exist") is None


def test_approve_pending_request_records_audit_trail() -> None:
    queue = ApprovalQueueService(settings=_settings(threshold=0.9))
    request = queue.process_extraction(_extraction(0.5))

    approved = queue.approve(request.id, reviewer="alice", notes="wygląda dobrze")

    assert approved.status == ApprovalStatus.APPROVED
    assert approved.decided_by == "alice"
    assert approved.decision_notes == "wygląda dobrze"
    assert approved.decided_at is not None
    assert queue.list_pending() == []


def test_reject_pending_request_records_reason() -> None:
    queue = ApprovalQueueService(settings=_settings(threshold=0.9))
    request = queue.process_extraction(_extraction(0.5))

    rejected = queue.reject(request.id, reviewer="bob", reason="błędna kwota")

    assert rejected.status == ApprovalStatus.REJECTED
    assert rejected.decided_by == "bob"
    assert rejected.decision_notes == "błędna kwota"


def test_approve_unknown_request_raises_not_found() -> None:
    queue = ApprovalQueueService(settings=_settings())
    with pytest.raises(ApprovalRequestNotFoundError):
        queue.approve("does-not-exist", reviewer="alice")


def test_approve_already_decided_request_raises_invalid_state() -> None:
    queue = ApprovalQueueService(settings=_settings(threshold=0.9))
    request = queue.process_extraction(_extraction(0.5))
    queue.approve(request.id, reviewer="alice")

    with pytest.raises(InvalidApprovalStateError):
        queue.approve(request.id, reviewer="bob")


def test_reject_already_auto_approved_request_raises_invalid_state() -> None:
    queue = ApprovalQueueService(settings=_settings(threshold=0.9))
    request = queue.process_extraction(_extraction(0.95))

    with pytest.raises(InvalidApprovalStateError):
        queue.reject(request.id, reviewer="bob", reason="zbyt ryzykowne")
