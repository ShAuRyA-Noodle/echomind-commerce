"""Echomind Commerce - `/api/simulate/*` endpoints.

Wired to the real OpenRouter 4-model swarm. Accepts either:
  - `buyer_prompt_texts`: pre-built list of prompt strings (bypasses Gemini generator;
    useful when Flash quota is exhausted or for direct demo injection)
  - Otherwise generates prompts via Gemini Flash from merchant truths + customer questions.

Endpoints
    POST /api/simulate/run         - run a swarm pass (real OpenRouter calls)
    GET  /api/simulate/{run_id}    - persisted run lookup (Neo4j-backed)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.schemas import BuyerPrompt, NotImplementedResponse
from config.prompts import AGENT_SIMULATOR_SYSTEM_PROMPT
from core.agents.prompt_gen import generate_buyer_prompts
from core.agents.runner import BuyerPromptInput, run_swarm
from graph.operations import deterministic_id, upsert_typed

logger = logging.getLogger("echomind.api.simulate")
router = APIRouter(prefix="/simulate", tags=["simulate"])


class SimulateRequest(BaseModel):
    domain: str = Field(default="specialty coffee retail")
    n_prompts: int = Field(default=20, ge=2, le=150)
    catalog_excerpt: str = Field(default="(catalog excerpt unavailable)")
    policies_summary: str = Field(default="(policies unavailable)")
    product_categories: list[str] = Field(default_factory=list)
    merchant_truths_summary: list[dict[str, Any]] = Field(default_factory=list)
    customer_questions: list[dict[str, Any]] = Field(default_factory=list)
    demo_mode: bool = Field(default=False, description="Cap to 10 prompts, ~30s wall-clock")
    # Optional: bypass Gemini Flash generator entirely, pass prompts directly.
    # Each string becomes a BuyerPrompt node. Useful when Flash quota is exhausted.
    buyer_prompt_texts: list[str] = Field(default_factory=list)


@router.post("/run", summary="Run the agent swarm against buyer prompts (real OpenRouter calls)")
async def run_simulation(req: SimulateRequest) -> dict[str, Any]:
    """Fan buyer prompts out to 4-model swarm, persist results to Neo4j.

    Prompt source priority:
        1. `buyer_prompt_texts` (direct injection, bypasses Gemini Flash)
        2. Gemini Flash generator (uses merchant truths + customer questions)
    """
    started = datetime.now(timezone.utc)
    run_id = deterministic_id("run", started.isoformat(), str(req.n_prompts))

    if req.buyer_prompt_texts:
        # Direct injection path - no Gemini Flash needed.
        from api.schemas import IntentClass
        runner_input: list[BuyerPromptInput] = []
        for i, text in enumerate(req.buyer_prompt_texts):
            bp_id = deterministic_id("bp", run_id, str(i), text[:32])
            bp = BuyerPrompt(
                id=bp_id,
                prompt_text=text,
                intent_class="discover",
                length_bucket="medium" if len(text) < 60 else "long",
                is_adversarial=False,
            )
            await upsert_typed(bp, "BuyerPrompt")
            runner_input.append(BuyerPromptInput(id=bp_id, text=text))
        prompts_generated = len(runner_input)
        logger.info("simulate.direct_injection prompts=%d", prompts_generated)
    else:
        # Gemini Flash generator path.
        prompts = generate_buyer_prompts(
            n_prompts=req.n_prompts,
            domain=req.domain,
            product_categories=req.product_categories,
            merchant_truths_summary=req.merchant_truths_summary,
            customer_questions=req.customer_questions,
        )
        if not prompts:
            return {
                "status": "error",
                "run_id": run_id,
                "prompts_generated": 0,
                "note": (
                    "Prompt generator returned empty. Gemini Flash quota likely exhausted "
                    "(20 req/day free tier). Pass `buyer_prompt_texts` list directly to bypass."
                ),
            }
        for bp in prompts:
            await upsert_typed(bp, "BuyerPrompt")
        runner_input = [BuyerPromptInput(id=p.id, text=p.prompt_text) for p in prompts]
        prompts_generated = len(prompts)

    representations = await run_swarm(
        buyer_prompts=runner_input,
        catalog_excerpt=req.catalog_excerpt,
        policies_summary=req.policies_summary,
        system_prompt_template=AGENT_SIMULATOR_SYSTEM_PROMPT,
        demo_mode=req.demo_mode,
    )

    for rep in representations:
        await upsert_typed(rep, "AgentRepresentation")

    by_slot: dict[str, int] = {}
    parse_failures = 0
    for r in representations:
        slot_key = (r.agent_model or "").split("/")[-1].split(":")[0]
        by_slot[slot_key] = by_slot.get(slot_key, 0) + 1
        if r.parse_failed:
            parse_failures += 1

    duration = round((datetime.now(timezone.utc) - started).total_seconds(), 2)
    logger.info(
        "simulate.run.complete run_id=%s prompts=%d calls=%d duration_s=%.1f",
        run_id,
        prompts_generated,
        len(representations),
        duration,
    )
    return {
        "status": "ok",
        "run_id": run_id,
        "prompts_generated": prompts_generated,
        "agent_calls": len(representations),
        "by_model": by_slot,
        "parse_failures": parse_failures,
        "duration_seconds": duration,
        "demo_mode": req.demo_mode,
        "started_at": started.isoformat(),
    }


@router.get(
    "/{run_id}",
    response_model=NotImplementedResponse,
    summary="Run lookup (live AgentRepresentation rows already persisted to Neo4j)",
)
async def get_simulation(run_id: str) -> NotImplementedResponse:
    return NotImplementedResponse(
        endpoint=f"GET /api/simulate/{run_id}",
        detail="AgentRepresentation rows live in Neo4j. Query via /api/graph or /api/audit.",
    )
