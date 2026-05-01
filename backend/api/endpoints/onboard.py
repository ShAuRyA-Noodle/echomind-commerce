"""Echomind Commerce - `/api/onboard/*` endpoints.

Wired to real Shopify ingest + Neo4j graph writes. The Custom App flow
skips OAuth (the merchant pastes the Admin API token at install time);
the ingest endpoint pulls products, policies, and reviews via the live
Admin GraphQL API and writes typed nodes to Neo4j.

Endpoints
    POST   /api/onboard/ingest/run     - kick off catalog crawl
    GET    /api/onboard/ingest/status  - live counts pulled from Neo4j
    POST   /api/onboard/shopify-oauth-start    (stub for v2 marketplace flow)
    GET    /api/onboard/shopify-oauth-callback (stub for v2 marketplace flow)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status

from api.schemas import NotImplementedResponse, Product, Policy, TrustSignal
from graph.operations import (
    deterministic_id,
    upsert_typed,
    graph_stats,
)
from services.shopify_service import shopify_service, ShopifyError

logger = logging.getLogger("echomind.api.onboard")
router = APIRouter(prefix="/onboard", tags=["onboard"])


@router.post(
    "/ingest/run",
    summary="Crawl Shopify catalog + policies + reviews into Neo4j (real)",
)
async def run_ingest(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Pull live catalog from Shopify Admin GraphQL, write typed nodes to Neo4j.

    Uses the env-configured `SHOPIFY_ADMIN_ACCESS_TOKEN`. Idempotent on
    `Product.id` so re-runs are safe.
    """
    started = datetime.now(timezone.utc)
    products_written = 0
    policies_written = 0
    reviews_written = 0

    try:
        shop = await shopify_service.fetch_shop_metadata()
    except ShopifyError as exc:
        raise HTTPException(status_code=502, detail=f"Shopify auth failed: {exc}") from exc

    # Stream products into Neo4j as they arrive.
    async for sp in shopify_service.crawl_products(page_size=50):
        product = Product(
            id=deterministic_id("prod", sp.get("handle") or sp.get("id", "")),
            shopify_gid=sp.get("id"),
            title=sp.get("title", ""),
            description=(sp.get("description") or "")[:4000] or None,
            currency=(shop.get("currencyCode") if isinstance(shop, dict) else None) or "USD",
            tags=list(sp.get("tags") or []),
            image_urls=[
                edge.get("node", {}).get("url")
                for edge in (sp.get("images") or {}).get("edges", [])
                if edge.get("node", {}).get("url")
            ],
        )
        await upsert_typed(product, "Product")
        products_written += 1

    # Policies (shop-scoped pages).
    try:
        policies = await shopify_service.fetch_policies()
    except ShopifyError:
        policies = []
    for pol in policies:
        if not pol.get("body"):
            continue
        pid = deterministic_id("policy", pol.get("_kind", "other"), (pol.get("body") or "")[:64])
        kind = (pol.get("_kind") or "other").replace("Policy", "").lower()
        kind_map = {
            "refund": "return",
            "shipping": "shipping",
            "termsofservice": "warranty",
            "privacy": "warranty",
            "subscription": "exchange",
        }
        await upsert_typed(
            Policy(
                id=pid,
                type=kind_map.get(kind, "other"),  # type: ignore[arg-type]
                text=(pol.get("body") or "")[:4000],
                scope="global",
                source_url=pol.get("url"),
            ),
            "Policy",
        )
        policies_written += 1

    # Reviews ingested via the per-product `fulcrum_reviews.items` metafield.
    try:
        reviews = await shopify_service.fetch_reviews()
    except ShopifyError:
        reviews = []
    for r in reviews:
        if not r.get("text") and not r.get("body"):
            continue
        rid = deterministic_id("trust", r.get("_product_id", ""), (r.get("text") or r.get("body", ""))[:64])
        await upsert_typed(
            TrustSignal(
                id=rid,
                type="review",
                value=(r.get("text") or r.get("body", ""))[:1000],
                attached_to=r.get("_product_id"),
            ),
            "TrustSignal",
        )
        reviews_written += 1

    logger.info(
        "onboard.ingest.complete shop=%s products=%d policies=%d reviews=%d",
        shop.get("name") if isinstance(shop, dict) else "?",
        products_written,
        policies_written,
        reviews_written,
    )
    return {
        "status": "ok",
        "shop": shop.get("name") if isinstance(shop, dict) else None,
        "currency": shop.get("currencyCode") if isinstance(shop, dict) else None,
        "products": products_written,
        "policies": policies_written,
        "reviews": reviews_written,
        "started_at": started.isoformat(),
        "duration_seconds": round((datetime.now(timezone.utc) - started).total_seconds(), 2),
    }


@router.get("/ingest/status", summary="Live ingest counts pulled from Neo4j")
async def get_ingest_status() -> dict[str, Any]:
    """Return the current node + edge counts in the graph by type."""
    stats = await graph_stats()
    return {"status": "ok", **stats}


@router.post(
    "/shopify-oauth-start",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Begin Shopify OAuth (v2 marketplace flow)",
)
async def shopify_oauth_start(payload: dict[str, Any] | None = None) -> NotImplementedResponse:
    """v2 marketplace flow stub. v1 uses Custom App token paste."""
    return NotImplementedResponse(
        endpoint="POST /api/onboard/shopify-oauth-start",
        detail="v2 marketplace flow. Hackathon submission uses Custom App token from .env.",
    )


@router.get(
    "/shopify-oauth-callback",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Shopify OAuth callback (v2 marketplace flow)",
)
async def shopify_oauth_callback(
    code: str | None = None,
    shop: str | None = None,
    state: str | None = None,
    hmac: str | None = None,
) -> NotImplementedResponse:
    return NotImplementedResponse(
        endpoint="GET /api/onboard/shopify-oauth-callback",
        detail="v2 marketplace flow. v1 is /api/onboard/ingest/run with the .env token.",
    )
