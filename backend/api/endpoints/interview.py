"""Echomind Commerce - `/api/interview/*` endpoints + WS handler.

Endpoints (per WINNING_PLAN §5.5):
    POST   /api/interview/start
    WS     /api/interview/ws/{session_id}     (mounted on the FastAPI app, not this router)
    POST   /api/interview/{id}/end
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, status

from api.schemas import NotImplementedResponse

logger = logging.getLogger("echomind.api.interview")

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post(
    "/start",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Start a Socratic interview session",
)
async def start_interview(payload: dict[str, Any] | None = None) -> NotImplementedResponse:
    """Final response: `{session_id, ws_url}`."""
    logger.info("interview.start payload=%s", payload)
    return NotImplementedResponse(
        endpoint="POST /api/interview/start",
        detail="Creates a session row, returns ws_url=/api/interview/ws/{session_id}.",
    )


@router.post(
    "/{session_id}/end",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Finalize an interview session and emit summary",
)
async def end_interview(session_id: str) -> NotImplementedResponse:
    """Final response: `{summary, node_count, edge_count}`."""
    logger.info("interview.end session_id=%s", session_id)
    return NotImplementedResponse(
        endpoint=f"POST /api/interview/{session_id}/end",
        detail="Closes the session, runs final extraction pass, returns counts.",
    )
