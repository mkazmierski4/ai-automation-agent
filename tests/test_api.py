"""Testy integracyjne REST API (`fastapi.testclient.TestClient`)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from src.api.deps import get_approval_queue_service, get_document_parser
from src.api.main import app
from src.core.config import Settings
from src.models.document import DocumentType, ExtractedDocument
from src.services.approval_queue import ApprovalQueueService


@pytest.fixture
def queue_service() -> ApprovalQueueService:
    settings = Settings(_env_file=None, hitl_auto_approve_threshold=0.9)
    return ApprovalQueueService(settings=settings)


@pytest.fixture
def fake_parser() -> MagicMock:
    return MagicMock()


@pytest.fixture
def client(queue_service: ApprovalQueueService, fake_parser: MagicMock) -> TestClient:
    app.dependency_overrides[get_approval_queue_service] = lambda: queue_service
    app.dependency_overrides[get_document_parser] = lambda: fake_parser
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "environment" in body


def test_process_document_low_confidence_creates_pending(
    client: TestClient, fake_parser: MagicMock
) -> None:
    fake_parser.parse.return_value = ExtractedDocument(
        document_type=DocumentType.EMAIL, confidence=0.5
    )

    response = client.post("/api/v1/documents/process", json={"text": "treść e-maila"})

    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    fake_parser.parse.assert_called_once_with("treść e-maila")


def test_process_document_high_confidence_is_auto_approved(
    client: TestClient, fake_parser: MagicMock
) -> None:
    fake_parser.parse.return_value = ExtractedDocument(
        document_type=DocumentType.EMAIL, confidence=0.99
    )

    response = client.post("/api/v1/documents/process", json={"text": "treść"})

    assert response.status_code == 201
    assert response.json()["status"] == "auto_approved"


def test_process_document_rejects_empty_text(client: TestClient) -> None:
    # Walidacja Pydantic (min_length=1) -> FastAPI zwraca natywnie 422
    response = client.post("/api/v1/documents/process", json={"text": ""})
    assert response.status_code == 422


def test_full_flow_upload_list_and_approve(
    client: TestClient, fake_parser: MagicMock
) -> None:
    fake_parser.parse.return_value = ExtractedDocument(
        document_type=DocumentType.EMAIL, confidence=0.4
    )

    created = client.post("/api/v1/documents/process", json={"text": "treść"}).json()
    request_id = created["id"]

    pending = client.get("/api/v1/approvals/pending").json()
    assert any(item["id"] == request_id for item in pending)

    approve_response = client.post(
        f"/api/v1/approvals/{request_id}/approve",
        json={"reviewer": "alice", "notes": "wygląda dobrze"},
    )

    assert approve_response.status_code == 200
    approved = approve_response.json()
    assert approved["status"] == "approved"
    assert approved["decided_by"] == "alice"

    pending_after = client.get("/api/v1/approvals/pending").json()
    assert all(item["id"] != request_id for item in pending_after)


def test_reject_request_success(client: TestClient, fake_parser: MagicMock) -> None:
    fake_parser.parse.return_value = ExtractedDocument(
        document_type=DocumentType.EMAIL, confidence=0.3
    )
    created = client.post("/api/v1/documents/process", json={"text": "treść"}).json()

    response = client.post(
        f"/api/v1/approvals/{created['id']}/reject",
        json={"reviewer": "bob", "reason": "błędne dane"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_approve_unknown_request_returns_404(client: TestClient) -> None:
    response = client.post(
        "/api/v1/approvals/does-not-exist/approve", json={"reviewer": "alice"}
    )
    assert response.status_code == 404


def test_approve_already_decided_request_returns_409(
    client: TestClient, fake_parser: MagicMock
) -> None:
    fake_parser.parse.return_value = ExtractedDocument(
        document_type=DocumentType.EMAIL, confidence=0.99  # auto-approved od razu
    )
    created = client.post("/api/v1/documents/process", json={"text": "treść"}).json()

    response = client.post(
        f"/api/v1/approvals/{created['id']}/approve", json={"reviewer": "alice"}
    )
    assert response.status_code == 409
