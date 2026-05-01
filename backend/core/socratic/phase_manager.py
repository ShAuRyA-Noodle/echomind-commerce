"""Echomind Commerce - Socratic interview phase manager (WINNING_PLAN §8).

Five commerce phases, advanced by statistical predicates over the live graph:

    1. Brand Mapping       - high-confidence MerchantTruths in `positioning`
    2. Product Truths      - Products with ≥1 incoming DESCRIBES from a non-
                             trivial MerchantTruth
    3. Customer Reality    - CustomerQuestion nodes with ≥1 ANSWERS edge each
    4. Policy Edge Cases   - Decisions formalized into trees + EXCEPTION_TO
                             edges per Policy
    5. Trust Signals       - TrustSignal connectivity + Pattern coverage

Triggers are conservative - better to spend a few extra questions in a phase
than to advance prematurely and miss tacit knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass

from api.schemas import SocraticPhase

PHASE_ORDER: tuple[SocraticPhase, ...] = (
    "brand_mapping",
    "product_truths",
    "customer_reality",
    "policy_edge_cases",
    "trust_signals",
)


@dataclass(frozen=True)
class GraphSnapshot:
    """A small structural snapshot of the live graph used by trigger checks.

    Fields are loose-typed dicts so the same shape can come from a Cypher
    query result or a unit-test fixture.
    """

    merchant_truths_by_category: dict[str, int]
    high_confidence_truths_by_category: dict[str, int]
    product_count: int
    products_with_describes: int
    customer_question_count: int
    customer_questions_with_answer: int
    decision_count: int
    decisions_with_tree: int
    policy_count: int
    policies_with_exceptions: int
    trust_signal_count: int
    pattern_count: int


def _phase_index(phase: SocraticPhase) -> int:
    return PHASE_ORDER.index(phase)


def _next_phase(phase: SocraticPhase) -> SocraticPhase | None:
    idx = _phase_index(phase)
    if idx + 1 >= len(PHASE_ORDER):
        return None
    return PHASE_ORDER[idx + 1]


def should_advance(phase: SocraticPhase, snap: GraphSnapshot) -> bool:
    """Return True if the current phase has met its advancement trigger."""
    if phase == "brand_mapping":
        return snap.high_confidence_truths_by_category.get("positioning", 0) >= 4

    if phase == "product_truths":
        if snap.product_count == 0:
            return False
        coverage = snap.products_with_describes / snap.product_count
        return coverage >= 0.6

    if phase == "customer_reality":
        return snap.customer_questions_with_answer >= 10

    if phase == "policy_edge_cases":
        return (
            snap.decisions_with_tree >= 3
            and snap.policy_count > 0
            and (snap.policies_with_exceptions / max(1, snap.policy_count)) >= 0.5
        )

    if phase == "trust_signals":
        return snap.trust_signal_count >= 5 and snap.pattern_count >= 2

    return False


def advance_if_ready(
    phase: SocraticPhase, snap: GraphSnapshot
) -> tuple[SocraticPhase, bool]:
    """Return (next_phase, advanced_bool). If already at last phase, stays."""
    if not should_advance(phase, snap):
        return phase, False
    nxt = _next_phase(phase)
    if nxt is None:
        return phase, False
    return nxt, True


def underrepresented_tacit_category(
    truths_by_tacit_category: dict[str, int],
) -> str | None:
    """Return the tacit category with the fewest truths captured so far.

    Returns ``None`` if every category has ≥3 truths (well-balanced graph).
    """
    expected = {
        "procedural",
        "conditional_heuristic",
        "experiential_pattern",
        "intuitive_judgment",
        "edge_case_knowledge",
        "meta_knowledge",
    }
    counts = {k: truths_by_tacit_category.get(k, 0) for k in expected}
    if all(c >= 3 for c in counts.values()):
        return None
    return min(counts, key=counts.get)  # type: ignore[arg-type]


__all__ = [
    "PHASE_ORDER",
    "GraphSnapshot",
    "should_advance",
    "advance_if_ready",
    "underrepresented_tacit_category",
]
