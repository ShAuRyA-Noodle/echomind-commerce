"""Echomind Commerce - `/api/debug` observability endpoint.

Surfaces enough live state for a judge (or for us, mid-demo) to confirm
the system is healthy, attached to real services, and correctly wired.

Routes:
    GET /api/debug/health     - extended health (vs. the slim /health)
    GET /api/debug/swarm      - agent swarm lineup + connectivity check
    GET /api/debug/graph      - Neo4j node + edge counts by type
    GET /api/debug/shopify    - shop metadata round-trip
    GET /api/debug/env        - sanitized env (which integrations are wired)
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from config.settings import settings
from core.agents.openrouter import call_one, AgentCall, swarm_model_lineup
from graph.neo4j_client import neo4j_client
from graph.operations import graph_stats
from services.llm_service import llm_service
from services.shopify_service import shopify_service

logger = logging.getLogger("echomind.api.debug")
router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/health", summary="Extended health (Neo4j + Gemini + OpenRouter + Shopify)")
async def debug_health() -> dict[str, Any]:
    out: dict[str, Any] = {}
    out["neo4j"] = await neo4j_client.ping()
    out["gemini"] = llm_service.healthcheck()

    # OpenRouter - small touch using the configured GPT-OSS slot.
    try:
        resp = await call_one(
            AgentCall(
                slot="gpt_oss",
                model=settings.OPENROUTER_AGENT_GPTOSS,
                system_prompt="Reply with a single word.",
                user_prompt="ping",
                max_tokens=8,
                temperature=0.0,
            )
        )
        out["openrouter"] = {
            "status": "ok" if resp.response_text else "empty",
            "latency_ms": resp.latency_ms,
            "parse_failed": resp.parse_failed,
            "model": resp.model,
            "sample": resp.response_text[:64],
            "error": resp.error,
        }
    except Exception as exc:  # noqa: BLE001
        out["openrouter"] = {"status": "error", "error": repr(exc)}

    # Shopify - shop metadata round-trip.
    try:
        shop = await shopify_service.fetch_shop_metadata()
        out["shopify"] = {
            "status": "ok",
            "name": shop.get("name"),
            "primary_domain": (shop.get("primaryDomain") or {}).get("url"),
            "currency": shop.get("currencyCode"),
            "plan": (shop.get("plan") or {}).get("displayName"),
        }
    except Exception as exc:  # noqa: BLE001
        out["shopify"] = {"status": "error", "error": repr(exc)}

    return out


@router.get("/swarm", summary="Agent swarm lineup + per-model connectivity")
async def debug_swarm() -> dict[str, Any]:
    lineup = swarm_model_lineup()
    out: dict[str, Any] = {"lineup": lineup, "checks": {}}
    for slot, model in lineup.items():
        try:
            resp = await call_one(
                AgentCall(
                    slot=slot,
                    model=model,
                    system_prompt="You return only single-word answers.",
                    user_prompt="Say pong.",
                    max_tokens=8,
                    temperature=0.0,
                )
            )
            out["checks"][slot] = {
                "model": model,
                "status": "ok" if resp.response_text else "empty",
                "latency_ms": resp.latency_ms,
                "parse_failed": resp.parse_failed,
                "sample": resp.response_text[:48],
                "error": resp.error,
            }
        except Exception as exc:  # noqa: BLE001
            out["checks"][slot] = {"model": model, "status": "error", "error": repr(exc)}
    return out


@router.get("/graph", summary="Live Neo4j node + edge counts by type")
async def debug_graph() -> dict[str, Any]:
    try:
        stats = await graph_stats()
        return {"status": "ok", **stats}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": repr(exc)}


@router.get("/shopify", summary="Shopify metadata + ingest summary")
async def debug_shopify() -> dict[str, Any]:
    try:
        shop = await shopify_service.fetch_shop_metadata()
        return {"status": "ok", "shop": shop}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": repr(exc)}


@router.get("/env", summary="Which integrations are wired (no secrets)")
async def debug_env() -> dict[str, Any]:
    def has(v: str | None) -> bool:
        return bool(v)

    return {
        "env": settings.ENV,
        "is_local": settings.is_local,
        "wired": {
            "gemini":            has(settings.GEMINI_API_KEY),
            "openrouter":        has(settings.OPENROUTER_API_KEY),
            "neo4j":             has(settings.NEO4J_URI),
            "firebase_admin":    has(settings.GOOGLE_APPLICATION_CREDENTIALS),
            "firebase_web":      has(settings.FIREBASE_API_KEY),
            "shopify_admin":     has(settings.SHOPIFY_ADMIN_ACCESS_TOKEN),
            "shopify_storefront": has(settings.SHOPIFY_STOREFRONT_ACCESS_TOKEN),
        },
        "swarm_lineup": swarm_model_lineup(),
        "gemini_models": {
            "flash": settings.GEMINI_FLASH_MODEL,
            "pro": settings.GEMINI_PRO_MODEL,
            "embedding": settings.GEMINI_EMBEDDING_MODEL,
        },
    }
