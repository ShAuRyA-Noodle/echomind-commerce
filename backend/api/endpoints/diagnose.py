"""Echomind Commerce - `/api/diagnose/*` endpoints.

Wired to real Cypher candidate detection + Gemini Pro judge + calibrator
+ revenue model + ranker. Persists every Gap node to Neo4j.

Endpoints
    POST /api/diagnose/run                          - find + classify + rank gaps
    GET  /api/diagnose/{diagnose_id}                - all gaps from Neo4j for this run
    GET  /api/diagnose/{diagnose_id}/gap/{gap_id}   - single gap detail + reasoning trace
"""

from __future__ import annotations

import logging
from typing import Any

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.ownership import ScopeContext, scope_ctx
from core.diagnose.cypher_diff import find_all_candidates
from core.diagnose.judge import classify_candidate
from core.diagnose.ranker import GapRankingInputs, rank_gaps, split_for_ui
from graph.neo4j_client import neo4j_client
from graph.operations import deterministic_id, upsert_typed

logger = logging.getLogger("echomind.api.diagnose")
router = APIRouter(prefix="/diagnose", tags=["diagnose"])


class DiagnoseRequest(BaseModel):
    surface_loss_rate: float = Field(default=0.5, ge=0.0, le=1.0)


@router.post("/run", summary="Find, classify, calibrate, rank gaps (real)")
async def run_diagnose(
    req: DiagnoseRequest | None = None,
    scope: ScopeContext = Depends(scope_ctx),
) -> dict[str, Any]:
    """Run the full diagnose pipeline.

    Steps (per WINNING_PLAN section 16.2):
        1. Cypher candidate detection across 5 gap types
        2. Gemini Pro classification + calibration per candidate
        3. Persist Gap nodes to Neo4j
        4. Rank by gap_priority, split into 4 UI buckets
    """
    surface_loss_rate = req.surface_loss_rate if req else 0.5
    started_at = datetime.now(timezone.utc)
    run_id = deterministic_id("drun", started_at.isoformat(), str(surface_loss_rate))

    candidates = await find_all_candidates()
    flat_candidates = [c for group in candidates.values() for c in group]
    logger.info("diagnose.candidates run_id=%s total=%d", run_id, len(flat_candidates))

    classified = []
    for cand in flat_candidates:
        gap = await classify_candidate(cand, surface_loss_rate=surface_loss_rate)
        # Stamp owner_uid when auth is on so subsequent scoped reads find it.
        await upsert_typed(gap, "Gap", scope=scope)
        # Tag with run id + timestamp so subsequent /api/diagnose/{run_id} calls
        # can filter; legacy gaps (no diagnose_run_id) still fall back to "latest".
        # The owner predicate keeps cross-tenant Gaps untouched when auth is on.
        await neo4j_client.run(
            f"MATCH (g:Gap {{id: $id}}) WHERE {scope.predicate('g')} "
            "SET g.diagnose_run_id = $rid, g.diagnose_run_at = $ts",
            scope.params({"id": gap.id, "rid": run_id, "ts": started_at.isoformat()}),
        )
        classified.append(gap)

    inputs_by_id = {g.id: GapRankingInputs() for g in classified}
    ranked = rank_gaps(classified, inputs_by_id)
    buckets = split_for_ui(ranked)

    return {
        "status": "ok",
        "run_id": run_id,
        "started_at": started_at.isoformat(),
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


@router.get("/{diagnose_id}", summary="Gaps for a specific diagnose run (or latest if `_`/`latest`)")
async def get_diagnose(
    diagnose_id: str,
    scope: ScopeContext = Depends(scope_ctx),
) -> dict[str, Any]:
    """Return Gap nodes scoped to a diagnose run.

    Resolution order:
        - `diagnose_id` == "_" or "latest": pick most recent `diagnose_run_id`
          present on any Gap; if none have a run id (legacy), return all.
        - otherwise: filter by exact `diagnose_run_id`.

    All reads are additionally scoped to the authenticated owner when auth is on.
    """
    resolved_id = diagnose_id
    if diagnose_id in {"_", "latest"}:
        latest = await neo4j_client.run(
            f"""
            MATCH (g:Gap) WHERE g.diagnose_run_id IS NOT NULL AND {scope.predicate("g")}
            RETURN g.diagnose_run_id AS rid, g.diagnose_run_at AS ts
            ORDER BY g.diagnose_run_at DESC
            LIMIT 1
            """,
            scope.params(),
        )
        resolved_id = latest[0]["rid"] if latest else None

    if resolved_id:
        rows = await neo4j_client.run(
            f"""
            MATCH (g:Gap) WHERE g.diagnose_run_id = $rid AND {scope.predicate("g")}
            RETURN g.id AS id, g.type AS type, g.severity AS severity,
                   g.calibration_label AS calibration_label,
                   coalesce(g.revenue_impact_usd_monthly, 0.0) AS revenue_impact_usd_monthly,
                   coalesce(g.affected_products, []) AS affected_products,
                   g.diagnose_run_id AS diagnose_run_id,
                   g.diagnose_run_at AS diagnose_run_at
            ORDER BY g.revenue_impact_usd_monthly DESC, g.severity DESC
            LIMIT 50
            """,
            scope.params({"rid": resolved_id}),
        )
    else:
        # Legacy fallback: no Gap has a run id yet (pre-migration data).
        rows = await neo4j_client.run(
            f"""
            MATCH (g:Gap) WHERE {scope.predicate("g")}
            RETURN g.id AS id, g.type AS type, g.severity AS severity,
                   g.calibration_label AS calibration_label,
                   coalesce(g.revenue_impact_usd_monthly, 0.0) AS revenue_impact_usd_monthly,
                   coalesce(g.affected_products, []) AS affected_products,
                   null AS diagnose_run_id,
                   null AS diagnose_run_at
            ORDER BY g.revenue_impact_usd_monthly DESC, g.severity DESC
            LIMIT 50
            """,
            scope.params(),
        )

    gaps = [
        {
            "id": r["id"],
            "type": r["type"],
            "severity": r.get("severity", 0.5),
            "calibration_label": r.get("calibration_label", "uncertain"),
            "revenue_impact_usd_monthly": r.get("revenue_impact_usd_monthly", 0.0),
            "affected_products": r.get("affected_products", []),
            "diagnose_run_id": r.get("diagnose_run_id"),
            "diagnose_run_at": r.get("diagnose_run_at"),
        }
        for r in rows
        if r.get("id")
    ]
    return {
        "status": "ok",
        "diagnose_id": diagnose_id,
        "resolved_run_id": resolved_id,
        "gaps": gaps,
        "total": len(gaps),
    }


@router.get(
    "/{diagnose_id}/gap/{gap_id}",
    summary="Single gap detail with full reasoning trace + source nodes",
)
async def get_gap(
    diagnose_id: str,
    gap_id: str,
    scope: ScopeContext = Depends(scope_ctx),
) -> dict[str, Any]:
    """Return a Gap node with its reasoning trace and all related source nodes.

    Fetches the Gap, its affected Products (with shopify_gid), the MerchantTruths
    that led to its detection, the AgentRepresentations that were involved, and
    any existing FixSuggestion. The frontend diff page builds its cinematic
    reasoning-trace animation from this response. All reads are scoped to the
    authenticated owner when auth is on.
    """
    logger.debug("gap.detail diagnose_id=%s gap_id=%s", diagnose_id, gap_id)
    # 1. Fetch the Gap node (scoped: a cross-tenant gap_id reads as not_found)
    gap_rows = await neo4j_client.run(
        f"MATCH (g:Gap {{id: $id}}) WHERE {scope.predicate('g')} RETURN g LIMIT 1",
        scope.params({"id": gap_id}),
    )
    if not gap_rows:
        return {"status": "not_found", "gap_id": gap_id}

    g: dict[str, Any] = gap_rows[0]["g"]
    affected_products: list[str] = g.get("affected_products") or []

    # 2. Affected Product nodes (shopify_gid needed for fix apply)
    product_rows: list[dict[str, Any]] = []
    if affected_products:
        product_rows = await neo4j_client.run(
            f"""
            MATCH (p:Product) WHERE p.id IN $ids AND {scope.predicate("p")}
            RETURN p.id AS id, p.title AS title,
                   p.shopify_gid AS shopify_gid,
                   p.description AS description
            LIMIT 10
            """,
            scope.params({"ids": affected_products}),
        )

    # 3. MerchantTruths related to affected products (via DESCRIBES edge)
    truth_rows: list[dict[str, Any]] = []
    if affected_products:
        truth_rows = await neo4j_client.run(
            f"""
            MATCH (m:MerchantTruth)-[:DESCRIBES]->(p:Product)
            WHERE p.id IN $ids AND {scope.predicate("m")} AND {scope.predicate("p")}
            RETURN m.id AS id, m.statement AS statement,
                   m.tacit_category AS tacit_category,
                   m.tacit_level AS tacit_level,
                   m.confidence AS confidence,
                   p.id AS product_id
            LIMIT 10
            """,
            scope.params({"ids": affected_products}),
        )
    # Fallback: any MerchantTruths when edges not yet written
    if not truth_rows:
        truth_rows = await neo4j_client.run(
            f"""
            MATCH (m:MerchantTruth)
            WHERE {scope.predicate("m")}
            RETURN m.id AS id, m.statement AS statement,
                   m.tacit_category AS tacit_category,
                   m.tacit_level AS tacit_level,
                   m.confidence AS confidence,
                   null AS product_id
            LIMIT 5
            """,
            scope.params(),
        )

    # 4. AgentRepresentations that mention the affected products
    agent_rows: list[dict[str, Any]] = []
    if affected_products:
        agent_rows = await neo4j_client.run(
            f"""
            MATCH (a:AgentRepresentation)-[:MENTIONS]->(p:Product)
            WHERE p.id IN $ids AND {scope.predicate("a")} AND {scope.predicate("p")}
            RETURN a.id AS id, a.agent_model AS agent_model,
                   a.response_text AS response_text,
                   a.confidence_in_recommendation AS confidence,
                   p.id AS product_id
            LIMIT 20
            """,
            scope.params({"ids": affected_products}),
        )
    # Fallback: any AgentRepresentations when MENTIONS edges not yet written
    if not agent_rows:
        agent_rows = await neo4j_client.run(
            f"""
            MATCH (a:AgentRepresentation)
            WHERE {scope.predicate("a")}
            RETURN a.id AS id, a.agent_model AS agent_model,
                   a.response_text AS response_text,
                   a.confidence_in_recommendation AS confidence,
                   null AS product_id
            LIMIT 10
            """,
            scope.params(),
        )

    # 5. Existing FixSuggestion for this gap (applied one preferred)
    fix_rows = await neo4j_client.run(
        f"""
        MATCH (f:FixSuggestion)
        WHERE f.gap_id = $gap_id AND {scope.predicate("f")}
        RETURN f ORDER BY f.applied DESC
        LIMIT 1
        """,
        scope.params({"gap_id": gap_id}),
    )
    fix: dict[str, Any] | None = fix_rows[0]["f"] if fix_rows else None

    return {
        "status": "ok",
        "gap": {
            "id": g.get("id", gap_id),
            "type": g.get("type", "omission"),
            "severity": g.get("severity", 0.5),
            "revenue_impact_usd_monthly": g.get("revenue_impact_usd_monthly", 0.0),
            "calibration_label": g.get("calibration_label", "uncertain"),
            "uncertainty_type": g.get("uncertainty_type"),
            "reasoning_chain": g.get("reasoning_chain", ""),
            "affected_products": [
                {
                    "product_id": r["id"],
                    "title": r.get("title", r["id"]),
                    "shopify_gid": r.get("shopify_gid"),
                    "description": r.get("description", ""),
                }
                for r in product_rows
            ]
            if product_rows
            else [
                {"product_id": pid, "title": pid, "shopify_gid": None, "description": ""}
                for pid in affected_products
            ],
        },
        "merchant_truths": [
            {
                "id": r["id"],
                "statement": r.get("statement", ""),
                "tacit_category": r.get("tacit_category"),
                "tacit_level": r.get("tacit_level"),
                "confidence": r.get("confidence", 0.8),
                "product_id": r.get("product_id"),
            }
            for r in truth_rows
            if r.get("id")
        ],
        "agent_representations": [
            {
                "id": r["id"],
                "agent_model": r.get("agent_model", "unknown"),
                "response_text": r.get("response_text", ""),
                "confidence": r.get("confidence"),
                "product_id": r.get("product_id"),
            }
            for r in agent_rows
            if r.get("id")
        ],
        "fix_suggestion": {
            "id": fix.get("id"),
            "fix_type": fix.get("fix_type", "copy_rewrite"),
            "proposed_text": fix.get("proposed_text", ""),
            "applied": fix.get("applied", False),
            "applied_at": fix.get("applied_at"),
            "predicted_delta_low": fix.get("predicted_delta_low"),
            "predicted_delta_high": fix.get("predicted_delta_high"),
            "voice_match_notes": fix.get("voice_match_notes"),
        }
        if fix
        else None,
    }
