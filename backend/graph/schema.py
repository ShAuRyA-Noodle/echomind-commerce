"""Echomind Commerce - Neo4j schema bootstrap script (constraints + indexes).

This module is the single source of truth for all Neo4j DDL. Running every
statement in `SCHEMA_INIT_QUERIES` against an AuraDB Free instance is
idempotent (every statement uses `IF NOT EXISTS`) and produces a graph with:

    * Uniqueness constraints on `id` for every node type in §6.1
    * Property indexes for hot lookup fields (e.g. `Product.shopify_gid`,
      `MerchantTruth.tacit_level`, `Gap.severity`)
    * VECTOR indexes for the four node types that carry an `embedding` field
      (Product, MerchantTruth, CustomerQuestion, BuyerPrompt)

Vector indexes assume Neo4j 5.13+ syntax and 768-dim vectors from
text-embedding-004. We use cosine similarity throughout.

Usage::

    from graph.schema import SCHEMA_INIT_QUERIES
    for q in SCHEMA_INIT_QUERIES:
        await client.run(q)
"""

from __future__ import annotations

from typing import Final

# Embedding dimensionality for `text-embedding-004`.
EMBEDDING_DIM: Final[int] = 768
SIMILARITY_FUNCTION: Final[str] = "cosine"

# All 11 node types from WINNING_PLAN §6.1.
NODE_TYPES: Final[tuple[str, ...]] = (
    "Product",
    "Policy",
    "TrustSignal",
    "MerchantTruth",
    "Decision",
    "Pattern",
    "CustomerQuestion",
    "BuyerPrompt",
    "AgentRepresentation",
    "Gap",
    "FixSuggestion",
)

# Node types that carry an `embedding` (768d) property.
EMBEDDING_NODE_TYPES: Final[tuple[str, ...]] = (
    "Product",
    "MerchantTruth",
    "CustomerQuestion",
    "BuyerPrompt",
)


def _uniqueness(label: str, prop: str = "id") -> str:
    return (
        f"CREATE CONSTRAINT {label.lower()}_{prop}_unique IF NOT EXISTS "
        f"FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
    )


def _index(label: str, prop: str) -> str:
    return (
        f"CREATE INDEX {label.lower()}_{prop}_idx IF NOT EXISTS "
        f"FOR (n:{label}) ON (n.{prop})"
    )


def _vector_index(label: str, prop: str = "embedding") -> str:
    return (
        f"CREATE VECTOR INDEX {label.lower()}_{prop}_vec IF NOT EXISTS "
        f"FOR (n:{label}) ON (n.{prop}) "
        f"OPTIONS {{ indexConfig: {{ "
        f"`vector.dimensions`: {EMBEDDING_DIM}, "
        f"`vector.similarity_function`: '{SIMILARITY_FUNCTION}' "
        f"}} }}"
    )


# ---------------------------------------------------------------------------
# SCHEMA_INIT_QUERIES - list of Cypher statements, executed in order.
# ---------------------------------------------------------------------------

SCHEMA_INIT_QUERIES: Final[list[str]] = [
    # 1) Uniqueness on id for every node type.
    *[_uniqueness(label) for label in NODE_TYPES],
    # 2) Hot lookup indexes per node type.
    _index("Product", "shopify_gid"),
    _index("Product", "title"),
    _index("Policy", "type"),
    _index("TrustSignal", "type"),
    _index("MerchantTruth", "tacit_level"),
    _index("MerchantTruth", "category"),
    _index("Decision", "frequency"),
    _index("Pattern", "name"),
    _index("CustomerQuestion", "intent_class"),
    _index("BuyerPrompt", "intent_class"),
    _index("AgentRepresentation", "agent_model"),
    _index("AgentRepresentation", "captured_at"),
    _index("Gap", "type"),
    _index("Gap", "severity"),
    _index("Gap", "calibration_label"),
    _index("FixSuggestion", "fix_type"),
    _index("FixSuggestion", "applied"),
    # 3) Vector indexes for embedding-bearing node types.
    *[_vector_index(label) for label in EMBEDDING_NODE_TYPES],
]


# Edge property indexes - created lazily, kept here so the file is also
# the *complete* DDL story.
EDGE_INDEX_QUERIES: Final[list[str]] = [
    "CREATE INDEX contradicts_resolution_idx IF NOT EXISTS "
    "FOR ()-[r:CONTRADICTS]-() ON (r.resolution)",
    "CREATE INDEX similar_to_score_idx IF NOT EXISTS "
    "FOR ()-[r:SIMILAR_TO]-() ON (r.embedding_similarity)",
]


# Convenience: callers can splice both lists together.
ALL_INIT_QUERIES: Final[list[str]] = [*SCHEMA_INIT_QUERIES, *EDGE_INDEX_QUERIES]


__all__ = [
    "EMBEDDING_DIM",
    "SIMILARITY_FUNCTION",
    "NODE_TYPES",
    "EMBEDDING_NODE_TYPES",
    "SCHEMA_INIT_QUERIES",
    "EDGE_INDEX_QUERIES",
    "ALL_INIT_QUERIES",
]
