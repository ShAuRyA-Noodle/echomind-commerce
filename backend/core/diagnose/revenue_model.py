"""Echomind Commerce - revenue impact model (WINNING_PLAN §18).

Parameterized estimate, not a measurement. Every parameter is exposed as a
slider in the audit UI. We emit a *range* (low / mid / high), not a point
estimate, and the calibration label of the prediction itself accompanies
every number - the §17.3 product principle of calibrated honesty applies to
predictions, not just diagnoses.

Formula::

    monthly_at_risk =
          severity (0..1)
        × surface_loss_rate
        × monthly_agent_traffic
        × baseline_AOV
        × baseline_conversion_rate

Each parameter has a default and a sensitivity multiplier (low / high) that
generates the range. Defaults are conservative industry medians; the merchant
overrides any of them in the UI.
"""

from __future__ import annotations

from dataclasses import dataclass

from api.schemas import PredictedDelta


# Industry defaults - every one is editable in the audit UI.
DEFAULT_MONTHLY_AGENT_TRAFFIC = 100  # buyer sessions referred by AI agents
DEFAULT_BASELINE_CONVERSION = 0.025  # 2.5% session-to-order conversion
DEFAULT_BASELINE_AOV = 35.0  # USD; coffee-typical
DEFAULT_SENSITIVITY_LOW = 0.7
DEFAULT_SENSITIVITY_HIGH = 1.3


@dataclass(frozen=True)
class RevenueParameters:
    """Editable parameter set for the revenue impact model."""

    monthly_agent_traffic: int = DEFAULT_MONTHLY_AGENT_TRAFFIC
    baseline_conversion: float = DEFAULT_BASELINE_CONVERSION
    baseline_aov: float = DEFAULT_BASELINE_AOV
    sensitivity_low: float = DEFAULT_SENSITIVITY_LOW
    sensitivity_high: float = DEFAULT_SENSITIVITY_HIGH


def revenue_at_risk(
    severity: float,
    surface_loss_rate: float,
    params: RevenueParameters | None = None,
) -> dict[str, float]:
    """Monthly $-at-risk for one gap, returned as a low / mid / high triple.

    Args:
        severity: gap severity in [0, 1].
        surface_loss_rate: fraction of relevant buyer prompts where agents
            fail to surface the affected product. Computed from the swarm.
        params: editable parameter set (defaults to industry medians).

    Returns:
        ``{"low": x, "mid": y, "high": z, "currency": "USD"}``
    """
    p = params or RevenueParameters()
    severity = max(0.0, min(1.0, severity))
    surface_loss_rate = max(0.0, min(1.0, surface_loss_rate))

    base = (
        severity
        * surface_loss_rate
        * p.monthly_agent_traffic
        * p.baseline_aov
        * p.baseline_conversion
    )

    return {
        "low": base * p.sensitivity_low,
        "mid": base,
        "high": base * p.sensitivity_high,
        "currency": "USD",
    }


def fix_predicted_delta(
    *,
    metric: str,
    expected_pp_low: float,
    expected_pp_high: float,
    rationale: str | None = None,
) -> PredictedDelta:
    """Build a PredictedDelta envelope for a fix's expected impact.

    `expected_pp_low` and `expected_pp_high` are in percentage points
    (e.g. 40.0 means "+40 pp surface rate"). The fix copy generator chooses
    these per gap_type heuristics; observed deltas after re-test get
    compared back to this range.
    """
    low = max(0.0, expected_pp_low)
    high = max(low, expected_pp_high)
    return PredictedDelta(
        low=low,
        high=high,
        metric=metric,
        rationale=rationale,
    )


__all__ = [
    "RevenueParameters",
    "revenue_at_risk",
    "fix_predicted_delta",
    "DEFAULT_MONTHLY_AGENT_TRAFFIC",
    "DEFAULT_BASELINE_CONVERSION",
    "DEFAULT_BASELINE_AOV",
]
