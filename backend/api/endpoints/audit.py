"""Echomind Commerce - `/api/audit/*` endpoints.

Wired to live graph reads. The audit dashboard pulls per-type node + edge
counts, the gap list with calibration labels, and a coarse readiness score.

Endpoints
    GET /api/audit/{store_id}        - dashboard summary
    GET /api/audit/{store_id}/gaps   - ranked gap list with affected products
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from graph.neo4j_client import neo4j_client
from graph.operations import graph_stats
from graph.queries import GAPS_WITH_AFFECTED_PRODUCTS

logger = logging.getLogger("echomind.api.audit")
router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/{store_id}", summary="Audit dashboard summary (live Neo4j read)")
async def get_audit(store_id: str) -> dict[str, Any]:
    """Dashboard payload: graph stats, readiness score, calibration mix, totals."""
    stats = await graph_stats()

    nodes = stats.get("nodes", {})
    products = nodes.get("Product", 0)
    truths = nodes.get("MerchantTruth", 0)
    agent_reps = nodes.get("AgentRepresentation", 0)
    gaps = nodes.get("Gap", 0)
    fixes = nodes.get("FixSuggestion", 0)

    calibration_mix = await _calibration_distribution()

    # Coarse readiness score: penalize gaps proportional to severity, weighted
    # by calibration confidence. Real version pulls per-gap fields from Neo4j.
    readiness_score = max(
        0,
        min(
            100,
            70
            + min(20, products // 2)
            + min(10, truths)
            - max(0, gaps * 2)
            + min(10, fixes),
        ),
    )

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


@router.get("/{store_id}/gaps", summary="Ranked gap list with affected products")
async def get_audit_gaps(store_id: str) -> dict[str, Any]:
    rows = await neo4j_client.run(GAPS_WITH_AFFECTED_PRODUCTS)
    return {"status": "ok", "store_id": store_id, "gaps": rows}


async def _calibration_distribution() -> dict[str, int]:
    cypher = """
    MATCH (g:Gap)
    WITH coalesce(g.calibration_label, 'uncertain') AS label, count(*) AS c
    RETURN label, c
    """
    rows = await neo4j_client.run(cypher)
    return {row["label"]: row["c"] for row in rows}
