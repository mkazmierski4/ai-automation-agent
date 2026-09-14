"""Schematy request/response warstwy API (DTO), oddzielone od modeli domenowych."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentProcessRequest(BaseModel):
    """Surowy tekst dokumentu przekazywany do ekstrakcji."""

    text: str = Field(min_length=1)


class ApprovalDecisionRequest(BaseModel):
    """Dane zatwierdzenia wniosku przez recenzenta."""

    reviewer: str = Field(min_length=1)
    notes: str | None = None


class RejectionRequest(BaseModel):
    """Dane odrzucenia wniosku przez recenzenta."""

    reviewer: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class HealthResponse(BaseModel):
    """Odpowiedź healthcheck."""

    status: str
    environment: str
