"""Echomind Commerce - `/api/graph/*` endpoints.

Live Neo4j reads for the force-directed graph viz, the search bar, and
per-node detail panels.

Endpoints
    GET /api/graph/{store_id}                 - paginated nodes + edges (for viz)
    GET /api/graph/{store_id}/search?q=       - text search across labels
    GET /api/graph/{store_id}/node/{node_id}  - single node + 1-hop neighbors
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Query

from graph.neo4j_client import neo4j_client

logger = logging.getLogger("echomind.api.graph")
router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/{store_id}", summary="Paginated graph dump for force-directed viz")
async def get_graph(
    store_id: str,
    limit: int = Query(default=200, ge=1, le=2000),
) -> dict[str, Any]:
    """Returns up to `limit` nodes + their edges. Frontend renders via react-force-graph-2d."""
    nodes_cy = """
    MATCH (n)
    RETURN n.id AS id,
           head(labels(n)) AS type,
           coalesce(n.title, n.statement, n.name, n.question, n.text, n.id) AS label,
           coalesce(n.confidence, 1.0) AS confidence
    LIMIT $limit
    """
    edges_cy = """
    MATCH (a)-[r]->(b)
    RETURN a.id AS source,
           b.id AS target,
           type(r) AS type,
           coalesce(r.weight, 1.0) AS weight
    LIMIT $limit
    """
    nodes = await neo4j_client.run(nodes_cy, {"limit": limit})
    edges = await neo4j_client.run(edges_cy, {"limit": limit * 3})
    return {"status": "ok", "store_id": store_id, "nodes": nodes, "edges": edges}


@router.get("/{store_id}/search", summary="Text search across labels / statements / titles")
async def search_graph(
    store_id: str,
    q: str = Query(..., min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    cypher = """
    MATCH (n)
    WHERE toLower(coalesce(n.title, '')) CONTAINS toLower($q)
       OR toLower(coalesce(n.statement, '')) CONTAINS toLower($q)
       OR toLower(coalesce(n.name, '')) CONTAINS toLower($q)
       OR toLower(coalesce(n.question, '')) CONTAINS toLower($q)
       OR toLower(coalesce(n.text, '')) CONTAINS toLower($q)
    RETURN n.id AS id,
           head(labels(n)) AS type,
           coalesce(n.title, n.statement, n.name, n.question, n.text, n.id) AS label
    LIMIT $limit
    """
    rows = await neo4j_client.run(cypher, {"q": q, "limit": limit})
    return {"status": "ok", "query": q, "matches": rows}


@router.get("/{store_id}/node/{node_id}", summary="Single node + 1-hop neighbors")
async def get_node_detail(store_id: str, node_id: str) -> dict[str, Any]:
    node_cy = "MATCH (n {id: $id}) RETURN n LIMIT 1"
    neighbors_cy = """
    MATCH (n {id: $id})-[r]-(m)
    RETURN n.id AS source_id,
           m.id AS neighbor_id,
           head(labels(m)) AS neighbor_type,
           coalesce(m.title, m.statement, m.name, m.question, m.text, m.id) AS neighbor_label,
           type(r) AS rel_type,
           startNode(r).id AS rel_from,
           endNode(r).id AS rel_to
    LIMIT 50
    """
    node_rows = await neo4j_client.run(node_cy, {"id": node_id})
    neighbor_rows = await neo4j_client.run(neighbors_cy, {"id": node_id})
    return {
        "status": "ok",
        "node": node_rows[0]["n"] if node_rows else None,
        "neighbors": neighbor_rows,
    }
