"""Echomind Commerce - buyer-intent prompt generator.

Wraps `BUYER_PROMPT_GENERATION` from `prompts.py`. Generates 50-150 buyer
prompts per audit, distributed 40/25/20/15 across discover/compare/objection/
post-purchase intent classes, seeded by:

    * Product categories (sample of titles + tags)
    * MerchantTruth statements (positioning + audience)
    * Real CustomerQuestion nodes (gold - actual customer phrasings)

Every emitted `BuyerPrompt` is persisted as a graph node so the audit run is
fully replayable.
"""

from __future__ import annotations

import logging
from typing import Any

from api.schemas import BuyerPrompt
from config.prompts import BUYER_PROMPT_GENERATION
from graph.operations import deterministic_id
from services.llm_service import llm_service, safe_json_loads

logger = logging.getLogger("echomind.agents.prompt_gen")


def generate_buyer_prompts(
    *,
    n_prompts: int,
    domain: str,
    product_categories: list[str],
    merchant_truths_summary: list[dict[str, Any]],
    customer_questions: list[dict[str, Any]],
) -> list[BuyerPrompt]:
    prompt_text = BUYER_PROMPT_GENERATION.format(
        n_prompts=n_prompts,
        domain=domain,
        product_categories=product_categories,
        merchant_truths_summary=merchant_truths_summary,
        customer_questions=customer_questions,
    )
    raw = ""
    try:
        raw = llm_service.gemini_flash(prompt_text, temperature=0.85)
    except Exception as exc:  # noqa: BLE001
        logger.exception("prompt_gen.failed exc=%r", exc)
        return []

    parsed = safe_json_loads(raw)
    if not isinstance(parsed, list):
        logger.warning("prompt_gen.parse_failed shape=%s", type(parsed).__name__)
        return []

    out: list[BuyerPrompt] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        text = item.get("prompt_text")
        if not text:
            continue
        bid = deterministic_id("bp", str(text))
        out.append(
            BuyerPrompt(
                id=bid,
                prompt_text=str(text),
                intent_class=str(item.get("intent_class", "discover")).lower(),  # type: ignore[arg-type]
                length_bucket=str(item.get("length_bucket", "medium")).lower(),  # type: ignore[arg-type]
                is_adversarial=bool(item.get("is_adversarial", False)),
                generated_from_truths=[
                    str(t) for t in (item.get("generated_from_truths") or [])
                ],
            )
        )
    return out


__all__ = ["generate_buyer_prompts"]
