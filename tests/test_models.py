"""Testy schematów Pydantic z `src.models.document`."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models.document import (
    ApprovalRequest,
    ApprovalStatus,
    DocumentType,
    ExtractedDocument,
    InvoiceData,
    InvoiceLineItem,
)


def _sample_invoice() -> InvoiceData:
    return InvoiceData(
        invoice_number="FV/2025/09/001",
        vendor_name="Acme Sp. z o.o.",
        issue_date=date(2025, 9, 1),
        due_date=date(2025, 9, 15),
        currency="pln",
        total_amount=Decimal("123.45"),
        line_items=[
            InvoiceLineItem(
                description="Usługa konsultingowa",
                quantity=1,
                unit_price=Decimal("123.45"),
                total=Decimal("123.45"),
            )
        ],
    )


def test_invoice_data_valid() -> None:
    invoice = _sample_invoice()
    assert invoice.currency == "PLN"  # normalizacja wielkości liter
    assert invoice.total_amount == Decimal("123.45")
    assert len(invoice.line_items) == 1


def test_invoice_data_rejects_missing_required_field() -> None:
    with pytest.raises(ValidationError):
        InvoiceData(
            vendor_name="Acme Sp. z o.o.",
            issue_date=date(2025, 9, 1),
            currency="PLN",
            total_amount=Decimal("100.00"),
        )  # brak invoice_number


def test_invoice_data_rejects_invalid_currency_length() -> None:
    with pytest.raises(ValidationError):
        InvoiceData(
            invoice_number="FV/1",
            vendor_name="Acme",
            issue_date=date(2025, 9, 1),
            currency="ZLOTY",
            total_amount=Decimal("1.00"),
        )


def test_invoice_line_item_rejects_non_positive_quantity() -> None:
    with pytest.raises(ValidationError):
        InvoiceLineItem(
            description="Coś",
            quantity=0,
            unit_price=Decimal("10.00"),
            total=Decimal("0.00"),
        )


def test_extracted_document_confidence_bounds() -> None:
    with pytest.raises(ValidationError):
        ExtractedDocument(document_type=DocumentType.INVOICE, confidence=1.5)

    doc = ExtractedDocument(
        document_type=DocumentType.INVOICE,
        confidence=0.92,
        invoice=_sample_invoice(),
    )
    assert doc.invoice is not None
    assert doc.confidence == pytest.approx(0.92)


def test_approval_request_defaults() -> None:
    extracted = ExtractedDocument(
        document_type=DocumentType.INVOICE,
        confidence=0.9,
        invoice=_sample_invoice(),
    )
    request = ApprovalRequest(
        document_type=DocumentType.INVOICE,
        proposed_action="Zaksięguj fakturę FV/2025/09/001",
        extracted_data=extracted,
    )

    assert request.status == ApprovalStatus.PENDING
    assert request.decided_at is None

    # id jest generowane automatycznie i jest unikalne dla każdej instancji
    other_request = ApprovalRequest(
        document_type=DocumentType.INVOICE,
        proposed_action="Zaksięguj fakturę FV/2025/09/001",
        extracted_data=extracted,
    )
    assert request.id != other_request.id
