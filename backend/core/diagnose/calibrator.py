"""Echomind Commerce - calibration formula (WINNING_PLAN §9.3, verbatim).

This is the *load-bearing trust signal* of the entire product. The 5-bucket
labels here are surfaced everywhere a confidence is shown - gap cards, fix
predictions, twin answers, the audit dashboard radar.

Formula::

    adjusted = 0.4·raw + 0.3·evidence + 0.3·coverage

    label = ≥0.80 certain | ≥0.60 confident | ≥0.35 uncertain
          | ≥0.15 low_confidence | else dont_know

The CRITICAL distinction (WINNING_PLAN §9.4):
    "I don't know"  = subgraph has essentially no relevant nodes (coverage <0.15).
    "I'm uncertain" = relevant nodes exist but are sparse / contradictory.

These two are surfaced with different colours and different copy. They are
NOT interchangeable.
"""

from __future__ import annotations

from typing import Literal

from api.schemas import CalibrationBlock, CalibrationLabel, UncertaintyType

# Bucket boundaries - locked by §9.3. Anything that needs to change here is a
# decision-log-worthy event because every UI surface depends on it.
_BUCKETS: tuple[tuple[float, CalibrationLabel], ...] = (
    (0.80, "certain"),
    (0.60, "confident"),
    (0.35, "uncertain"),
    (0.15, "low_confidence"),
    (0.00, "dont_know"),
)

_DONT_KNOW_COVERAGE_FLOOR = 0.15  # §9.4


def adjusted_confidence(
    raw: float,
    evidence_factor: float,
    coverage_factor: float,
) -> float:
    """0.4·raw + 0.3·evidence + 0.3·coverage, clamped to [0, 1]."""
    raw = max(0.0, min(1.0, raw))
    evidence_factor = max(0.0, min(1.0, evidence_factor))
    coverage_factor = max(0.0, min(1.0, coverage_factor))
    return 0.4 * raw + 0.3 * evidence_factor + 0.3 * coverage_factor


def evidence_factor_from_count(supporting_nodes: int, target: int = 3) -> float:
    """min(1.0, supporting_nodes / target). Default target = 3 per §9.3."""
    if supporting_nodes <= 0:
        return 0.0
    return min(1.0, supporting_nodes / max(1, target))


def coverage_factor(relevant_nodes: int, expected_nodes: int) -> float:
    """relevant / expected, clamped. Drives the dont_know floor."""
    if expected_nodes <= 0:
        return 0.0
    return max(0.0, min(1.0, relevant_nodes / expected_nodes))


def label_for(adjusted: float, coverage: float | None = None) -> CalibrationLabel:
    """Map an adjusted score to its 5-bucket label.

    If coverage is provided AND falls below the §9.4 floor, the result is
    forced to ``dont_know`` even if the adjusted score is higher - coverage
    is the single signal that distinguishes "we don't know" from "we are
    uncertain".
    """
    if coverage is not None and coverage < _DONT_KNOW_COVERAGE_FLOOR:
        return "dont_know"
    for floor, name in _BUCKETS:
        if adjusted >= floor:
            return name
    return "dont_know"


def uncertainty_type_for(
    label: CalibrationLabel,
    coverage: float,
    has_contradictions: bool = False,
    has_relevant_subgraph: bool = True,
) -> UncertaintyType | None:
    """Reason code for the §9.4 distinction, or None for confident outputs.

    `dont_know`           → "out_of_domain" (we lack the data entirely)
    `uncertain`/`low_*`   → "data_contradictory" if contradictions present,
                            else "data_sparse"
    `confident`/`certain` → None
    """
    if label == "dont_know" or not has_relevant_subgraph or coverage < _DONT_KNOW_COVERAGE_FLOOR:
        return "out_of_domain"
    if label in ("uncertain", "low_confidence"):
        return "data_contradictory" if has_contradictions else "data_sparse"
    return None


def calibrate(
    *,
    raw: float,
    supporting_nodes: int,
    relevant_nodes: int,
    expected_nodes: int,
    has_contradictions: bool = False,
) -> CalibrationBlock:
    """End-to-end: turn raw inputs into a typed `CalibrationBlock`.

    This is what every diagnose / fix / twin caller invokes - keeps the whole
    project on a single calibration code path.
    """
    ev = evidence_factor_from_count(supporting_nodes)
    cov = coverage_factor(relevant_nodes, expected_nodes)
    adj = adjusted_confidence(raw, ev, cov)
    lbl = label_for(adj, coverage=cov)
    return CalibrationBlock(
        raw_confidence=raw,
        evidence_factor=ev,
        coverage_factor=cov,
        adjusted_confidence=adj,
        label=lbl,
    )


# Convenience reasoning string emitter (matches `CALIBRATOR_REASONING_PROMPT`
# output schema; pure-Python reference impl so callers can render without an
# extra LLM hop on hot paths).
def reasoning_string(block: CalibrationBlock, supporting_nodes: int) -> str:
    if block.label == "certain":
        return f"Certain: {supporting_nodes} supporting graph nodes consistently agree."
    if block.label == "confident":
        return f"Confident: agent outputs and merchant truths align across {supporting_nodes} nodes."
    if block.label == "uncertain":
        return f"Uncertain: {supporting_nodes} nodes cover this but conflict on outcome."
    if block.label == "low_confidence":
        return f"Low confidence: only {supporting_nodes} supporting node(s) - verify before acting."
    return "Don't know: subgraph contains no MerchantTruth covering this product."


__all__ = [
    "adjusted_confidence",
    "evidence_factor_from_count",
    "coverage_factor",
    "label_for",
    "uncertainty_type_for",
    "calibrate",
    "reasoning_string",
]
