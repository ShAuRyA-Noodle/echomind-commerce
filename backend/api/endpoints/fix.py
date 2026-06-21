"""Echomind Commerce - `/api/fix/*` endpoints.

Wired to real fix copy generation + Shopify Admin mutation + retest delta.

Endpoints
    POST /api/fix/generate/{gap_id}  - Gemini Pro copy gen (in merchant voice)
    POST /api/fix/apply              - push hydrated FixSuggestion to Shopify (real)
    POST /api/fix/retest/{fix_id}    - rerun swarm + measure observed delta
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.ownership import ScopeContext, scope_ctx
from api.schemas import AgentRepresentation, FixSuggestion, Gap
from config.prompts import AGENT_SIMULATOR_SYSTEM_PROMPT
from core.agents.runner import BuyerPromptInput, run_swarm
from core.fix.copy_generator import generate_fix
from core.fix.retest_orchestrator import measure_delta, serialize_delta
from core.fix.shopify_writer import apply_fix
from graph.neo4j_client import neo4j_client
from graph.operations import upsert_typed

logger = logging.getLogger("echomind.api.fix")
router = APIRouter(prefix="/fix", tags=["fix"])


class GenerateFixRequest(BaseModel):
    fix_type: str | None = None
    severity: float = Field(default=0.5, ge=0.0, le=1.0)
    affected_products: list[str] = Field(default_factory=list)
    merchant_voice_samples: list[str] = Field(default_factory=list)
    subgraph_direct: list[dict[str, Any]] = Field(default_factory=list)
    subgraph_semantic: list[dict[str, Any]] = Field(default_factory=list)
    subgraph_decisions: list[dict[str, Any]] = Field(default_factory=list)
    subgraph_contradictions: list[dict[str, Any]] = Field(default_factory=list)


class ApplyFixFullRequest(BaseModel):
    fix: FixSuggestion
    target_product_gid: str | None = None
    target_page_gid: str | None = None


@router.post("/generate/{gap_id}", summary="Generate FixSuggestion for a Gap (Gemini Pro)")
async def generate_fix_endpoint(
    gap_id: str,
    req: GenerateFixRequest,
    scope: ScopeContext = Depends(scope_ctx),
) -> dict[str, Any]:
    """Build a fix using the 4-strategy subgraph + merchant voice samples.

    When auth is on the gap must belong to the caller, and the new
    FixSuggestion is stamped with the owner so it scopes on later reads/applies.
    """
    # Ownership gate: the Gap this fix targets must be the caller's (when auth on).
    if scope.active:
        gap_rows = await neo4j_client.run(
            "MATCH (g:Gap {id: $id}) RETURN g LIMIT 1",
            {"id": gap_id},
        )
        scope.require_owns(gap_rows[0]["g"] if gap_rows else None, kind="gap")

    gap = Gap(
        id=gap_id,
        type=req.fix_type or "omission",  # type: ignore[arg-type]
        severity=req.severity,
        affected_products=req.affected_products,
    )
    fix = await generate_fix(
        gap=gap,
        subgraph_direct=req.subgraph_direct,
        subgraph_semantic=req.subgraph_semantic,
        subgraph_decisions=req.subgraph_decisions,
        subgraph_contradictions=req.subgraph_contradictions,
        merchant_voice_samples=req.merchant_voice_samples,
    )
    await upsert_typed(fix, "FixSuggestion", scope=scope)
    return _serialize_fix(fix)


@router.post("/apply", summary="Apply hydrated FixSuggestion to Shopify (real mutation)")
async def apply_fix_full(
    req: ApplyFixFullRequest,
    scope: ScopeContext = Depends(scope_ctx),
) -> dict[str, Any]:
    """Push the fix to Shopify Admin GraphQL.

    Caller hands the FixSuggestion (queried from Neo4j) plus the target gid.

    Authorization (defense-in-depth): when auth is enabled this mutation is
    gated on ownership. The caller supplies the FixSuggestion in the body, so we
    do NOT trust it - we re-fetch the persisted FixSuggestion (and, when given,
    the target Product) from Neo4j by id/gid and confirm the authenticated owner
    owns them before touching Shopify. A cross-tenant fix/target is rejected with
    403; an unknown one with 404. No-op when auth is off (open demo unchanged).
    """
    if scope.active:
        await _authorize_apply(req, scope)

    applied = await apply_fix(
        req.fix,
        target_product_gid=req.target_product_gid,
        target_page_gid=req.target_page_gid,
    )
    await upsert_typed(applied, "FixSuggestion", scope=scope)
    return _serialize_fix(applied)


async def _authorize_apply(req: ApplyFixFullRequest, scope: ScopeContext) -> None:
    """Confirm the caller owns the FixSuggestion and/or target Product.

    Server-side re-fetch by id/gid (never trusting body-supplied owner data).
    Raises 403/404 via `scope.require_owns` on a cross-tenant or unknown
    resource. If neither the fix node nor the target product exists yet (e.g. a
    freshly generated fix not yet persisted), the apply is allowed - there is no
    other tenant's resource being mutated.
    """
    checked_any = False

    fix_id = getattr(req.fix, "id", None)
    if fix_id:
        fix_rows = await neo4j_client.run(
            "MATCH (f:FixSuggestion {id: $id}) RETURN f LIMIT 1",
            {"id": fix_id},
        )
        if fix_rows:
            scope.require_owns(fix_rows[0]["f"], kind="fix")
            checked_any = True

    if req.target_product_gid:
        prod_rows = await neo4j_client.run(
            "MATCH (p:Product {shopify_gid: $gid}) RETURN p LIMIT 1",
            {"gid": req.target_product_gid},
        )
        if prod_rows:
            scope.require_owns(prod_rows[0]["p"], kind="product")
            checked_any = True

    if not checked_any:
        logger.info(
            "fix.apply.no_persisted_resource fix_id=%s gid=%s - allowing (nothing owned to violate)",
            fix_id,
            req.target_product_gid,
        )


class RetestRequest(BaseModel):
    catalog_excerpt: str | None = None
    policies_summary: str | None = None
    demo_mode: bool = True  # cap to 10 prompts so retest finishes in ~30s


@router.post("/retest/{fix_id}", summary="Rerun swarm + measure observed delta (real)")
async def retest_fix(
    fix_id: str,
    req: RetestRequest | None = None,
    scope: ScopeContext = Depends(scope_ctx),
) -> dict[str, Any]:
    """Rerun the swarm against the buyer prompts that previously surfaced this gap,
    compute the before/after surface-rate delta, and persist `observed_delta`
    onto the FixSuggestion node. Closes the detect → fix → re-test → measure loop.

    The FixSuggestion (and its Gap) are scoped to the authenticated owner when
    auth is on, so a caller cannot retest another tenant's fix.
    """
    cfg = req or RetestRequest()

    # 1. Fetch FixSuggestion + Gap (scoped: cross-tenant ids read as not_found)
    fix_rows = await neo4j_client.run(
        f"MATCH (f:FixSuggestion {{id: $id}}) WHERE {scope.predicate('f')} RETURN f LIMIT 1",
        scope.params({"id": fix_id}),
    )
    if not fix_rows:
        return {"status": "not_found", "fix_id": fix_id}
    f = fix_rows[0]["f"]
    gap_id = f.get("gap_id")

    gap_rows = await neo4j_client.run(
        f"MATCH (g:Gap {{id: $id}}) WHERE {scope.predicate('g')} RETURN g LIMIT 1",
        scope.params({"id": gap_id}),
    )
    if not gap_rows:
        return {"status": "gap_not_found", "fix_id": fix_id, "gap_id": gap_id}
    g = gap_rows[0]["g"]
    affected_products: list[str] = g.get("affected_products") or []

    # 2. Resolve product titles (used as surface-rate targets)
    title_rows = []
    description_rows = []
    if affected_products:
        title_rows = await neo4j_client.run(
            f"""
            MATCH (p:Product) WHERE p.id IN $ids AND {scope.predicate("p")}
            RETURN p.id AS id, p.title AS title, p.description AS description
            """,
            scope.params({"ids": affected_products}),
        )
        description_rows = title_rows
    target_titles = [r["title"] for r in title_rows if r.get("title")]

    # 3. Discover buyer prompts that previously surfaced the gap.
    #    Two strategies, tried in order:
    #    a) AgentRep MENTIONS Product (edge) → buyer_prompt_id
    #    b) Any AgentRep whose surfaced_products substring-matches a target title
    hist_rows = []
    if affected_products:
        hist_rows = await neo4j_client.run(
            f"""
            MATCH (a:AgentRepresentation)-[:MENTIONS]->(p:Product)
            WHERE p.id IN $ids AND {scope.predicate("a")} AND {scope.predicate("p")}
            OPTIONAL MATCH (b:BuyerPrompt {{id: a.buyer_prompt_id}})
            RETURN a.id AS rep_id, a.agent_model AS agent_model,
                   a.response_text AS response_text,
                   coalesce(a.surfaced_products, []) AS surfaced_products,
                   a.buyer_prompt_id AS buyer_prompt_id,
                   b.prompt_text AS prompt_text
            LIMIT 60
            """,
            scope.params({"ids": affected_products}),
        )
    if not hist_rows and target_titles:
        # surfaced_products substring match (no edge required)
        hist_rows = await neo4j_client.run(
            f"""
            MATCH (a:AgentRepresentation)
            WHERE ({scope.predicate("a")})
              AND any(t IN a.surfaced_products WHERE toLower(t) IN $titles_lower)
            OPTIONAL MATCH (b:BuyerPrompt {{id: a.buyer_prompt_id}})
            RETURN a.id AS rep_id, a.agent_model AS agent_model,
                   a.response_text AS response_text,
                   coalesce(a.surfaced_products, []) AS surfaced_products,
                   a.buyer_prompt_id AS buyer_prompt_id,
                   b.prompt_text AS prompt_text
            LIMIT 60
            """,
            scope.params({"titles_lower": [t.lower() for t in target_titles]}),
        )

    before_reps: list[AgentRepresentation] = []
    prompt_map: dict[str, str] = {}
    for r in hist_rows:
        try:
            before_reps.append(
                AgentRepresentation(
                    id=r["rep_id"],
                    agent_model=r.get("agent_model") or "unknown",
                    buyer_prompt_id=r.get("buyer_prompt_id") or "",
                    response_text=r.get("response_text") or "",
                    surfaced_products=r.get("surfaced_products") or [],
                )
            )
        except Exception:  # noqa: BLE001 - skip malformed rows
            logger.exception("retest.before_rep.parse_failed rep_id=%s", r.get("rep_id"))
        pid = r.get("buyer_prompt_id")
        if pid and r.get("prompt_text") and pid not in prompt_map:
            prompt_map[pid] = r["prompt_text"]

    if not prompt_map:
        return {
            "status": "no_prompts_found",
            "fix_id": fix_id,
            "gap_id": gap_id,
            "detail": "No historical BuyerPrompts surfaced this gap. Run a swarm pass first.",
        }

    # 4. Build catalog excerpt from affected Products if caller didn't supply one
    if cfg.catalog_excerpt:
        catalog = cfg.catalog_excerpt
    else:
        catalog_lines: list[str] = []
        for r in description_rows[:10]:
            title = r.get("title") or r.get("id")
            desc = (r.get("description") or "")[:280]
            catalog_lines.append(f"- {title}: {desc}")
        catalog = "\n".join(catalog_lines) or "(catalog unavailable)"
    policies = cfg.policies_summary or "(policies unchanged)"

    runner_input = [
        BuyerPromptInput(id=pid, text=text) for pid, text in prompt_map.items()
    ]

    # 5. Rerun swarm (after state)
    after_reps = await run_swarm(
        buyer_prompts=runner_input,
        catalog_excerpt=catalog,
        policies_summary=policies,
        system_prompt_template=AGENT_SIMULATOR_SYSTEM_PROMPT,
        demo_mode=cfg.demo_mode,
    )

    # Persist the new representations so /replay reflects them (owner-stamped)
    for rep in after_reps:
        await upsert_typed(rep, "AgentRepresentation", scope=scope)

    # 6. Measure delta
    fix_obj = FixSuggestion(
        id=f.get("id", fix_id),
        gap_id=gap_id,
        fix_type=f.get("fix_type", "copy_rewrite"),  # type: ignore[arg-type]
        proposed_text=f.get("proposed_text", ""),
        applied=bool(f.get("applied", False)),
    )
    gap_obj = Gap(
        id=g.get("id", gap_id),
        type=g.get("type", "omission"),  # type: ignore[arg-type]
        severity=g.get("severity", 0.5),
    )
    delta = measure_delta(
        fix=fix_obj,
        gap=gap_obj,
        before=before_reps,
        after=after_reps,
        target_product_titles=target_titles or [pid for pid in affected_products],
    )

    # 7. Persist observed_delta back onto the FixSuggestion (owner-scoped write)
    await neo4j_client.run(
        f"""
        MATCH (f:FixSuggestion {{id: $id}})
        WHERE {scope.predicate("f")}
        SET f.observed_delta = $delta_pp,
            f.observed_before_rate = $before_rate,
            f.observed_after_rate = $after_rate,
            f.retested_at = $ts
        RETURN f.id AS id
        """,
        scope.params({
            "id": fix_id,
            "delta_pp": float(delta.delta_pp),
            "before_rate": float(delta.before_surface_rate),
            "after_rate": float(delta.after_surface_rate),
            "ts": _utcnow_iso(),
        }),
    )

    return {
        "status": "ok",
        "fix_id": fix_id,
        "gap_id": gap_id,
        "delta": serialize_delta(delta),
        "n_buyer_prompts": len(runner_input),
        "n_before_reps": len(before_reps),
        "n_after_reps": len(after_reps),
        "target_titles": target_titles,
    }


def _utcnow_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _serialize_fix(fix: FixSuggestion) -> dict[str, Any]:
    pdr = fix.predicted_delta_range
    return {
        "id": fix.id,
        "gap_id": fix.gap_id,
        "fix_type": fix.fix_type,
        "proposed_text": fix.proposed_text,
        "applied": fix.applied,
        "applied_at": fix.applied_at.isoformat() if fix.applied_at else None,
        "shopify_resource_id": fix.shopify_resource_id,
        "predicted_delta_range": (
            {"low": pdr.low, "high": pdr.high, "metric": pdr.metric, "rationale": pdr.rationale}
            if pdr
            else None
        ),
        "observed_delta": fix.observed_delta,
        "voice_match_notes": fix.voice_match_notes,
    }
