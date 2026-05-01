"""Echomind Commerce - gap priority ranker (WINNING_PLAN §9.2).

Sorts the diagnosed gaps by what to fix first.

Formula::

    gap_priority =
          0.40 · revenue_impact_normalized
        + 0.20 · confidence (only `confident` or `certain` rank high)
        + 0.20 · fixability (FixSuggestion exists, predicted_delta_range > 10pp)
        + 0.10 · affected_products_share
        + 0.10 · agent_consensus (multiple agents reveal this gap)

Behaviour:
    * `uncertain` gaps surface but are flagged "verify first."
    * `low_confidence` gaps are hidden by default, visible in advanced view.
    * `dont_know` gaps go under "needs more data" - never actionable.
"""

from __future__ import annotations

from dataclasses import dataclass

from api.schemas import CalibrationLabel, Gap


# Confidence weight per bucket. `dont_know` and `low_confidence` are zeroed so
# they don't accidentally rank above genuinely high-evidence gaps.
_CONF_WEIGHT: dict[CalibrationLabel, float] = {
    "certain": 1.0,
    "confident": 0.85,
    "uncertain": 0.4,
    "low_confidence": 0.15,
    "dont_know": 0.0,
}


@dataclass(frozen=True)
class GapRankingInputs:
    """Side data needed to rank a Gap (not on the Gap node itself)."""

    fixability: float = 0.0  # 0..1; FixSuggestion exists with predicted delta > 10pp
    agent_consensus: float = 0.0  # 0..1; share of swarm models that revealed this gap
    affected_products_share: float = 0.0  # 0..1; affected_products / total_products


def gap_priority(
    gap: Gap,
    inputs: GapRankingInputs,
    *,
    max_revenue_in_audit: float | None = None,
) -> float:
    """Score a single gap. Higher = fix first."""
    revenue_norm = 0.0
    if max_revenue_in_audit and max_revenue_in_audit > 0:
        revenue_norm = min(1.0, gap.revenue_impact_usd_monthly / max_revenue_in_audit)
    conf_w = _CONF_WEIGHT.get(gap.calibration_label, 0.0)
    return (
        0.40 * revenue_norm
        + 0.20 * conf_w
        + 0.20 * max(0.0, min(1.0, inputs.fixability))
        + 0.10 * max(0.0, min(1.0, inputs.affected_products_share))
        + 0.10 * max(0.0, min(1.0, inputs.agent_consensus))
    )


def rank_gaps(
    gaps: list[Gap],
    inputs_by_id: dict[str, GapRankingInputs] | None = None,
) -> list[tuple[Gap, float]]:
    """Return gaps in descending priority order with their scores.

    The split-display invariant per §9.2 is enforced *by the UI*, not by this
    function. The ranker provides a single ordering; the UI surfaces:
        * `certain` / `confident` at the top
        * `uncertain` flagged "verify first"
        * `low_confidence` hidden behind "advanced view"
        * `dont_know` listed under "needs more data"
    """
    inputs_by_id = inputs_by_id or {}
    max_revenue = max((g.revenue_impact_usd_monthly for g in gaps), default=0.0)
    ranked = [
        (g, gap_priority(g, inputs_by_id.get(g.id, GapRankingInputs()), max_revenue_in_audit=max_revenue))
        for g in gaps
    ]
    ranked.sort(key=lambda pair: pair[1], reverse=True)
    return ranked


def split_for_ui(
    ranked: list[tuple[Gap, float]],
) -> dict[str, list[tuple[Gap, float]]]:
    """Split ranked gaps into the four UI buckets per §9.2."""
    headline: list[tuple[Gap, float]] = []
    verify_first: list[tuple[Gap, float]] = []
    advanced: list[tuple[Gap, float]] = []
    needs_more_data: list[tuple[Gap, float]] = []
    for g, score in ranked:
        if g.calibration_label in ("certain", "confident"):
            headline.append((g, score))
        elif g.calibration_label == "uncertain":
            verify_first.append((g, score))
        elif g.calibration_label == "low_confidence":
            advanced.append((g, score))
        else:  # dont_know
            needs_more_data.append((g, score))
    return {
        "headline": headline,
        "verify_first": verify_first,
        "advanced": advanced,
        "needs_more_data": needs_more_data,
    }


__all__ = [
    "GapRankingInputs",
    "gap_priority",
    "rank_gaps",
    "split_for_ui",
]
