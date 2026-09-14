"""Endpoint healthcheck."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.core.config import Settings, get_settings
from src.models.api import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Zwraca status aplikacji oraz aktywne środowisko."""
    return HealthResponse(status="ok", environment=settings.app_env)
