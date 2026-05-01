"""Echomind Commerce - gap classification judge (Gemini Pro).

Takes a `GapCandidate` from `cypher_diff.py`, runs `GAP_JUDGE_PROMPT` from
`prompts.py`, validates the JSON output, and returns a typed `Gap` node
ready for upsert. Calibration runs through `calibrator.calibrate(...)`.

The judge is the LLM half of the AI/deterministic boundary in §5.4 - it
does NLP classification (omission / contradiction / ambiguity / hallucination
/ dark_zone). It does NOT do math; that's the calibrator + revenue model.
"""

from __future__ import annotations

import logging
from typing import Any

from api.schemas import Gap
from config.prompts import GAP_JUDGE_PROMPT
from core.diagnose import calibrator, revenue_model
from core.diagnose.cypher_diff import GapCandidate
from graph.operations import deterministic_id
from services.llm_service import llm_service, safe_json_loads

logger = logging.getLogger("echomind.diagnose.judge")


async def classify_candidate(
    candidate: GapCandidate,
    *,
    triggering_prompts: list[str] | None = None,
    revenue_params: revenue_model.RevenueParameters | None = None,
    surface_loss_rate: float = 0.5,
    expected_relevant_nodes: int = 5,
) -> Gap:
    """Run the gap judge over a candidate, calibrate, return a typed Gap.

    Args:
        candidate: pre-filtered candidate from a Cypher diff query.
        triggering_prompts: optional buyer-prompt text list for context.
        revenue_params: editable parameter set for the revenue model.
        surface_loss_rate: fraction of relevant prompts where agents miss
            the affected product. The diagnose orchestrator computes this
            from the swarm and passes it in.
        expected_relevant_nodes: denominator for coverage_factor (typical 5).
    """
    prompt = GAP_JUDGE_PROMPT.format(
        affected_products=candidate.affected_products,
        merchant_side_evidence=candidate.merchant_evidence,
        agent_side_evidence=candidate.agent_evidence,
        triggering_prompts=triggering_prompts or [],
    )

    raw = ""
    parsed: dict[str, Any] | None = None
    try:
        raw = llm_service.gemini_pro(prompt)
        loaded = safe_json_loads(raw)
        if isinstance(loaded, dict):
            parsed = loaded
    except Exception as exc:  # noqa: BLE001 - judge failures must not crash diagnose
        logger.exception("judge.failed exc=%r", exc)
        parsed = None

    # Default to the pre-filter's candidate type if the judge can't classify.
    gap_type = candidate.candidate_type
    severity = 0.5
    raw_conf = 0.4
    supporting_nodes = max(1, len(candidate.affected_products))
    relevant_nodes = supporting_nodes
    reasoning_chain_text = ""

    if parsed:
        gap_type = parsed.get("type", gap_type)  # type: ignore[assignment]
        severity = float(parsed.get("severity", severity) or severity)
        ci = parsed.get("calibration_inputs") or {}
        raw_conf = float(ci.get("raw_confidence", raw_conf) or raw_conf)
        supporting_nodes = int(ci.get("supporting_nodes_count", supporting_nodes) or supporting_nodes)
        coverage_in = float(ci.get("coverage_factor", 0.0) or 0.0)
        relevant_nodes = max(1, int(round(coverage_in * expected_relevant_nodes)))
        chain = parsed.get("reasoning_chain") or []
        if isinstance(chain, list):
            reasoning_chain_text = " | ".join(
                f"step {s.get('step')}: {s.get('claim')}" for s in chain if isinstance(s, dict)
            )

    # Calibration formula (§9.3) - single source of truth.
    block = calibrator.calibrate(
        raw=raw_conf,
        supporting_nodes=supporting_nodes,
        relevant_nodes=relevant_nodes,
        expected_nodes=expected_relevant_nodes,
        has_contradictions=(gap_type == "contradiction"),
    )
    uncertainty = calibrator.uncertainty_type_for(
        block.label,
        block.coverage_factor,
        has_contradictions=(gap_type == "contradiction"),
        has_relevant_subgraph=relevant_nodes > 0,
    )

    # Revenue impact - parameterized estimate, not a measurement.
    revenue_band = revenue_model.revenue_at_risk(
        severity=severity,
        surface_loss_rate=surface_loss_rate,
        params=revenue_params,
    )

    affected_product_ids = [
        p.get("id", "") for p in candidate.affected_products if isinstance(p, dict)
    ]
    gap_id = deterministic_id(
        "gap",
        gap_type,
        *(pid for pid in affected_product_ids if pid),
        str(candidate.raw_row.get("agent_id", "")),
    )
    return Gap(
        id=gap_id,
        type=gap_type,
        severity=max(0.0, min(1.0, severity)),
        revenue_impact_usd_monthly=revenue_band["mid"],
        calibration_label=block.label,
        uncertainty_type=uncertainty,
        reasoning_chain=reasoning_chain_text or None,
        affected_products=affected_product_ids,
    )


async def classify_all(
    candidates: list[GapCandidate],
    *,
    revenue_params: revenue_model.RevenueParameters | None = None,
    surface_loss_rate: float = 0.5,
) -> list[Gap]:
    """Classify a batch of candidates in sequence (judge calls are not free)."""
    out: list[Gap] = []
    for c in candidates:
        gap = await classify_candidate(
            c, revenue_params=revenue_params, surface_loss_rate=surface_loss_rate
        )
        out.append(gap)
    return out


__all__ = ["classify_candidate", "classify_all"]
