"""Echomind Commerce - frontier scorer (WINNING_PLAN §9.1).

Picks the next-best graph node to probe with a Socratic question. The score
combines five normalized signals:

    frontier_score =
          0.30 · depth_need        (1 - confidence)
        + 0.25 · connectivity_gap  (1 - outbound_edges / expected_for_type)
        + 0.15 · recency_decay     (exp(-Δt / 600s))
        + 0.20 · centrality        (PageRank approx, incrementally maintained)
        + 0.10 · phase_weight      (1.0 if category fits current phase else 0.4)

The implementation here is the math; cypher-side reads (live data) live in
`graph/queries.py::TOP_FRONTIER_MERCHANT_TRUTHS`. Question generation uses
the top-K nodes from this score.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

from api.schemas import SocraticPhase, TruthCategory


# Expected outbound-edge counts by node type (for connectivity_gap).
EXPECTED_EDGES_BY_TYPE: dict[str, int] = {
    "MerchantTruth": 3,
    "Decision": 4,
    "Pattern": 2,
    "CustomerQuestion": 2,
    "Product": 6,
    "Policy": 4,
    "TrustSignal": 1,
}


# Per-phase preferred MerchantTruth.category (boosts phase_weight).
_PHASE_PREFERS: dict[SocraticPhase, set[TruthCategory]] = {
    "brand_mapping": {"positioning", "audience", "style"},
    "product_truths": {"positioning", "audience"},
    "customer_reality": {"audience", "relationship"},
    "policy_edge_cases": {"edge_case"},
    "trust_signals": {"relationship", "style"},
}


@dataclass(frozen=True)
class FrontierInputs:
    """Per-node inputs for frontier scoring."""

    node_type: str
    confidence: float
    out_edges: int
    seconds_since_touched: float
    centrality: float = 0.5  # 0..1; PageRank approximation
    category: str | None = None  # MerchantTruth-only; None for other types


def depth_need(confidence: float) -> float:
    return max(0.0, min(1.0, 1.0 - confidence))


def connectivity_gap(node_type: str, out_edges: int) -> float:
    expected = EXPECTED_EDGES_BY_TYPE.get(node_type, 3)
    return max(0.0, min(1.0, 1.0 - (out_edges / max(1, expected))))


def recency_decay(seconds_since_touched: float) -> float:
    """exp(-Δt / 600s). Recent touches → ~1.0; older → → 0."""
    return math.exp(-max(0.0, seconds_since_touched) / 600.0)


def phase_weight(node_category: str | None, phase: SocraticPhase) -> float:
    if node_category is None:
        return 0.4
    return 1.0 if node_category in _PHASE_PREFERS.get(phase, set()) else 0.4


def frontier_score(node: FrontierInputs, phase: SocraticPhase) -> float:
    return (
        0.30 * depth_need(node.confidence)
        + 0.25 * connectivity_gap(node.node_type, node.out_edges)
        + 0.15 * recency_decay(node.seconds_since_touched)
        + 0.20 * max(0.0, min(1.0, node.centrality))
        + 0.10 * phase_weight(node.category, phase)
    )


def top_k(
    nodes: Iterable[tuple[str, FrontierInputs]],
    phase: SocraticPhase,
    k: int = 3,
) -> list[tuple[str, float]]:
    """Score and return top-K (node_id, score) pairs in descending score order."""
    scored = [(nid, frontier_score(n, phase)) for nid, n in nodes]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]


__all__ = [
    "EXPECTED_EDGES_BY_TYPE",
    "FrontierInputs",
    "depth_need",
    "connectivity_gap",
    "recency_decay",
    "phase_weight",
    "frontier_score",
    "top_k",
]
