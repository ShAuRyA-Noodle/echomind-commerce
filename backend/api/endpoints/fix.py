"""Echomind Commerce - `/api/fix/*` endpoints (fix gen + apply + retest).

Endpoints (per WINNING_PLAN §5.5):
    POST   /api/fix/generate/{gap_id}
    POST   /api/fix/apply/{fix_id}
    POST   /api/fix/retest/{fix_id}
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, status

from api.schemas import NotImplementedResponse

logger = logging.getLogger("echomind.api.fix")

router = APIRouter(prefix="/fix", tags=["fix"])


@router.post(
    "/generate/{gap_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Generate a fix candidate for a given gap",
)
async def generate_fix(gap_id: str) -> NotImplementedResponse:
    """Final response: `{fix_id, proposed_text, predicted_delta_range}`."""
    logger.info("fix.generate gap_id=%s", gap_id)
    return NotImplementedResponse(
        endpoint=f"POST /api/fix/generate/{gap_id}",
        detail="Pulls gap + subgraph, calls fix copy generator, persists FixSuggestion.",
    )


@router.post(
    "/apply/{fix_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Apply a fix to Shopify (real Admin API mutation)",
)
async def apply_fix(fix_id: str) -> NotImplementedResponse:
    """Final response: `{applied, shopify_resource_id}`."""
    logger.info("fix.apply fix_id=%s", fix_id)
    return NotImplementedResponse(
        endpoint=f"POST /api/fix/apply/{fix_id}",
        detail="Calls ShopifyService writer, sets FixSuggestion.applied=True with timestamp.",
    )


@router.post(
    "/retest/{fix_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Re-run scoped agent simulation against the applied fix",
)
async def retest_fix(fix_id: str) -> NotImplementedResponse:
    """Final response: `{retest_run_id, delta}`."""
    logger.info("fix.retest fix_id=%s", fix_id)
    return NotImplementedResponse(
        endpoint=f"POST /api/fix/retest/{fix_id}",
        detail="Re-runs only the prompts that touched the affected entity, returns observed delta.",
    )
