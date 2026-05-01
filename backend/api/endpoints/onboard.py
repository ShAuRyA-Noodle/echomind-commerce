"""Echomind Commerce - `/api/onboard/*` endpoints.

Real route handlers wired to FastAPI. Until the Shopify OAuth flow and the
catalog ingest pipeline land, every handler returns a structured
`NotImplementedResponse` with HTTP 501 so the frontend can develop against
real shapes today.

Endpoints (per WINNING_PLAN §5.5):
    POST   /api/onboard/shopify-oauth-start
    GET    /api/onboard/shopify-oauth-callback
    GET    /api/onboard/ingest/{job_id}
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, status

from api.schemas import NotImplementedResponse

logger = logging.getLogger("echomind.api.onboard")

router = APIRouter(prefix="/onboard", tags=["onboard"])


@router.post(
    "/shopify-oauth-start",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Begin Shopify OAuth - returns redirect URL",
)
async def shopify_oauth_start(payload: dict[str, Any] | None = None) -> NotImplementedResponse:
    """Kick off Shopify OAuth.

    Final shape (per spec): `{redirect_url}`. Implementation lands with
    `services/shopify_service.py.start_oauth()`.
    """
    logger.info("onboard.shopify_oauth_start payload=%s", payload)
    return NotImplementedResponse(
        endpoint="POST /api/onboard/shopify-oauth-start",
        detail="Wires to ShopifyService.start_oauth(). Returns {redirect_url} when complete.",
    )


@router.get(
    "/shopify-oauth-callback",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Shopify OAuth callback - exchanges code for token, kicks off ingest job",
)
async def shopify_oauth_callback(
    code: str | None = None,
    shop: str | None = None,
    state: str | None = None,
    hmac: str | None = None,
) -> NotImplementedResponse:
    """OAuth callback. Final response: `{store_id, ingest_job_id}`."""
    logger.info("onboard.shopify_oauth_callback shop=%s state=%s", shop, state)
    return NotImplementedResponse(
        endpoint="GET /api/onboard/shopify-oauth-callback",
        detail="Validates HMAC, exchanges code, persists store, enqueues ingest job.",
    )


@router.get(
    "/ingest/{job_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Ingest-job status (polled by /onboard wizard)",
)
async def get_ingest_status(job_id: str) -> NotImplementedResponse:
    """Final response: `{status, products, policies, reviews}`."""
    logger.info("onboard.get_ingest_status job_id=%s", job_id)
    return NotImplementedResponse(
        endpoint=f"GET /api/onboard/ingest/{job_id}",
        detail="Returns ingest job progress. Counts pulled from Neo4j once nodes land.",
    )
