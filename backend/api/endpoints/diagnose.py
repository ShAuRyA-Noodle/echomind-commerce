"""Echomind Commerce - `/api/diagnose/*` endpoints.

Wired to real Cypher candidate detection + Gemini Pro judge + calibrator
+ revenue model + ranker. Persists every Gap node to Neo4j.

Endpoints
    POST /api/diagnose/run                          - find + classify + rank gaps
    GET  /api/diagnose/{diagnose_id}                - persisted gap list
    GET  /api/diagnose/{diagnose_id}/gap/{gap_id}   - single gap detail
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.schemas import NotImplementedResponse
from core.diagnose.cypher_diff import find_all_candidates
from core.diagnose.judge import classify_candidate
from core.diagnose.ranker import GapRankingInputs, rank_gaps, split_for_ui
from graph.operations import upsert_typed

logger = logging.getLogger("echomind.api.diagnose")
router = APIRouter(prefix="/diagnose", tags=["diagnose"])


class DiagnoseRequest(BaseModel):
    surface_loss_rate: float = Field(default=0.5, ge=0.0, le=1.0)


@router.post("/run", summary="Find, classify, calibrate, rank gaps (real)")
async def run_diagnose(req: DiagnoseRequest | None = None) -> dict[str, Any]:
    """Run the full diagnose pipeline.

    Steps (per WINNING_PLAN section 16.2):
        1. Cypher candidate detection across 5 gap types
        2. Gemini Pro classification + calibration per candidate
        3. Persist Gap nodes to Neo4j
        4. Rank by gap_priority, split into 4 UI buckets
    """
    surface_loss_rate = req.surface_loss_rate if req else 0.5
    candidates = await find_all_candidates()
    flat_candidates = [c for group in candidates.values() for c in group]
    logger.info("diagnose.candidates total=%d", len(flat_candidates))

    classified = []
    for cand in flat_candidates:
        gap = await classify_candidate(cand, surface_loss_rate=surface_loss_rate)
        await upsert_typed(gap, "Gap")
        classified.append(gap)

    inputs_by_id = {g.id: GapRankingInputs() for g in classified}
    ranked = rank_gaps(classified, inputs_by_id)
    buckets = split_for_ui(ranked)

    return {
        "status": "ok",
        "candidates_found": len(flat_candidates),
        "candidates_by_type": {k: len(v) for k, v in candidates.items()},
        "gaps_classified": len(classified),
        "buckets": {
            "headline": len(buckets["headline"]),
            "verify_first": len(buckets["verify_first"]),
            "advanced": len(buckets["advanced"]),
            "needs_more_data": len(buckets["needs_more_data"]),
        },
        "top_5_gaps": [
            {
                "id": g.id,
                "type": g.type,
                "severity": g.severity,
                "calibration_label": g.calibration_label,
                "revenue_impact_usd_monthly": g.revenue_impact_usd_monthly,
                "score": round(score, 4),
            }
            for g, score in ranked[:5]
        ],
    }


@router.get(
    "/{diagnose_id}",
    response_model=NotImplementedResponse,
    summary="Persisted diagnose run (lookup by id)",
)
async def get_diagnose(diagnose_id: str) -> NotImplementedResponse:
    """Run-id-keyed lookup persists in Firestore (v2). Gap nodes live in Neo4j now."""
    return NotImplementedResponse(
        endpoint=f"GET /api/diagnose/{diagnose_id}",
        detail="Per-run grouping in Firestore (v2). Gap nodes queryable now via /api/graph.",
    )


@router.get(
    "/{diagnose_id}/gap/{gap_id}",
    response_model=NotImplementedResponse,
    summary="Single gap detail with full reasoning trace + source nodes",
)
async def get_gap(diagnose_id: str, gap_id: str) -> NotImplementedResponse:
    return NotImplementedResponse(
        endpoint=f"GET /api/diagnose/{diagnose_id}/gap/{gap_id}",
        detail="Returns gap + reasoning chain + source subgraph + candidate fixes.",
    )
