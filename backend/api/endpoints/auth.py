"""Echomind Commerce - `/api/auth/*` endpoints (Firebase session validation)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, status

from api.schemas import NotImplementedResponse
from utils.logging_safety import safe_log

logger = logging.getLogger("echomind.api.auth")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/session",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Validate a Firebase ID token, mint a server session",
)
async def validate_session(payload: dict | None = None) -> NotImplementedResponse:
    """Final response: `{uid, email, expires_at}`."""
    logger.info("auth.session payload_keys=%s", safe_log(list((payload or {}).keys())))
    return NotImplementedResponse(
        endpoint="POST /api/auth/session",
        detail="Verifies Firebase ID token via firebase-admin, returns user descriptor.",
    )
