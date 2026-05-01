"""Echomind Commerce - `/api/simulate/*` endpoints (agent swarm).

Endpoints (per WINNING_PLAN §5.5):
    POST   /api/simulate/run
    WS     /api/simulate/ws/{run_id}     (mounted on the app)
    GET    /api/simulate/{run_id}
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, status

from api.schemas import NotImplementedResponse

logger = logging.getLogger("echomind.api.simulate")

router = APIRouter(prefix="/simulate", tags=["simulate"])


@router.post(
    "/run",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Kick off an agent-swarm simulation run",
)
async def run_simulation(payload: dict[str, Any] | None = None) -> NotImplementedResponse:
    """Final response: `{run_id, prompt_count, agent_count}`."""
    logger.info("simulate.run payload=%s", payload)
    return NotImplementedResponse(
        endpoint="POST /api/simulate/run",
        detail="Generates BuyerPrompts, fans out to all 4 agents, persists AgentRepresentations.",
    )


@router.get(
    "/{run_id}",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    response_model=NotImplementedResponse,
    summary="Get simulation results for a run",
)
async def get_simulation(run_id: str) -> NotImplementedResponse:
    """Final response: `{agents: [{model, prompts, responses, surface_rates}]}`."""
    logger.info("simulate.get run_id=%s", run_id)
    return NotImplementedResponse(
        endpoint=f"GET /api/simulate/{run_id}",
        detail="Aggregates all AgentRepresentations for this run, computes surface rates.",
    )
