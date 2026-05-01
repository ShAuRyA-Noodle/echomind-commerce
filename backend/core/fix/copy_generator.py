"""Echomind Commerce - fix copy generator (WINNING_PLAN §17).

Takes a `Gap`, retrieves its 4-strategy subgraph, samples merchant voice
from interview transcripts, and asks Gemini Pro to draft a `FixSuggestion`
in the merchant's own voice.

Hard rules from `prompts.py::FIX_COPY_GENERATION_PROMPT`:
    * Proposed text must be derivable entirely from the retrieved subgraph.
    * If subgraph is too thin, return null + uncertainty_notes - do NOT
      improvise content.
    * Predicted delta range is honest (range, not point estimate).
    * Reasoning chain cites specific source node ids.
"""

from __future__ import annotations

import logging
from typing import Any

from api.schemas import FixSuggestion, FixType, Gap, PredictedDelta
from config.prompts import FIX_COPY_GENERATION_PROMPT
from core.diagnose import calibrator
from graph.operations import deterministic_id
from services.llm_service import llm_service, safe_json_loads

logger = logging.getLogger("echomind.fix.copy_generator")


# Default predicted-delta band per gap type (percentage points).
# These are the priors we send into the prompt; Gemini Pro can override.
_DEFAULT_DELTA_BAND: dict[str, tuple[float, float]] = {
    "omission": (30.0, 60.0),
    "contradiction": (40.0, 75.0),
    "ambiguity": (15.0, 35.0),
    "hallucination": (5.0, 20.0),
    "dark_zone": (20.0, 50.0),
}


def _default_fix_type_for(gap_type: str) -> FixType:
    return {
        "omission": "copy_rewrite",
        "contradiction": "copy_rewrite",
        "ambiguity": "copy_rewrite",
        "hallucination": "policy_clarify",
        "dark_zone": "faq_add",
    }.get(gap_type, "copy_rewrite")  # type: ignore[return-value]


async def generate_fix(
    *,
    gap: Gap,
    subgraph_direct: list[dict[str, Any]],
    subgraph_semantic: list[dict[str, Any]],
    subgraph_decisions: list[dict[str, Any]],
    subgraph_contradictions: list[dict[str, Any]],
    merchant_voice_samples: list[str],
    fix_type: FixType | None = None,
) -> FixSuggestion:
    """Generate a typed FixSuggestion ready for upsert + apply."""
    chosen_fix_type = fix_type or _default_fix_type_for(gap.type)
    prompt = FIX_COPY_GENERATION_PROMPT.format(
        gap_type=gap.type,
        gap_severity=gap.severity,
        gap_affected_products=gap.affected_products,
        gap_reasoning_chain=gap.reasoning_chain or "",
        fix_type=chosen_fix_type,
        subgraph_direct=subgraph_direct,
        subgraph_semantic=subgraph_semantic,
        subgraph_decisions=subgraph_decisions,
        subgraph_contradictions=subgraph_contradictions,
        merchant_voice_samples=merchant_voice_samples,
    )
    raw = ""
    parsed: dict[str, Any] | None = None
    try:
        raw = llm_service.gemini_pro(prompt, temperature=0.5)
        loaded = safe_json_loads(raw)
        if isinstance(loaded, dict):
            parsed = loaded
    except Exception as exc:  # noqa: BLE001
        logger.exception("fix.copy_gen.failed exc=%r", exc)

    proposed_text: str | None = None
    voice_match_notes: str | None = None
    pdr: PredictedDelta | None = None

    if parsed:
        proposed_text = parsed.get("proposed_text")
        voice_match_notes = parsed.get("voice_match_notes")
        pred = parsed.get("predicted_delta_range") or {}
        if isinstance(pred, dict) and pred.get("low") is not None and pred.get("high") is not None:
            pdr = PredictedDelta(
                low=float(pred.get("low", 0.0)),
                high=float(pred.get("high", 0.0)),
                metric=str(pred.get("metric", "agent_surface_rate_pp")),
                rationale=pred.get("rationale"),
            )

    # Fall back to default delta band if Gemini didn't supply one.
    if pdr is None:
        low, high = _DEFAULT_DELTA_BAND.get(gap.type, (10.0, 30.0))
        pdr = PredictedDelta(
            low=low,
            high=high,
            metric="agent_surface_rate_pp",
            rationale="Default band per gap_type; replace with measured delta after re-test.",
        )

    fix_id = deterministic_id("fix", gap.id, chosen_fix_type)
    return FixSuggestion(
        id=fix_id,
        gap_id=gap.id,
        fix_type=chosen_fix_type,
        proposed_text=proposed_text or "",
        applied=False,
        predicted_delta_range=pdr,
        voice_match_notes=voice_match_notes,
    )


__all__ = ["generate_fix"]
