"""Echomind Commerce - `/api/graph/*` endpoints (graph viz + search).

Endpoints (per WINNING_PLAN §5.5):
    GET    /api/graph/{store_id}
    GET    /api/graph/{store_id}/search?q=
    GET    /api/graph/{store_id}/node/{node_id}
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Query, status

from api.schemas import NotImplementedResponse

logger = logging.getLogger("echomind.api.graph")

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get(
    "/{store_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Paginated nodes + edges for a store's graph",
)
async def get_graph(store_id: str, cursor: str | None = None) -> NotImplementedResponse:
    """Final response: `{nodes, edges}` (paginated)."""
    logger.info("graph.get store_id=%s cursor=%s", store_id, cursor)
    return NotImplementedResponse(
        endpoint=f"GET /api/graph/{store_id}",
        detail="Returns a page of nodes/edges scoped to the store. Wires to graph.operations.",
    )


@router.get(
    "/{store_id}/search",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Hybrid (text + vector) search across the graph",
)
async def search_graph(
    store_id: str,
    q: str = Query(..., description="Search query string"),
) -> NotImplementedResponse:
    """Final response: `{nodes}` (top-k results)."""
    logger.info("graph.search store_id=%s q=%s", store_id, q)
    return NotImplementedResponse(
        endpoint=f"GET /api/graph/{store_id}/search",
        detail="Hybrid full-text + embedding search via graph.queries.",
    )


@router.get(
    "/{store_id}/node/{node_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Node detail panel: node + neighbors + contradictions",
)
async def get_node_detail(store_id: str, node_id: str) -> NotImplementedResponse:
    """Final response: `{node, neighbors, contradictions}`."""
    logger.info("graph.node_detail store_id=%s node_id=%s", store_id, node_id)
    return NotImplementedResponse(
        endpoint=f"GET /api/graph/{store_id}/node/{node_id}",
        detail="Returns the node, all 1-hop neighbors, and any incident CONTRADICTS edges.",
    )
