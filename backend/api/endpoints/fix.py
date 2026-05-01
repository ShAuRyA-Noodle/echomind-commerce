"""Echomind Commerce - `/api/fix/*` endpoints.

Wired to real fix copy generation + Shopify Admin mutation + retest delta.

Endpoints
    POST /api/fix/generate/{gap_id}  - Gemini Pro copy gen (in merchant voice)
    POST /api/fix/apply              - push hydrated FixSuggestion to Shopify (real)
    POST /api/fix/retest/{fix_id}    - rerun swarm + measure observed delta
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.schemas import FixSuggestion, Gap, NotImplementedResponse
from core.fix.copy_generator import generate_fix
from core.fix.shopify_writer import apply_fix
from graph.operations import upsert_typed

logger = logging.getLogger("echomind.api.fix")
router = APIRouter(prefix="/fix", tags=["fix"])


class GenerateFixRequest(BaseModel):
    fix_type: str | None = None
    severity: float = Field(default=0.5, ge=0.0, le=1.0)
    affected_products: list[str] = Field(default_factory=list)
    merchant_voice_samples: list[str] = Field(default_factory=list)
    subgraph_direct: list[dict[str, Any]] = Field(default_factory=list)
    subgraph_semantic: list[dict[str, Any]] = Field(default_factory=list)
    subgraph_decisions: list[dict[str, Any]] = Field(default_factory=list)
    subgraph_contradictions: list[dict[str, Any]] = Field(default_factory=list)


class ApplyFixFullRequest(BaseModel):
    fix: FixSuggestion
    target_product_gid: str | None = None
    target_page_gid: str | None = None


@router.post("/generate/{gap_id}", summary="Generate FixSuggestion for a Gap (Gemini Pro)")
async def generate_fix_endpoint(gap_id: str, req: GenerateFixRequest) -> dict[str, Any]:
    """Build a fix using the 4-strategy subgraph + merchant voice samples."""
    gap = Gap(
        id=gap_id,
        type=req.fix_type or "omission",  # type: ignore[arg-type]
        severity=req.severity,
        affected_products=req.affected_products,
    )
    fix = await generate_fix(
        gap=gap,
        subgraph_direct=req.subgraph_direct,
        subgraph_semantic=req.subgraph_semantic,
        subgraph_decisions=req.subgraph_decisions,
        subgraph_contradictions=req.subgraph_contradictions,
        merchant_voice_samples=req.merchant_voice_samples,
    )
    await upsert_typed(fix, "FixSuggestion")
    return _serialize_fix(fix)


@router.post("/apply", summary="Apply hydrated FixSuggestion to Shopify (real mutation)")
async def apply_fix_full(req: ApplyFixFullRequest) -> dict[str, Any]:
    """Push the fix to Shopify Admin GraphQL.

    Caller hands the FixSuggestion (queried from Neo4j) plus the target gid.
    """
    applied = await apply_fix(
        req.fix,
        target_product_gid=req.target_product_gid,
        target_page_gid=req.target_page_gid,
    )
    await upsert_typed(applied, "FixSuggestion")
    return _serialize_fix(applied)


@router.post(
    "/retest/{fix_id}",
    response_model=NotImplementedResponse,
    summary="Rerun swarm + measure observed delta",
)
async def retest_fix(fix_id: str) -> NotImplementedResponse:
    """Wires to retest_orchestrator.measure_delta + simulate.run_swarm."""
    return NotImplementedResponse(
        endpoint=f"POST /api/fix/retest/{fix_id}",
        detail=(
            "Reruns swarm scoped to affected products + buyer prompts that "
            "previously surfaced the gap, computes observed_delta, persists."
        ),
    )


def _serialize_fix(fix: FixSuggestion) -> dict[str, Any]:
    pdr = fix.predicted_delta_range
    return {
        "id": fix.id,
        "gap_id": fix.gap_id,
        "fix_type": fix.fix_type,
        "proposed_text": fix.proposed_text,
        "applied": fix.applied,
        "applied_at": fix.applied_at.isoformat() if fix.applied_at else None,
        "shopify_resource_id": fix.shopify_resource_id,
        "predicted_delta_range": (
            {"low": pdr.low, "high": pdr.high, "metric": pdr.metric, "rationale": pdr.rationale}
            if pdr
            else None
        ),
        "observed_delta": fix.observed_delta,
        "voice_match_notes": fix.voice_match_notes,
    }
