"""Echomind Commerce - embeddings wrapper.

Convenience layer around `services.llm_service.LLMService.gemini_embed` for
text-embedding-004. Adds:
    * Trivial in-process LRU cache so identical strings are not re-embedded.
    * Batch helper that preserves input order.
    * Convenience cosine helper for ad-hoc similarity outside Neo4j.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Iterable

from services.llm_service import llm_service

logger = logging.getLogger("echomind.embeddings")


# ---------------------------------------------------------------------------
# Single-string embed with an LRU cache
# ---------------------------------------------------------------------------


@lru_cache(maxsize=4096)
def _cached_embed(text: str) -> tuple[float, ...]:
    """LRU-cached single-string embed. Returned as a tuple so it's hashable."""
    vector = llm_service.gemini_embed(text)
    return tuple(vector)


def embed_text(text: str) -> list[float]:
    """Return the 768-dim embedding for `text`.

    Uses an in-process LRU cache to avoid duplicate API calls for identical
    inputs. Returns an empty list if the input is empty.
    """
    if not text:
        return []
    return list(_cached_embed(text))


def embed_texts(texts: Iterable[str]) -> list[list[float]]:
    """Embed a list of texts, preserving order. Empty inputs yield empty vectors."""
    return [embed_text(t) for t in texts]


# ---------------------------------------------------------------------------
# Cosine similarity (ad-hoc; production uses Neo4j vector index)
# ---------------------------------------------------------------------------


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two equal-length float vectors.

    Returns 0.0 if either vector is empty or zero-norm.
    """
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for x, y in zip(a, b):
        dot += x * y
        norm_a += x * x
        norm_b += y * y
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / ((norm_a**0.5) * (norm_b**0.5))


__all__ = ["embed_text", "embed_texts", "cosine_similarity"]
