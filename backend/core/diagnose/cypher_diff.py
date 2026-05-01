"""Echomind Commerce - Cypher gap-candidate detection (WINNING_PLAN §16.2).

Runs the five named candidate queries from `graph/queries.py`, normalizes
the rows into a uniform `GapCandidate` shape, and hands them to
`core/diagnose/judge.py` for LLM classification.

This module is pure-deterministic - no LLM calls. The Cypher predicates are
intentionally permissive (broad recall); the LLM judge handles precision.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from api.schemas import GapType
from graph import queries as Q
from graph.neo4j_client import neo4j_client

logger = logging.getLogger("echomind.diagnose.cypher_diff")


@dataclass
class GapCandidate:
    """Uniform shape over all five candidate query outputs."""

    candidate_type: GapType  # what the Cypher pre-filter thinks it is
    affected_products: list[dict[str, Any]] = field(default_factory=list)
    merchant_evidence: list[dict[str, Any]] = field(default_factory=list)
    agent_evidence: list[dict[str, Any]] = field(default_factory=list)
    raw_row: dict[str, Any] = field(default_factory=dict)


async def find_omission_candidates() -> list[GapCandidate]:
    rows = await neo4j_client.run(Q.CANDIDATE_OMISSION, {})
    out: list[GapCandidate] = []
    for r in rows:
        out.append(
            GapCandidate(
                candidate_type="omission",
                affected_products=[{"id": r["product_id"], "title": r["title"]}],
                merchant_evidence=[
                    {"truth_count": r["truth_count"], "mention_count": r["mention_count"]}
                ],
                raw_row=r,
            )
        )
    return out


async def find_contradiction_candidates() -> list[GapCandidate]:
    rows = await neo4j_client.run(Q.CANDIDATE_CONTRADICTION, {})
    return [
        GapCandidate(
            candidate_type="contradiction",
            affected_products=[{"id": r["product_id"], "title": r["title"]}],
            merchant_evidence=[{"truth_id": r["truth_id"], "statement": r["truth"]}],
            agent_evidence=[
                {
                    "agent_id": r["agent_id"],
                    "agent_model": r["agent_model"],
                    "text": r["agent_text"],
                }
            ],
            raw_row=r,
        )
        for r in rows
    ]


async def find_ambiguity_candidates() -> list[GapCandidate]:
    rows = await neo4j_client.run(Q.CANDIDATE_AMBIGUITY, {})
    return [
        GapCandidate(
            candidate_type="ambiguity",
            affected_products=[{"id": r["product_id"], "title": r["title"]}],
            agent_evidence=[
                {"agents": r["agents"], "texts": r["texts"]}
            ],
            raw_row=r,
        )
        for r in rows
    ]


async def find_hallucination_candidates() -> list[GapCandidate]:
    rows = await neo4j_client.run(Q.CANDIDATE_HALLUCINATION, {})
    return [
        GapCandidate(
            candidate_type="hallucination",
            agent_evidence=[
                {
                    "agent_id": r["agent_id"],
                    "agent_model": r["agent_model"],
                    "hallucinated_title": r["hallucinated_title"],
                    "text": r["agent_text"],
                }
            ],
            raw_row=r,
        )
        for r in rows
    ]


async def find_dark_zone_candidates() -> list[GapCandidate]:
    rows = await neo4j_client.run(Q.CANDIDATE_DARK_ZONE, {})
    return [
        GapCandidate(
            candidate_type="dark_zone",
            affected_products=[{"id": pid, "title": ""} for pid in r["product_ids"]],
            raw_row=r,
        )
        for r in rows
    ]


async def find_all_candidates() -> dict[GapType, list[GapCandidate]]:
    """One-shot: run all 5 candidate queries and return them grouped by type."""
    omissions = await find_omission_candidates()
    contradictions = await find_contradiction_candidates()
    ambiguities = await find_ambiguity_candidates()
    hallucinations = await find_hallucination_candidates()
    dark_zones = await find_dark_zone_candidates()
    out: dict[GapType, list[GapCandidate]] = {
        "omission": omissions,
        "contradiction": contradictions,
        "ambiguity": ambiguities,
        "hallucination": hallucinations,
        "dark_zone": dark_zones,
    }
    logger.info(
        "diagnose.candidates omission=%d contradiction=%d ambiguity=%d "
        "hallucination=%d dark_zone=%d",
        len(omissions),
        len(contradictions),
        len(ambiguities),
        len(hallucinations),
        len(dark_zones),
    )
    return out


__all__ = [
    "GapCandidate",
    "find_omission_candidates",
    "find_contradiction_candidates",
    "find_ambiguity_candidates",
    "find_hallucination_candidates",
    "find_dark_zone_candidates",
    "find_all_candidates",
]
