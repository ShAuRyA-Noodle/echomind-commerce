"""Echomind Commerce - fix re-test orchestrator (WINNING_PLAN §17.2).

After a fix is applied to Shopify, re-runs the agent swarm scoped to
(a) the affected products, and (b) the buyer prompts that previously
surfaced this gap. Computes the measured before/after surface-rate delta
and labels the prediction calibration.

This closes the loop: detect → fix → re-test → measure.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from api.schemas import AgentRepresentation, FixSuggestion, Gap

logger = logging.getLogger("echomind.fix.retest")


@dataclass(frozen=True)
class DeltaResult:
    """Before/after measurement for one fix."""

    before_surface_rate: float
    after_surface_rate: float
    delta_pp: float  # percentage points
    in_predicted_range: bool
    n_calls_before: int
    n_calls_after: int


def compute_surface_rate(
    representations: list[AgentRepresentation], target_product_titles: list[str]
) -> float:
    """Fraction of representations that surfaced any of `target_product_titles`."""
    if not representations:
        return 0.0
    titles_lower = {t.lower() for t in target_product_titles if t}
    if not titles_lower:
        return 0.0
    hits = 0
    for r in representations:
        for s in r.surfaced_products or []:
            if s.lower() in titles_lower:
                hits += 1
                break
    return hits / len(representations)


def measure_delta(
    *,
    fix: FixSuggestion,
    gap: Gap,
    before: list[AgentRepresentation],
    after: list[AgentRepresentation],
    target_product_titles: list[str],
) -> DeltaResult:
    """Compute the delta and check it against the predicted range."""
    b_rate = compute_surface_rate(before, target_product_titles)
    a_rate = compute_surface_rate(after, target_product_titles)
    delta_pp = (a_rate - b_rate) * 100.0
    pdr = fix.predicted_delta_range
    in_range = bool(pdr and pdr.low <= delta_pp <= pdr.high)
    logger.info(
        "retest.delta gap_id=%s before=%.3f after=%.3f delta_pp=%.1f in_range=%s",
        gap.id,
        b_rate,
        a_rate,
        delta_pp,
        in_range,
    )
    return DeltaResult(
        before_surface_rate=b_rate,
        after_surface_rate=a_rate,
        delta_pp=delta_pp,
        in_predicted_range=in_range,
        n_calls_before=len(before),
        n_calls_after=len(after),
    )


def serialize_delta(delta: DeltaResult) -> dict[str, Any]:
    """JSON-friendly representation for the audit dashboard before/after panel."""
    return {
        "before_surface_rate": round(delta.before_surface_rate, 3),
        "after_surface_rate": round(delta.after_surface_rate, 3),
        "delta_pp": round(delta.delta_pp, 1),
        "in_predicted_range": delta.in_predicted_range,
        "n_calls_before": delta.n_calls_before,
        "n_calls_after": delta.n_calls_after,
    }


__all__ = ["DeltaResult", "compute_surface_rate", "measure_delta", "serialize_delta"]
