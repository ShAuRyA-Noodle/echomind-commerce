"""Echomind Commerce - Socratic next-question generator.

Wraps `SOCRATIC_QUESTION_GENERATION_PROMPT`. Inputs come from the engine:
phase, graph stats, top-3 frontiers, recent Q&A, underrepresented tacit
category. Output is one question + a follow-up + structured metadata for
the audit log.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from api.schemas import SocraticPhase
from config.prompts import SOCRATIC_QUESTION_GENERATION_PROMPT
from services.llm_service import llm_service, safe_json_loads

logger = logging.getLogger("echomind.socratic.question_gen")


@dataclass
class GeneratedQuestion:
    """One next-question result, surfaced to UI + audit log."""

    question: str | None
    follow_up_if_brief: str | None = None
    targets_frontier_id: str | None = None
    targets_tacit_category: str | None = None
    phase_style_used: int | None = None
    rationale: str | None = None
    uncertainty_notes: str | None = None
    raw_text: str = ""


def generate_question(
    *,
    phase: SocraticPhase,
    question_count: int,
    elapsed_minutes: float,
    domain: str,
    graph_stats: dict[str, Any],
    top_3_frontiers: list[dict[str, Any]],
    last_5_qa_pairs: list[dict[str, str]],
    underrepresented_tacit_category: str | None,
) -> GeneratedQuestion:
    prompt = SOCRATIC_QUESTION_GENERATION_PROMPT.format(
        phase=phase,
        question_count=question_count,
        elapsed_minutes=round(elapsed_minutes, 1),
        domain=domain,
        graph_stats=graph_stats,
        top_3_frontiers=top_3_frontiers,
        last_5_qa_pairs=last_5_qa_pairs,
        underrepresented_tacit_category=underrepresented_tacit_category or "balanced",
    )
    raw = ""
    try:
        raw = llm_service.gemini_flash(prompt, temperature=0.7)
    except Exception as exc:  # noqa: BLE001
        logger.exception("question_gen.failed exc=%r", exc)
        return GeneratedQuestion(question=None, raw_text=raw, uncertainty_notes=repr(exc))

    parsed = safe_json_loads(raw)
    if not isinstance(parsed, dict):
        return GeneratedQuestion(
            question=None, raw_text=raw, uncertainty_notes="parse_failed"
        )
    return GeneratedQuestion(
        question=parsed.get("question"),
        follow_up_if_brief=parsed.get("follow_up_if_brief"),
        targets_frontier_id=parsed.get("targets_frontier_id"),
        targets_tacit_category=parsed.get("targets_tacit_category"),
        phase_style_used=parsed.get("phase_style_used"),
        rationale=parsed.get("rationale"),
        uncertainty_notes=parsed.get("uncertainty_notes"),
        raw_text=raw,
    )


__all__ = ["GeneratedQuestion", "generate_question"]
