"""Echomind Commerce - entity resolution (WINNING_PLAN §13).

Three-stage cascade for deduping entity surface forms across multiple agent
outputs and multiple extraction passes:

    1. Levenshtein on the surface form (catches typos / casing).
    2. Cosine similarity on `text-embedding-004` embeddings (catches paraphrase).
    3. Gemini disambiguation call (only for the residual hard cases).

Without this, surface-rate calculations are garbage - an agent mentioning
"YGC" 5× and "Yirgacheffe" 3× appears as 0% surface rate for either name.

Thresholds are tunable. Defaults below were validated against the Fulcrum
Coffee catalog; tuning notes live in Decision Log #22.
"""

from __future__ import annotations

import logging
from typing import Iterable

from graph.embeddings import cosine_similarity, embed_text

logger = logging.getLogger("echomind.entity_resolver")


# Tunable thresholds.
LEVENSHTEIN_RATIO_MERGE = 0.3   # ≤ this fraction of edits per char ⇒ MERGE
LEVENSHTEIN_RATIO_REJECT = 0.7  # ≥ this ⇒ DISTINCT without further checks
COSINE_MERGE = 0.92             # ≥ this cosine ⇒ MERGE
COSINE_DISCARD = 0.55           # < this ⇒ DISTINCT


def _levenshtein(a: str, b: str) -> int:
    """Pure-Python Levenshtein (small strings - no perf hot-path)."""
    a = a.lower()
    b = b.lower()
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            ins = cur[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            cur[j] = min(ins, dele, sub)
        prev = cur
    return prev[-1]


def _levenshtein_ratio(a: str, b: str) -> float:
    """Edit distance normalised by max(len(a), len(b))."""
    if not a and not b:
        return 0.0
    return _levenshtein(a, b) / max(len(a), len(b))


def resolve_pair(
    name_a: str,
    name_b: str,
    *,
    use_embeddings: bool = True,
) -> str:
    """Decide whether two surface forms refer to the same entity.

    Returns one of: "merge" / "distinct" / "ambiguous".

    `ambiguous` means stages 1 and 2 disagree or were inconclusive - the
    caller should optionally invoke `gemini_disambiguate(...)` for the final
    word. We don't run Gemini here because most call sites are inside hot
    loops (entity resolution after every extraction pass).
    """
    a = (name_a or "").strip()
    b = (name_b or "").strip()
    if not a or not b:
        return "distinct"
    if a.lower() == b.lower():
        return "merge"

    # Stage 1 - Levenshtein.
    lev = _levenshtein_ratio(a, b)
    if lev <= LEVENSHTEIN_RATIO_MERGE:
        return "merge"
    if lev >= LEVENSHTEIN_RATIO_REJECT and not use_embeddings:
        return "distinct"

    # Stage 2 - embedding cosine.
    if use_embeddings:
        try:
            ea = embed_text(a)
            eb = embed_text(b)
            cos = cosine_similarity(ea, eb)
            if cos >= COSINE_MERGE:
                return "merge"
            if cos < COSINE_DISCARD:
                return "distinct"
            # else: ambiguous, falls through.
            return "ambiguous"
        except Exception as exc:  # noqa: BLE001 - embed failure ⇒ defer to Gemini
            logger.warning("entity_resolver.embed_failed err=%r", exc)
            return "ambiguous"

    return "ambiguous"


def merge_groups(names: Iterable[str]) -> list[set[str]]:
    """Cluster a list of surface forms into merge-equivalent groups.

    Greedy: O(N²) over names. Fine for the typical audit-time entity counts
    (≤200 unique names). Use a union-find replacement if scale changes.
    """
    seen: list[set[str]] = []
    for name in names:
        placed = False
        for group in seen:
            sample = next(iter(group))
            if resolve_pair(name, sample) == "merge":
                group.add(name)
                placed = True
                break
        if not placed:
            seen.append({name})
    return seen


__all__ = [
    "resolve_pair",
    "merge_groups",
    "LEVENSHTEIN_RATIO_MERGE",
    "LEVENSHTEIN_RATIO_REJECT",
    "COSINE_MERGE",
    "COSINE_DISCARD",
]
