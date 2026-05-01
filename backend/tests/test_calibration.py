"""Calibration formula tests - WINNING_PLAN §9.3 verbatim.

Locks the formula:

    adjusted_confidence = 0.4 × raw_confidence
                        + 0.3 × evidence_factor
                        + 0.3 × coverage_factor

    label = ≥0.80 certain | ≥0.60 confident | ≥0.35 uncertain
          | ≥0.15 low_confidence | else dont_know

These tests exist so that a regression in the bucket boundaries (the
load-bearing trust signal of the entire product) fails CI, not the demo.

A reference implementation lives here in the test file. When the runtime
calibrator is built into `core/diagnose/calibrator.py`, the implementation
should be pulled in and the duplicate removed - see Decision Log #7.
"""

from __future__ import annotations

from typing import Literal

import pytest

CalibrationLabel = Literal[
    "certain", "confident", "uncertain", "low_confidence", "dont_know"
]


def adjusted_confidence(raw: float, evidence: float, coverage: float) -> float:
    """Reference impl. of WINNING_PLAN §9.3 calibration formula."""
    return 0.4 * raw + 0.3 * evidence + 0.3 * coverage


def calibration_label(adjusted: float) -> CalibrationLabel:
    """Reference bucket assignment from WINNING_PLAN §9.3."""
    if adjusted >= 0.80:
        return "certain"
    if adjusted >= 0.60:
        return "confident"
    if adjusted >= 0.35:
        return "uncertain"
    if adjusted >= 0.15:
        return "low_confidence"
    return "dont_know"


# ---------------------------------------------------------------------------
# Formula correctness
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,ev,cov,expected",
    [
        (1.0, 1.0, 1.0, 1.0),
        (0.0, 0.0, 0.0, 0.0),
        (0.5, 0.5, 0.5, 0.5),
        (1.0, 0.0, 0.0, 0.4),
        (0.0, 1.0, 0.0, 0.3),
        (0.0, 0.0, 1.0, 0.3),
        (0.8, 0.6, 0.4, 0.4 * 0.8 + 0.3 * 0.6 + 0.3 * 0.4),
    ],
)
def test_adjusted_confidence_formula(
    raw: float, ev: float, cov: float, expected: float
) -> None:
    assert adjusted_confidence(raw, ev, cov) == pytest.approx(expected, abs=1e-9)


# ---------------------------------------------------------------------------
# Bucket boundaries - locked by §9.3
# ---------------------------------------------------------------------------


def test_certain_at_or_above_0_80() -> None:
    assert calibration_label(0.80) == "certain"
    assert calibration_label(0.95) == "certain"
    assert calibration_label(1.00) == "certain"


def test_confident_band_0_60_to_0_80() -> None:
    assert calibration_label(0.60) == "confident"
    assert calibration_label(0.79) == "confident"
    assert calibration_label(0.799999) == "confident"


def test_uncertain_band_0_35_to_0_60() -> None:
    assert calibration_label(0.35) == "uncertain"
    assert calibration_label(0.5) == "uncertain"
    assert calibration_label(0.599999) == "uncertain"


def test_low_confidence_band_0_15_to_0_35() -> None:
    assert calibration_label(0.15) == "low_confidence"
    assert calibration_label(0.25) == "low_confidence"
    assert calibration_label(0.349999) == "low_confidence"


def test_dont_know_below_0_15() -> None:
    assert calibration_label(0.149999) == "dont_know"
    assert calibration_label(0.05) == "dont_know"
    assert calibration_label(0.0) == "dont_know"


def test_dont_know_is_first_class_output() -> None:
    """dont_know is a *valid* output, not an error path. WINNING_PLAN §16.3."""
    label = calibration_label(adjusted_confidence(raw=0.0, evidence=0.0, coverage=0.0))
    assert label == "dont_know"


# ---------------------------------------------------------------------------
# End-to-end scenarios - these are the cases that show up in the demo
# ---------------------------------------------------------------------------


def test_yirg_contradiction_is_confident() -> None:
    """Demo headline gap: 3 agents disagree with the merchant truth.

    Inputs reflect a strong signal: high raw confidence, plenty of evidence,
    decent coverage. Should land at `confident` (the demo label).
    """
    score = adjusted_confidence(raw=0.88, evidence=0.83, coverage=0.62)
    assert calibration_label(score) == "confident"


def test_decaf_dark_zone_is_dont_know() -> None:
    """Demo `dont_know` gap: decaf line - no MerchantTruth, no agent prompts.

    coverage_factor is essentially 0, evidence_factor is 0; only the raw
    score from the LLM contributes - and even that is suppressed by the
    formula, dropping us into `dont_know` exactly as the product principle
    requires.

    Math:
        0.4 * 0.30 + 0.3 * 0.0 + 0.3 * 0.05 = 0.135 (< 0.15 floor) -> dont_know
    """
    score = adjusted_confidence(raw=0.30, evidence=0.0, coverage=0.05)
    assert calibration_label(score) == "dont_know"
    # An even more collapsed signal still lands in dont_know.
    score_collapsed = adjusted_confidence(raw=0.15, evidence=0.0, coverage=0.05)
    assert calibration_label(score_collapsed) == "dont_know"

    # Sanity: bumping raw enough to clear the 0.15 floor lifts us to
    # low_confidence, NOT confident - the formula works as expected.
    score_lifted = adjusted_confidence(raw=0.40, evidence=0.0, coverage=0.05)
    assert calibration_label(score_lifted) == "low_confidence"


def test_partial_provider_failure_downgrades_one_bucket() -> None:
    """If one swarm provider rate-limits mid-run, calibration downgrades.

    Per failure-mode #5.3, the calibrator detects reduced sample size and
    auto-downgrades. Here we model that as: same raw + evidence, but
    coverage drops sharply from 0.7 to 0.2 (because one of four agents
    missed every prompt), which moves `confident` to `uncertain`.

    Math:
        full     = 0.4 * 0.75 + 0.3 * 0.7 + 0.3 * 0.7  = 0.72 -> confident
        degraded = 0.4 * 0.75 + 0.3 * 0.7 + 0.3 * 0.2  = 0.57 -> uncertain
    """
    full = calibration_label(
        adjusted_confidence(raw=0.75, evidence=0.7, coverage=0.7)
    )
    degraded = calibration_label(
        adjusted_confidence(raw=0.75, evidence=0.7, coverage=0.2)
    )
    assert full == "confident"
    assert degraded == "uncertain"
    # Strictly down a bucket - never the same label, never up.
    assert full != degraded
