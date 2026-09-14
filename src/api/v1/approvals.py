"""Endpointy kolejki zatwierdzeń Human-in-the-Loop."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.deps import get_approval_queue_service
from src.models.api import ApprovalDecisionRequest, RejectionRequest
from src.models.document import ApprovalRequest
from src.services.approval_queue import ApprovalQueueService

router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])


@router.get("/pending", response_model=list[ApprovalRequest])
def list_pending(
    queue: ApprovalQueueService = Depends(get_approval_queue_service),
) -> list[ApprovalRequest]:
    """Zwraca listę wniosków oczekujących na decyzję człowieka."""
    return queue.list_pending()


@router.post("/{request_id}/approve", response_model=ApprovalRequest)
def approve_request(
    request_id: str,
    payload: ApprovalDecisionRequest,
    queue: ApprovalQueueService = Depends(get_approval_queue_service),
) -> ApprovalRequest:
    """Zatwierdza wniosek będący w statusie PENDING."""
    return queue.approve(request_id, reviewer=payload.reviewer, notes=payload.notes)


@router.post("/{request_id}/reject", response_model=ApprovalRequest)
def reject_request(
    request_id: str,
    payload: RejectionRequest,
    queue: ApprovalQueueService = Depends(get_approval_queue_service),
) -> ApprovalRequest:
    """Odrzuca wniosek będący w statusie PENDING."""
    return queue.reject(request_id, reviewer=payload.reviewer, reason=payload.reason)
