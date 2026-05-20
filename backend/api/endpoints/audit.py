"""Echomind Commerce - `/api/audit/*` endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from graph.neo4j_client import neo4j_client
from graph.operations import graph_stats

logger = logging.getLogger("echomind.api.audit")
router = APIRouter(prefix="/audit", tags=["audit"])

# Direct gap fetch - no HARMS edges required (they are written only when
# fix is applied; gaps detected before fixes have no HARMS edges yet).
GAPS_DIRECT = """
MATCH (g:Gap)
RETURN g.id AS gap_id,
       g.type AS gap_type,
       coalesce(g.severity, 0.5) AS severity,
       coalesce(g.calibration_label, 'uncertain') AS calibration_label,
       coalesce(g.revenue_impact_usd_monthly, 0.0) AS revenue_impact,
       coalesce(g.reasoning_chain, '') AS reasoning_chain,
       coalesce(g.affected_products, []) AS affected_product_ids
ORDER BY g.revenue_impact_usd_monthly DESC, g.severity DESC
LIMIT 40
"""


@router.get("/{store_id}", summary="Audit dashboard summary (live Neo4j read)")
async def get_audit(store_id: str) -> dict[str, Any]:
    stats = await graph_stats()
    nodes = stats.get("nodes", {})
    products = nodes.get("Product", 0)
    truths = nodes.get("MerchantTruth", 0)
    agent_reps = nodes.get("AgentRepresentation", 0)
    gaps = nodes.get("Gap", 0)
    fixes = nodes.get("FixSuggestion", 0)
    calibration_mix = await _calibration_distribution()
    readiness_score = max(0, min(100,
        70 + min(20, products // 2) + min(10, truths) - max(0, gaps * 2) + min(10, fixes)
    ))
    return {
        "status": "ok",
        "store_id": store_id,
        "readiness_score": readiness_score,
        "graph": stats,
        "calibration_mix": calibration_mix,
        "totals": {
            "products": products,
            "merchant_truths": truths,
            "agent_representations": agent_reps,
            "gaps": gaps,
            "fixes": fixes,
        },
    }


@router.get("/{store_id}/gaps", summary="Ranked gap list (direct, no HARMS edges required)")
async def get_audit_gaps(store_id: str) -> dict[str, Any]:
    rows = await neo4j_client.run(GAPS_DIRECT, {})
    # Shape rows to match frontend ApiGap interface
    gaps = [
        {
            "gap_id": r["gap_id"],
            "gap_type": r["gap_type"],
            "severity": r["severity"],
            "calibration_label": r["calibration_label"],
            "revenue_impact": r["revenue_impact"],
            "reasoning_chain": r["reasoning_chain"],
            "affected_products": [
                {"product_id": pid, "title": pid}
                for pid in (r["affected_product_ids"] or [])
            ],
        }
        for r in rows
    ]
    return {"status": "ok", "store_id": store_id, "gaps": gaps}


@router.get("/{store_id}/timeline", summary="Chronological swarm event timeline for replay")
async def get_timeline(store_id: str) -> dict[str, Any]:
    """Return all agent responses, detected gaps, and applied fixes in time order.

    Used by the /replay page to build its timeline scrubber and event log.
    """
    logger.debug("audit.timeline store_id=%s", store_id)
    agent_rows = await neo4j_client.run(
        """
        MATCH (a:AgentRepresentation)
        OPTIONAL MATCH (b:BuyerPrompt {id: a.buyer_prompt_id})
        RETURN a.id AS id,
               a.agent_model AS agent_model,
               a.response_text AS response_text,
               coalesce(a.surfaced_products, []) AS surfaced_products,
               a.captured_at AS captured_at,
               a.confidence_in_recommendation AS confidence,
               b.prompt_text AS prompt_text,
               b.intent_class AS intent_class
        ORDER BY a.captured_at ASC
        LIMIT 100
        """,
    )

    gap_rows = await neo4j_client.run(
        """
        MATCH (g:Gap)
        RETURN g.id AS id, g.type AS type,
               coalesce(g.severity, 0.5) AS severity,
               coalesce(g.calibration_label, 'uncertain') AS calibration_label,
               coalesce(g.revenue_impact_usd_monthly, 0.0) AS revenue_impact,
               coalesce(g.affected_products, []) AS affected_products
        ORDER BY g.severity DESC
        LIMIT 20
        """,
    )

    fix_rows = await neo4j_client.run(
        """
        MATCH (f:FixSuggestion)
        WHERE f.applied = true
        RETURN f.id AS id, f.gap_id AS gap_id, f.fix_type AS fix_type,
               f.applied_at AS applied_at, f.shopify_resource_id AS shopify_resource_id,
               f.proposed_text AS proposed_text
        ORDER BY f.applied_at ASC
        LIMIT 20
        """,
    )

    events = [
        {
            "event_type": "agent_response",
            "id": r["id"],
            "agent_model": r.get("agent_model", "unknown"),
            "response_text": (r.get("response_text") or "")[:400],
            "surfaced_products": r.get("surfaced_products") or [],
            "captured_at": r.get("captured_at"),
            "confidence": r.get("confidence"),
            "prompt_text": (r.get("prompt_text") or "")[:200],
            "intent_class": r.get("intent_class", ""),
        }
        for r in agent_rows
        if r.get("id")
    ]

    return {
        "status": "ok",
        "store_id": store_id,
        "events": events,
        "gaps": [
            {
                "id": r.get("id"),
                "type": r.get("type"),
                "severity": r.get("severity", 0.5),
                "calibration_label": r.get("calibration_label", "uncertain"),
                "revenue_impact": r.get("revenue_impact", 0.0),
                "affected_products": r.get("affected_products") or [],
            }
            for r in gap_rows
            if r.get("id")
        ],
        "fixes": [
            {
                "id": r.get("id"),
                "gap_id": r.get("gap_id"),
                "fix_type": r.get("fix_type"),
                "applied_at": r.get("applied_at"),
                "shopify_resource_id": r.get("shopify_resource_id"),
                "proposed_text": (r.get("proposed_text") or "")[:200],
            }
            for r in fix_rows
            if r.get("id")
        ],
        "totals": {
            "agent_responses": len(agent_rows),
            "gaps": len(gap_rows),
            "fixes_applied": len(fix_rows),
        },
    }


@router.get("/{store_id}/decisions", summary="Decision nodes for policy decision tree")
async def get_decisions(store_id: str, type: str | None = None) -> dict[str, Any]:
    """Return Decision nodes for the policy/decision-tree page.

    Optional `type` query param filters server-side by substring match against
    question/context/outcome (case-insensitive). `type` values like
    "returns"/"shipping"/"warranty" map naturally; "all" or omitted = no filter.
    """
    logger.debug("audit.decisions store_id=%s type=%s", store_id, type)
    needle = (type or "").replace("-", " ").strip().lower()
    apply_filter = bool(needle) and needle != "all"

    if apply_filter:
        rows = await neo4j_client.run(
            """
            MATCH (d:Decision)
            WHERE toLower(coalesce(d.question, ''))  CONTAINS $needle
               OR toLower(coalesce(d.context, ''))   CONTAINS $needle
               OR toLower(coalesce(d.outcome, ''))   CONTAINS $needle
            RETURN d.id AS id, d.question AS question, d.context AS context,
                   d.outcome AS outcome,
                   coalesce(d.conditions, []) AS conditions,
                   d.frequency AS frequency,
                   coalesce(d.confidence, 0.7) AS confidence
            ORDER BY d.confidence DESC
            LIMIT 40
            """,
            {"needle": needle},
        )
    else:
        rows = await neo4j_client.run(
            """
            MATCH (d:Decision)
            RETURN d.id AS id, d.question AS question, d.context AS context,
                   d.outcome AS outcome,
                   coalesce(d.conditions, []) AS conditions,
                   d.frequency AS frequency,
                   coalesce(d.confidence, 0.7) AS confidence
            ORDER BY d.confidence DESC
            LIMIT 40
            """,
        )

    decisions = [
        {
            "id": r["id"],
            "question": r.get("question", ""),
            "context": r.get("context", ""),
            "outcome": r.get("outcome", ""),
            "conditions": r.get("conditions") or [],
            "frequency": r.get("frequency", ""),
            "confidence": r.get("confidence", 0.7),
        }
        for r in rows
        if r.get("id")
    ]
    return {
        "status": "ok",
        "store_id": store_id,
        "filter_type": type,
        "decisions": decisions,
        "total": len(decisions),
    }


async def _calibration_distribution() -> dict[str, int]:
    rows = await neo4j_client.run(
        "MATCH (g:Gap) WITH coalesce(g.calibration_label,'uncertain') AS label, count(*) AS c RETURN label, c"
    )
    return {row["label"]: row["c"] for row in rows}
