"""Echomind Commerce - graph CRUD operations.

Two surfaces in one module:

    * Class-based ``GraphOperations`` - generic, dict-based, for endpoints
      that don't yet have typed pydantic objects.
    * Free-function API (``upsert_product(p)`` etc.) - typed, used by the
      Socratic engine, swarm runner, and diagnose pipeline. These take
      pydantic models and write through named Cypher in `queries.py`.

Both APIs share the same `Neo4jClient` singleton.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any

from .neo4j_client import Neo4jClient, neo4j_client

logger = logging.getLogger("echomind.graph.ops")


# ---------------------------------------------------------------------------
# Free-function API - typed, used by core/* modules
# ---------------------------------------------------------------------------


def deterministic_id(prefix: str, *parts: str) -> str:
    """Stable, idempotent ID derived from a content hash.

    `prefix` controls grouping (e.g. "prod", "truth", "gap"); `parts` carry
    the entity-identifying content. Re-applying the same parts always yields
    the same id - perfect for MERGE.
    """
    raw = "|".join(p or "" for p in parts).encode("utf-8")
    digest = hashlib.sha1(raw).hexdigest()[:16]
    return f"{prefix}_{digest}"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


async def upsert_product_typed(p: Any) -> str:
    """Typed Product upsert. Imports queries lazily to avoid circular import."""
    from . import queries as Q

    await neo4j_client.run(
        Q.UPSERT_PRODUCT,
        {
            "id": p.id,
            "shopify_gid": getattr(p, "shopify_gid", None),
            "title": p.title,
            "description": getattr(p, "description", None),
            "price": getattr(p, "price", None),
            "currency": getattr(p, "currency", None),
            "image_urls": getattr(p, "image_urls", []),
            "tags": getattr(p, "tags", []),
            "variants_summary": getattr(p, "variants_summary", None),
            "ingested_at": (getattr(p, "ingested_at", None) or datetime.now(timezone.utc)).isoformat(),
        },
    )
    return p.id


async def upsert_typed(node: Any, label: str) -> str:
    """Generic typed upsert: takes a pydantic model + label, MERGEs by id."""
    cypher = (
        f"MERGE (n:{label} {{id: $id}}) SET n += $props RETURN n.id AS id"
    )
    props = node.model_dump() if hasattr(node, "model_dump") else dict(node)
    nid = props.pop("id", None)
    await neo4j_client.run(cypher, {"id": nid, "props": props})
    return nid


async def upsert_edge_typed(
    rel_type: str,
    from_id: str,
    to_id: str,
    props: dict[str, Any] | None = None,
) -> None:
    """Generic typed edge upsert. `rel_type` must be a valid EdgeType."""
    cypher = (
        f"MATCH (a {{id: $from_id}}), (b {{id: $to_id}}) "
        f"MERGE (a)-[r:{rel_type}]->(b) "
        "SET r += $props RETURN type(r) AS rel"
    )
    await neo4j_client.run(
        cypher,
        {"from_id": from_id, "to_id": to_id, "props": props or {}},
    )


async def graph_stats() -> dict[str, Any]:
    """Per-type node + edge counts for the audit dashboard."""
    from . import queries as Q

    nodes = await neo4j_client.run(Q.GRAPH_NODE_COUNTS, {})
    edges = await neo4j_client.run(Q.GRAPH_EDGE_COUNTS, {})
    return {
        "nodes": {row["label"]: row["c"] for row in nodes if row.get("label")},
        "edges": {row["rel"]: row["c"] for row in edges if row.get("rel")},
    }


# Compat aliases for callers expecting the snake_case typed names.
upsert_product = upsert_product_typed


class GraphOperations:
    """Domain-level Neo4j read/write helpers."""

    def __init__(self, client: Neo4jClient | None = None) -> None:
        self.client = client or neo4j_client

    # ------------------------------------------------------------------
    # Generic upsert helpers (used by the typed methods below)
    # ------------------------------------------------------------------

    async def upsert_node(
        self,
        label: str,
        node_id: str,
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """MERGE a node by id and SET the supplied properties.

        Returns the post-merge node as a plain dict.
        """
        cypher = (
            f"MERGE (n:{label} {{id: $id}}) "
            "SET n += $props "
            "RETURN n"
        )
        records = await self.client.run(cypher, {"id": node_id, "props": properties})
        return records[0]["n"] if records else {}

    async def upsert_edge(
        self,
        from_label: str,
        from_id: str,
        edge_type: str,
        to_label: str,
        to_id: str,
        properties: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """MERGE an edge between two nodes and SET edge properties.

        Returns a small dict describing the edge.
        """
        cypher = (
            f"MATCH (a:{from_label} {{id: $from_id}}), (b:{to_label} {{id: $to_id}}) "
            f"MERGE (a)-[r:{edge_type}]->(b) "
            "SET r += $props "
            "RETURN type(r) AS type, properties(r) AS props"
        )
        records = await self.client.run(
            cypher,
            {"from_id": from_id, "to_id": to_id, "props": properties or {}},
        )
        return records[0] if records else {}

    # ------------------------------------------------------------------
    # Typed convenience wrappers (one per node type from §6.1)
    # ------------------------------------------------------------------

    async def upsert_product(self, product: dict[str, Any]) -> dict[str, Any]:
        """Create/update a Product node. Expects a dict shaped like `Product` (api/schemas.py)."""
        return await self.upsert_node("Product", product["id"], product)

    async def upsert_policy(self, policy: dict[str, Any]) -> dict[str, Any]:
        return await self.upsert_node("Policy", policy["id"], policy)

    async def upsert_trust_signal(self, trust_signal: dict[str, Any]) -> dict[str, Any]:
        return await self.upsert_node("TrustSignal", trust_signal["id"], trust_signal)

    async def upsert_merchant_truth(self, truth: dict[str, Any]) -> dict[str, Any]:
        return await self.upsert_node("MerchantTruth", truth["id"], truth)

    async def upsert_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        return await self.upsert_node("Decision", decision["id"], decision)

    async def upsert_pattern(self, pattern: dict[str, Any]) -> dict[str, Any]:
        return await self.upsert_node("Pattern", pattern["id"], pattern)

    async def upsert_customer_question(self, q: dict[str, Any]) -> dict[str, Any]:
        return await self.upsert_node("CustomerQuestion", q["id"], q)

    async def upsert_buyer_prompt(self, bp: dict[str, Any]) -> dict[str, Any]:
        return await self.upsert_node("BuyerPrompt", bp["id"], bp)

    async def upsert_agent_representation(self, rep: dict[str, Any]) -> dict[str, Any]:
        return await self.upsert_node("AgentRepresentation", rep["id"], rep)

    async def upsert_gap(self, gap: dict[str, Any]) -> dict[str, Any]:
        return await self.upsert_node("Gap", gap["id"], gap)

    async def upsert_fix_suggestion(self, fix: dict[str, Any]) -> dict[str, Any]:
        return await self.upsert_node("FixSuggestion", fix["id"], fix)

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    async def get_node(self, label: str, node_id: str) -> dict[str, Any] | None:
        cypher = f"MATCH (n:{label} {{id: $id}}) RETURN n LIMIT 1"
        records = await self.client.run(cypher, {"id": node_id})
        return records[0]["n"] if records else None

    async def neighbors(
        self,
        label: str,
        node_id: str,
        depth: int = 1,
    ) -> list[dict[str, Any]]:
        """Return immediate (or up-to-depth) neighbors of a node."""
        cypher = (
            f"MATCH (n:{label} {{id: $id}})-[r*1..{depth}]-(m) "
            "RETURN DISTINCT m, r"
        )
        return await self.client.run(cypher, {"id": node_id})

    async def count_by_label(self) -> dict[str, int]:
        """Return {label: count} for every label present in the graph."""
        from .queries import NODE_COUNTS_BY_LABEL

        records = await self.client.run(NODE_COUNTS_BY_LABEL)
        return {row["label"]: int(row["count"]) for row in records}


# Module-level singleton bound to the default Neo4jClient.
graph_ops = GraphOperations()
