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


async def _calibration_distribution() -> dict[str, int]:
    rows = await neo4j_client.run(
        "MATCH (g:Gap) WITH coalesce(g.calibration_label,'uncertain') AS label, count(*) AS c RETURN label, c"
    )
    return {row["label"]: row["c"] for row in rows}
