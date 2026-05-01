"""Echomind Commerce - `/api/audit/*` endpoints (dashboard data).

Endpoints (per WINNING_PLAN §5.5):
    GET    /api/audit/{store_id}
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, status

from api.schemas import NotImplementedResponse

logger = logging.getLogger("echomind.api.audit")

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get(
    "/{store_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Audit dashboard payload for a store",
)
async def get_audit(store_id: str) -> NotImplementedResponse:
    """Final response: `{readiness_score, gap_count, fix_count, last_audit_at}`."""
    logger.info("audit.get store_id=%s", store_id)
    return NotImplementedResponse(
        endpoint=f"GET /api/audit/{store_id}",
        detail="Aggregates the latest diagnose run for the store.",
    )
