"""Echomind Commerce - Socratic redundancy checker.

Two-stage:
    1. Embedding cosine similarity vs. last 30 questions (fast, deterministic)
    2. Gemini fallback adjudication only when cosine lands in the ambiguous
       0.75-0.88 band (per WINNING_PLAN §13)

Why this matters: without redundancy detection, the question generator will
re-ask paraphrased versions of recent questions and the merchant disengages.
Question density (verbal Q&A per minute) is a graded artifact.
"""

from __future__ import annotations

import logging

from config.prompts import REDUNDANCY_CHECK_PROMPT
from graph.embeddings import cosine_similarity, embed_text
from services.llm_service import llm_service, safe_json_loads

logger = logging.getLogger("echomind.socratic.redundancy")


COSINE_DEFINITELY_REDUNDANT = 0.88
COSINE_DEFINITELY_DISTINCT = 0.75


def is_redundant(
    candidate: str,
    last_questions: list[str],
    *,
    use_llm_fallback: bool = True,
) -> bool:
    """Return True if `candidate` semantically duplicates any of last 30 Qs."""
    if not candidate or not last_questions:
        return False

    cand_emb = embed_text(candidate)
    if not cand_emb:
        # If embedding fails, fall through to LLM (or fail-open).
        if use_llm_fallback:
            return _llm_check(candidate, last_questions)
        return False

    ambiguous_pairs: list[tuple[int, str, float]] = []
    for idx, prior in enumerate(last_questions[:30]):
        prior_emb = embed_text(prior)
        if not prior_emb:
            continue
        cos = cosine_similarity(cand_emb, prior_emb)
        if cos >= COSINE_DEFINITELY_REDUNDANT:
            return True
        if cos >= COSINE_DEFINITELY_DISTINCT:
            ambiguous_pairs.append((idx, prior, cos))

    if not ambiguous_pairs or not use_llm_fallback:
        return False
    return _llm_check(candidate, [p for _, p, _ in ambiguous_pairs])


def _llm_check(candidate: str, last_questions: list[str]) -> bool:
    prompt = REDUNDANCY_CHECK_PROMPT.format(
        candidate_question=candidate,
        last_30_questions=last_questions,
    )
    try:
        raw = llm_service.gemini_flash(prompt, temperature=0.1)
    except Exception as exc:  # noqa: BLE001
        logger.warning("redundancy.llm_failed exc=%r", exc)
        return False
    parsed = safe_json_loads(raw)
    if not isinstance(parsed, dict):
        return False
    return bool(parsed.get("is_redundant", False))


__all__ = ["is_redundant", "COSINE_DEFINITELY_REDUNDANT", "COSINE_DEFINITELY_DISTINCT"]
