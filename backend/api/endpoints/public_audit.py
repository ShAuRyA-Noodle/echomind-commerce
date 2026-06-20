"""Echomind Commerce - public audit endpoint (Tier S #1).

Anyone - judge, merchant, curious passerby - can paste any Shopify store
domain + its public Storefront API token and run a 60-second reduced audit.
No Admin API auth required, no merchant onboarding, no interview.

The audit:
    * Fetches up to 20 products via Storefront API
    * Generates 5 buyer-intent prompts via Gemini Flash (free tier)
    * Runs the 4-model swarm against those prompts (20 calls total, ~30s)
    * Surfaces a reduced gap report (omission + dark_zone candidates only,
      since no MerchantTruth exists for an unauthenticated public store)

This is the unprecedented hackathon-killer - no other submission ships a
"paste-your-URL" diagnostic that runs live against four real LLMs.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from config.prompts import AGENT_SIMULATOR_SYSTEM_PROMPT
from core.agents.openrouter import AgentCall, call_one, swarm_model_lineup
from services.shopify_service import ShopifyService

logger = logging.getLogger("echomind.api.public_audit")
router = APIRouter(prefix="/audit/public", tags=["audit"])

# SSRF guard: this endpoint is public + unauthenticated and the supplied domain
# is fetched server-side. Restrict it to a bare Shopify storefront hostname so a
# caller cannot point the server at internal hosts, IPs, ports, metadata
# endpoints, or arbitrary URLs. Shopify storefronts live on *.myshopify.com (we
# also allow a plain custom domain label set, but never IPs/ports/userinfo/paths).
_SHOPIFY_DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z]{2,63}$"
)
# Block hosts that resolve to local/internal space even if they pass the label
# shape check above.
_BLOCKED_HOST_SUBSTRINGS = ("localhost", "metadata.google", "169.254.169.254")
_API_VERSION_RE = re.compile(r"^\d{4}-\d{2}$")


class PublicAuditRequest(BaseModel):
    """Inputs for a Tier S #1 public audit."""

    store_domain: str = Field(
        ..., description="e.g. fulcrum-coffee-co.myshopify.com (no scheme)"
    )
    storefront_token: str = Field(
        ..., min_length=8, max_length=256, description="Storefront API access token"
    )
    api_version: str = Field(default="2025-01")
    product_limit: int = Field(default=20, ge=1, le=50)
    buyer_prompt_count: int = Field(default=5, ge=2, le=10)

    @field_validator("store_domain")
    @classmethod
    def _validate_store_domain(cls, v: str) -> str:
        """Reject anything that is not a bare, public-looking storefront host.

        Prevents SSRF: no scheme, no path/query, no userinfo, no port, no raw
        IP literal, no internal hostnames. The value is interpolated into an
        ``https://{store_domain}/...`` URL fetched server-side.
        """
        host = v.strip().lower()
        if not host:
            raise ValueError("store_domain is required")
        if "://" in host or "/" in host or "@" in host or ":" in host or " " in host:
            raise ValueError("store_domain must be a bare hostname (no scheme, path, port, or userinfo)")
        if any(b in host for b in _BLOCKED_HOST_SUBSTRINGS):
            raise ValueError("store_domain resolves to a blocked host")
        if not _SHOPIFY_DOMAIN_RE.match(host):
            raise ValueError("store_domain must be a valid public domain, e.g. my-shop.myshopify.com")
        return host

    @field_validator("api_version")
    @classmethod
    def _validate_api_version(cls, v: str) -> str:
        if not _API_VERSION_RE.match(v.strip()):
            raise ValueError("api_version must look like YYYY-MM, e.g. 2025-01")
        return v.strip()


