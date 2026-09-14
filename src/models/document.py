"""Schematy Pydantic dla dokumentów wejściowych i danych ustrukturyzowanych.

Modele w tym module pełnią dwie role:
1. Structured output wymuszany na LLM (JSON Schema) podczas ekstrakcji danych
   z dokumentów (np. faktur).
2. Reprezentacja akcji przekazywanej do warstwy Human-in-the-Loop, oczekującej
   na zatwierdzenie lub odrzucenie przez człowieka.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class DocumentType(str, Enum):
    """Rozpoznany typ dokumentu wejściowego."""

    INVOICE = "invoice"
    EMAIL = "email"
    UNKNOWN = "unknown"


class InvoiceLineItem(BaseModel):
    """Pojedyncza pozycja na fakturze."""

    description: str
    quantity: float = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    total: Decimal = Field(ge=0)


class InvoiceData(BaseModel):
    """Ustrukturyzowane dane wyekstrahowane z faktury (structured output LLM)."""

    invoice_number: str
    vendor_name: str
    issue_date: date
    due_date: date | None = None
    currency: str = Field(min_length=3, max_length=3)
    total_amount: Decimal = Field(ge=0)
    line_items: list[InvoiceLineItem] = Field(default_factory=list)

    @field_validator("currency")
    @classmethod
    def _uppercase_currency(cls, value: str) -> str:
        return value.upper()


class ExtractedDocument(BaseModel):
    """Wynik ekstrakcji: rozpoznany typ dokumentu, dane i pewność modelu."""

    document_type: DocumentType
    confidence: float = Field(ge=0.0, le=1.0)
    invoice: InvoiceData | None = None
    raw_text_excerpt: str | None = Field(default=None, max_length=500)


class ApprovalStatus(str, Enum):
    """Stan akcji w kolejce Human-in-the-Loop."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequest(BaseModel):
    """Akcja zaproponowana przez system, oczekująca na decyzję człowieka."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: DocumentType
    proposed_action: str
    extracted_data: ExtractedDocument
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewer_comment: str | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    decided_at: datetime | None = None
