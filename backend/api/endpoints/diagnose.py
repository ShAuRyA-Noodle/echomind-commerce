"""Echomind Commerce - `/api/diagnose/*` endpoints (gap detection).

Endpoints (per WINNING_PLAN §5.5):
    POST   /api/diagnose/run
    GET    /api/diagnose/{id}
    GET    /api/diagnose/{id}/gap/{gap_id}
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, status

from api.schemas import NotImplementedResponse

logger = logging.getLogger("echomind.api.diagnose")

router = APIRouter(prefix="/diagnose", tags=["diagnose"])


@router.post(
    "/run",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Run the diagnose pipeline (gap detection + ranking)",
)
async def run_diagnose(payload: dict[str, Any] | None = None) -> NotImplementedResponse:
    """Final response: `{diagnose_id}`."""
    logger.info("diagnose.run payload=%s", payload)
    return NotImplementedResponse(
        endpoint="POST /api/diagnose/run",
        detail="Cypher candidate detection -> Pro judge -> revenue model -> calibrator -> ranker.",
    )


@router.get(
    "/{diagnose_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Fetch diagnose result (all gaps + readiness)",
)
async def get_diagnose(diagnose_id: str) -> NotImplementedResponse:
    """Final response: `{gaps: [Gap], readiness_score, calibration_summary}`."""
    logger.info("diagnose.get id=%s", diagnose_id)
    return NotImplementedResponse(
        endpoint=f"GET /api/diagnose/{diagnose_id}",
        detail="Returns the full gap list and the aggregate readiness score.",
    )


@router.get(
    "/{diagnose_id}/gap/{gap_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Drill-down: full reasoning chain for one gap",
)
async def get_gap(diagnose_id: str, gap_id: str) -> NotImplementedResponse:
    """Final response: `{gap, reasoning_chain, source_nodes, fix_candidates}`."""
    logger.info("diagnose.gap id=%s gap=%s", diagnose_id, gap_id)
    return NotImplementedResponse(
        endpoint=f"GET /api/diagnose/{diagnose_id}/gap/{gap_id}",
        detail="Returns gap + reasoning trace + source subgraph + candidate fixes.",
    )