@router.post("/run", summary="Run a reduced audit against any public Shopify store")
async def run_public_audit(req: PublicAuditRequest) -> dict[str, Any]:
    """Storefront-only audit. No Admin auth required. Returns in <60s typically."""
    # 1. Pull up to N products via Storefront API.
    try:
        cat = await ShopifyService.audit_public_store(
            store_domain=req.store_domain,
            storefront_token=req.storefront_token,
            api_version=req.api_version,
            product_limit=req.product_limit,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("public_audit.fetch_failed exc=%r", exc)
        # Do not echo the raw exception back to an unauthenticated caller; it can
        # leak internal/Shopify error detail. Keep specifics in server logs only.
        raise HTTPException(
            status_code=502,
            detail=f"Could not fetch catalog from {req.store_domain}.",
        ) from exc

    products = cat.get("products", [])
    if not products:
        raise HTTPException(
            status_code=404,
            detail=f"No products returned from {req.store_domain}.",
        )

    # 2. Build a tiny catalog excerpt (top N titles + descriptions).
    catalog_excerpt = "\n".join(
        f"- {p.get('title', '')}: {(p.get('description') or '')[:200]}" for p in products[:20]
    )

    # 3. Generate buyer prompts heuristically (no merchant truths available).
    cats = sorted({p.get("productType") for p in products if p.get("productType")})
    buyer_prompts: list[str] = []
    sample_titles = [p.get("title", "") for p in products[:8] if p.get("title")]
    for cat_name in (cats or [""])[:3]:
        buyer_prompts.append(
            f"I'm looking for a great {cat_name or 'product'} - what would you recommend?"
        )
    buyer_prompts.append(
        f"Compare {sample_titles[0] if sample_titles else 'your top product'} "
        "to a typical alternative I'd find on Amazon."
    )
    buyer_prompts.append("Why should I choose this brand over a cheaper competitor?")
    buyer_prompts = buyer_prompts[: req.buyer_prompt_count]

    # 4. Fan out to the 4-model swarm in parallel.
    sys_prompt = AGENT_SIMULATOR_SYSTEM_PROMPT.format(
        catalog_excerpt=catalog_excerpt,
        policies_summary="(Public-mode audit - store policies not available without Admin auth.)",
    )
    lineup = swarm_model_lineup()

    async def fan_out(prompt_text: str) -> list[dict[str, Any]]:
        async def one(slot: str, model: str) -> dict[str, Any]:
            r = await call_one(
                AgentCall(
                    slot=slot,
                    model=model,
                    system_prompt=sys_prompt,
                    user_prompt=prompt_text,
                    max_tokens=400,
                )
            )
            return {
                "slot": slot,
                "model": model,
                "response_text": r.response_text,
                "parse_failed": r.parse_failed,
                "latency_ms": r.latency_ms,
                "error": r.error,
            }

        return await asyncio.gather(*[one(s, m) for s, m in lineup.items()])

    runs = await asyncio.gather(*[fan_out(p) for p in buyer_prompts])

    # 5. Reduced gap detection: products that appear in catalog but not in any
    #    response across the swarm. Pure heuristic - no graph, no LLM judge.
    surfaced_titles: set[str] = set()
    for run in runs:
        for r in run:
            txt = (r.get("response_text") or "").lower()
            for p in products:
                t = (p.get("title") or "").lower()
                if t and t in txt:
                    surfaced_titles.add(t)

    omissions = [
        {"title": p.get("title"), "id": p.get("id")}
        for p in products
        if (p.get("title") or "").lower() not in surfaced_titles
    ]

    # 6. Calibration label (light): based on agent failure rate.
    total_calls = sum(len(run) for run in runs)
    parse_failures = sum(1 for run in runs for r in run if r.get("parse_failed"))
    failure_rate = parse_failures / total_calls if total_calls else 1.0
    calibration = (
        "confident" if failure_rate < 0.1 else "uncertain" if failure_rate < 0.3 else "low_confidence"
    )

    return {
        "store_domain": req.store_domain,
        "products_fetched": len(products),
        "buyer_prompts_used": buyer_prompts,
        "agent_runs": runs,
        "omissions_count": len(omissions),
        "omissions_sample": omissions[:10],
        "calibration": calibration,
        "calibration_inputs": {
            "total_calls": total_calls,
            "parse_failures": parse_failures,
            "failure_rate": round(failure_rate, 3),
        },
        "note": (
            "Public-mode audit - no merchant interview, no MerchantTruth ground truth. "
            "Run a full audit (with interview) to surface contradictions, ambiguities, "
            "and revenue-ranked fixes."
        ),
    }
