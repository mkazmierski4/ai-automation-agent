"""Punkt wejścia aplikacji FastAPI."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1 import approvals, documents, health
from src.services.approval_queue import (
    ApprovalRequestNotFoundError,
    InvalidApprovalStateError,
)

app = FastAPI(
    title="Human-in-the-Loop AI Document & Task Processor",
    description=(
        "Automatyzacja przetwarzania dokumentów (PDF/e-mail) z ekstrakcją danych "
        "przez LLM (structured outputs) i obowiązkowym zatwierdzeniem akcji przez "
        "człowieka przed wykonaniem."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ApprovalRequestNotFoundError)
def _handle_not_found(_: Request, exc: ApprovalRequestNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidApprovalStateError)
def _handle_invalid_state(_: Request, exc: InvalidApprovalStateError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


app.include_router(health.router)
app.include_router(documents.router)
app.include_router(approvals.router)
