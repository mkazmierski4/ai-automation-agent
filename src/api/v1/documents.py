"""Endpoint przetwarzania dokumentów: tekst -> ekstrakcja LLM -> kolejka HITL."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.deps import get_approval_queue_service, get_document_parser
from src.models.api import DocumentProcessRequest
from src.models.document import ApprovalRequest
from src.services.approval_queue import ApprovalQueueService
from src.services.document_parser import DocumentParser

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/process", response_model=ApprovalRequest, status_code=201)
def process_document(
    payload: DocumentProcessRequest,
    parser: DocumentParser = Depends(get_document_parser),
    queue: ApprovalQueueService = Depends(get_approval_queue_service),
) -> ApprovalRequest:
    """Ekstrahuje dane z tekstu dokumentu i tworzy wpis w kolejce HITL."""
    extraction = parser.parse(payload.text)
    return queue.process_extraction(extraction)
