"""Echomind Commerce - agent swarm runner (WINNING_PLAN §15).

Fans out one buyer prompt to all four swarm slots in parallel, then iterates
across N buyer prompts with bounded concurrency. The runner produces typed
`AgentRepresentation` rows + the live token streams for the `/simulate` UI.

Performance:
    * Default concurrency = 8 (4 slots × 2 prompts in-flight)
    * Demo mode caps prompt count to 10 → ~30s wall-clock for 40 calls
    * Failed slots are *not* retried beyond `call_one`'s 3 attempts; they
      surface as `parse_failed=true` rows so the calibration auto-downgrades.

Output:
    * `run_swarm(buyer_prompts)` → `list[AgentRepresentation]`
    * Optional event callback for streaming tokens to the UI WebSocket.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Awaitable, Callable

from api.schemas import AgentRepresentation
from config.settings import settings
from core.agents.openrouter import (
    AgentCall,
    AgentResponse,
    call_one,
    swarm_model_lineup,
)
from graph.operations import deterministic_id

logger = logging.getLogger("echomind.agents.runner")


@dataclass(frozen=True)
class BuyerPromptInput:
    """Minimal shape needed to fan a buyer prompt out to the swarm."""

    id: str
    text: str


# Event types the runner emits - wire into `/api/simulate/ws/{run_id}`.
EventCallback = Callable[[dict], Awaitable[None]]


async def run_swarm(
    *,
    buyer_prompts: list[BuyerPromptInput],
    catalog_excerpt: str,
    policies_summary: str,
    system_prompt_template: str,
    on_event: EventCallback | None = None,
    concurrency: int = 8,
    demo_mode: bool = False,
) -> list[AgentRepresentation]:
    """Run the 4-model swarm against `buyer_prompts`. Returns one
    `AgentRepresentation` per (slot × prompt).

    `system_prompt_template` is the rendered AGENT_SIMULATOR_SYSTEM_PROMPT
    with `{catalog_excerpt}` and `{policies_summary}` already filled in by
    the caller. The runner doesn't know about prompts.py.
    """
    if demo_mode:
        buyer_prompts = buyer_prompts[:10]
        concurrency = max(4, concurrency)

    lineup = swarm_model_lineup()
    sem = asyncio.Semaphore(concurrency)

    sys_prompt = system_prompt_template.format(
        catalog_excerpt=catalog_excerpt,
        policies_summary=policies_summary,
    )

    async def fan_out_one(bp: BuyerPromptInput) -> list[AgentRepresentation]:
        out: list[AgentRepresentation] = []

        async def call_slot(slot: str, model: str) -> None:
            async with sem:
                if on_event:
                    await on_event({"type": "agent_start", "slot": slot, "buyer_prompt_id": bp.id})
                resp = await call_one(
                    AgentCall(
                        slot=slot,
                        model=model,
                        system_prompt=sys_prompt,
                        user_prompt=bp.text,
                    )
                )
                rep = _to_representation(bp.id, resp)
                out.append(rep)
                if on_event:
                    await on_event(
                        {
                            "type": "agent_done",
                            "slot": slot,
                            "buyer_prompt_id": bp.id,
                            "latency_ms": resp.latency_ms,
                            "parse_failed": resp.parse_failed,
                            "error": resp.error,
                        }
                    )

        await asyncio.gather(*[call_slot(slot, model) for slot, model in lineup.items()])
        return out

    all_results = await asyncio.gather(*[fan_out_one(bp) for bp in buyer_prompts])
    flat = [rep for sub in all_results for rep in sub]
    if on_event:
        await on_event({"type": "run_complete", "total_calls": len(flat)})
    logger.info(
        "swarm.run_complete prompts=%d slots=%d total_calls=%d demo=%s",
        len(buyer_prompts),
        len(lineup),
        len(flat),
        bool(demo_mode),
    )
    return flat


def _to_representation(buyer_prompt_id: str, resp: AgentResponse) -> AgentRepresentation:
    """Convert a swarm AgentResponse into a typed AgentRepresentation node."""
    parsed = resp.parsed_json or {}
    surfaced_titles: list[str] = []
    cited_policies: list[str] = []
    confidence: float | None = None
    if isinstance(parsed, dict):
        recs = parsed.get("recommended_products") or []
        for r in recs if isinstance(recs, list) else []:
            t = r.get("product_title") if isinstance(r, dict) else None
            if t:
                surfaced_titles.append(t)
        if isinstance(parsed.get("confidence"), (int, float)):
            confidence = float(parsed["confidence"])
        cps = parsed.get("cited_policies") or []
        if isinstance(cps, list):
            cited_policies = [str(c) for c in cps]
    rep_id = deterministic_id("agent_rep", resp.slot, buyer_prompt_id)
    return AgentRepresentation(
        id=rep_id,
        agent_model=resp.model,
        buyer_prompt_id=buyer_prompt_id,
        response_text=resp.response_text,
        surfaced_products=surfaced_titles,
        cited_policies=cited_policies,
        confidence_in_recommendation=confidence,
        latency_ms=resp.latency_ms,
        captured_at=datetime.now(timezone.utc),
        parse_failed=resp.parse_failed,
    )


__all__ = [
    "BuyerPromptInput",
    "run_swarm",
]
