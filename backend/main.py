"""Echomind Commerce - FastAPI application entrypoint.

Run locally with::

    uvicorn main:app --reload --host 0.0.0.0 --port 8000

The app:
    * mounts every router from `api/endpoints` under `/api`
    * exposes `/health` (pings Neo4j + does one Gemini call)
    * registers two real WebSocket handlers:
        - `/api/interview/ws/{session_id}` runs the live Socratic loop
          (text_input -> extract -> persist -> graph_update events)
        - `/api/simulate/ws/{run_id}` streams agent_start / agent_done /
          run_progress events from the OpenRouter swarm runner
    * uses a lifespan handler to bring up + tear down Neo4j + Firebase
    * applies CORS for the Next.js dev server (http://localhost:3000)
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.auth_deps import verify_ws_token
from api.auth_middleware import FirebaseAuthMiddleware, SecurityHeadersMiddleware
from api.endpoints import (
    audit,
    auth,
    debug,
    diagnose,
    fix,
    graph,
    interview,
    onboard,
    public_audit,
    simulate,
)
from api.schemas import HealthResponse
from config.prompts import AGENT_SIMULATOR_SYSTEM_PROMPT
from config.settings import settings
from core.agents.prompt_gen import generate_buyer_prompts
from core.agents.runner import BuyerPromptInput, run_swarm
from core.socratic.extractor import extract_chunk
from core.socratic.question_gen import generate_question
from graph.neo4j_client import neo4j_client
from graph.operations import graph_stats, upsert_typed
from services.firebase_service import firebase_service
from services.llm_service import llm_service
from utils.logging_safety import safe_log

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("echomind.main")


# ---------------------------------------------------------------------------
# Lifespan: bring up Neo4j + Firebase on startup, tear down on shutdown.
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    logger.info("startup.begin env=%s", settings.ENV)
    try:
        await neo4j_client.connect()
        logger.info("startup.neo4j.ok")
    except Exception:  # noqa: BLE001
        logger.exception("startup.neo4j.failed - backend will run degraded")
    try:
        firebase_service.initialize()
        logger.info("startup.firebase.attempted")
    except Exception:  # noqa: BLE001
        logger.exception("startup.firebase.failed - backend will run degraded")
    logger.info("startup.complete")
    try:
        yield
    finally:
        logger.info("shutdown.begin")
        try:
            await neo4j_client.close()
        except Exception:  # noqa: BLE001
            logger.exception("shutdown.neo4j.failed")
        try:
            firebase_service.shutdown()
        except Exception:  # noqa: BLE001
            logger.exception("shutdown.firebase.failed")
        logger.info("shutdown.complete")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Echomind Commerce API",
    description=(
        "AI Representation Optimizer for Shopify merchants. "
        "Backend for the Kasparro Agentic Commerce Hackathon (Track 5)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(FirebaseAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=[],
    max_age=600,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(onboard.router)
api_router.include_router(interview.router)
api_router.include_router(simulate.router)
api_router.include_router(diagnose.router)
api_router.include_router(fix.router)
api_router.include_router(audit.router)
api_router.include_router(graph.router)
api_router.include_router(auth.router)
api_router.include_router(public_audit.router)
# Debug router exposes infra state (model lineup, env wiring, Shopify metadata).
# Only mount when running locally so production never exposes /api/debug/*.
if settings.is_local:
    api_router.include_router(debug.router)
app.include_router(api_router)


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {
        "service": "echomind-commerce-backend",
        "version": "0.1.0",
        "env": settings.ENV,
    }


@app.get("/health", tags=["meta"], response_model=HealthResponse)
async def health() -> JSONResponse:
    """Live health check: pings Neo4j and exercises one Gemini Flash call."""
    neo4j_status = await neo4j_client.ping()
    gemini_status = llm_service.healthcheck()
    overall: str = "ok"
    if neo4j_status.get("status") != "ok" or gemini_status.get("gemini_flash") not in {"ok", "empty"}:
        overall = "degraded"
    if neo4j_status.get("status") == "error" and gemini_status.get("gemini_flash") == "error":
        overall = "error"
    body = HealthResponse(
        status=overall,  # type: ignore[arg-type]
        neo4j=neo4j_status,
        gemini=gemini_status,
        env=settings.ENV,
    )
    return JSONResponse(content=body.model_dump(), status_code=200)


# ---------------------------------------------------------------------------
# WebSocket: /api/interview/ws/{session_id} - live Socratic loop
# ---------------------------------------------------------------------------


_PHASE_LABELS = {
    "brand_mapping": "Brand Mapping",
    "product_truths": "Product Truths",
    "customer_reality": "Customer Reality",
    "policy_edge_cases": "Policy Edge Cases",
    "trust_signals": "Trust Signals",
}
_PHASE_ORDER = list(_PHASE_LABELS.keys())


@app.websocket("/api/interview/ws/{session_id}")
async def interview_ws(websocket: WebSocket, session_id: str) -> None:
    """Real Socratic loop over a WebSocket.

    Inbound messages
        {type: "text_input", text: "..."}                 - merchant utterance
        {type: "control",    action: "start"}             - emit first question
        {type: "control",    action: "next_question"}     - advance the loop
        {type: "control",    action: "advance_phase"}     - manual phase bump

    Outbound events
        {type: "session_open", session_id, phase}
        {type: "transcript",   speaker: "M"|"I", text, final: true}
        {type: "extraction",   counts: {...}, parse_failed: bool}
        {type: "graph_update", added: [{type, id, label}], stats: {...}}
        {type: "question",     text, follow_up_if_brief, phase, phase_label}
        {type: "phase_change", phase, phase_label}
        {type: "progress",     question_count, elapsed_minutes, graph_stats}
        {type: "error",        message}
    """
    await websocket.accept()
    user = await verify_ws_token(websocket)
    if user is None:
        return
    logger.info("interview.ws.connected session_id=%s uid=%s", safe_log(session_id), safe_log(user.get("uid")))

    state: dict[str, Any] = {
        "phase": "brand_mapping",
        "phase_idx": 0,
        "question_count": 0,
        "history": [],
        "domain": "specialty coffee retail",
    }
    started_at = asyncio.get_event_loop().time()

    async def send(event: dict[str, Any]) -> None:
        try:
            await websocket.send_json(event)
        except Exception:  # noqa: BLE001
            pass

    async def emit_progress() -> None:
        elapsed_min = (asyncio.get_event_loop().time() - started_at) / 60.0
        try:
            stats = await graph_stats()
        except Exception:  # noqa: BLE001
            stats = {}
        await send(
            {
                "type": "progress",
                "question_count": state["question_count"],
                "elapsed_minutes": round(elapsed_min, 2),
                "graph_stats": stats,
            }
        )

    await send(
        {
            "type": "session_open",
            "session_id": session_id,
            "phase": state["phase"],
            "phase_label": _PHASE_LABELS[state["phase"]],
        }
    )

    try:
        while True:
            message = await websocket.receive_json()
            mtype = message.get("type")

            if mtype == "text_input":
                text = (message.get("text") or "").strip()
                if not text:
                    continue
                await send({"type": "transcript", "speaker": "M", "text": text, "final": True})
                state["history"].append({"M": text})

                # Run Gemini Flash extraction over the chunk.
                result = extract_chunk(
                    transcript_chunk=text,
                    phase=state["phase"],
                    phase_name=_PHASE_LABELS[state["phase"]],
                    domain=state["domain"],
                )
                added: list[dict[str, str]] = []
                for t in result.merchant_truths:
                    await upsert_typed(t, "MerchantTruth")
                    added.append({"type": "MerchantTruth", "id": t.id, "label": t.statement[:80]})
                for d in result.decisions:
                    await upsert_typed(d, "Decision")
                    added.append({"type": "Decision", "id": d.id, "label": d.question[:80]})
                for p in result.patterns:
                    await upsert_typed(p, "Pattern")
                    added.append({"type": "Pattern", "id": p.id, "label": p.name[:80]})
                for q in result.customer_questions:
                    await upsert_typed(q, "CustomerQuestion")
                    added.append({"type": "CustomerQuestion", "id": q.id, "label": q.question[:80]})
                for pol in result.policies:
                    await upsert_typed(pol, "Policy")
                    added.append({"type": "Policy", "id": pol.id, "label": pol.text[:80]})

                await send(
                    {
                        "type": "extraction",
                        "counts": {
                            "merchant_truths": len(result.merchant_truths),
                            "decisions": len(result.decisions),
                            "patterns": len(result.patterns),
                            "customer_questions": len(result.customer_questions),
                            "policies": len(result.policies),
                        },
                        "parse_failed": result.parse_failed,
                    }
                )
                if added:
                    try:
                        stats = await graph_stats()
                    except Exception:  # noqa: BLE001
                        stats = {}
                    await send({"type": "graph_update", "added": added, "stats": stats})

            elif mtype == "control":
                action = message.get("action")
                if action in ("start", "next_question"):
                    elapsed_min = (asyncio.get_event_loop().time() - started_at) / 60.0
                    last_pairs = [
                        {"M": h.get("M", ""), "I": h.get("I", "")}
                        for h in state["history"][-5:]
                    ]
                    try:
                        stats = await graph_stats()
                    except Exception:  # noqa: BLE001
                        stats = {}
                    q = generate_question(
                        phase=state["phase"],
                        question_count=state["question_count"],
                        elapsed_minutes=elapsed_min,
                        domain=state["domain"],
                        graph_stats=stats,
                        top_3_frontiers=[],
                        last_5_qa_pairs=last_pairs,
                        underrepresented_tacit_category=None,
                    )
                    if q.question:
                        state["question_count"] += 1
                        state["history"].append({"I": q.question})
                        await send(
                            {
                                "type": "question",
                                "text": q.question,
                                "follow_up_if_brief": q.follow_up_if_brief,
                                "phase": state["phase"],
                                "phase_label": _PHASE_LABELS[state["phase"]],
                            }
                        )
                    else:
                        await send(
                            {
                                "type": "error",
                                "message": "Question generator returned null.",
                                "uncertainty_notes": q.uncertainty_notes,
                            }
                        )
                    await emit_progress()

                elif action == "advance_phase":
                    next_idx = min(state["phase_idx"] + 1, len(_PHASE_ORDER) - 1)
                    state["phase_idx"] = next_idx
                    state["phase"] = _PHASE_ORDER[next_idx]
                    await send(
                        {
                            "type": "phase_change",
                            "phase": state["phase"],
                            "phase_label": _PHASE_LABELS[state["phase"]],
                        }
                    )

                elif action == "ping":
                    await send({"type": "pong"})

                else:
                    await send({"type": "error", "message": f"unknown control action: {action}"})

            elif mtype == "audio_chunk":
                # Browser-side STT (Web Speech API) transcribes locally and
                # emits text_input events; this branch is reserved for the
                # server-side STT V2 path, gated until quota is wired.
                await send(
                    {
                        "type": "error",
                        "message": "audio_chunk path: use browser Web Speech API; backend STT V2 is gated by Cloud Speech quota.",
                    }
                )
            else:
                await send({"type": "error", "message": f"unknown message type: {mtype}"})

    except WebSocketDisconnect:
        logger.info("interview.ws.disconnected session_id=%s", safe_log(session_id))
    except Exception:  # noqa: BLE001
        logger.exception("interview.ws.error session_id=%s", safe_log(session_id))
        try:
            await websocket.close(code=1011)
        except Exception:  # noqa: BLE001
            pass


# ---------------------------------------------------------------------------
# WebSocket: /api/simulate/ws/{run_id} - real swarm streaming
# ---------------------------------------------------------------------------


@app.websocket("/api/simulate/ws/{run_id}")
async def simulate_ws(websocket: WebSocket, run_id: str) -> None:
    """Stream live agent events as the swarm runs.

    Inbound
        {type: "control", action: "start", config: {...}}

    Outbound
        {type: "run_open", run_id}
        {type: "agent_start", slot, buyer_prompt_id}
        {type: "agent_done",  slot, buyer_prompt_id, latency_ms, parse_failed}
        {type: "run_progress", completed, total}
        {type: "run_complete", total_calls}
    """
    await websocket.accept()
    user = await verify_ws_token(websocket)
    if user is None:
        return
    logger.info("simulate.ws.connected run_id=%s uid=%s", safe_log(run_id), safe_log(user.get("uid")))
    await websocket.send_json({"type": "run_open", "run_id": run_id})

    try:
        message = await websocket.receive_json()
        if message.get("type") != "control" or message.get("action") != "start":
            await websocket.send_json(
                {
                    "type": "error",
                    "message": "First message must be {type:'control',action:'start',config:{...}}",
                }
            )
            await websocket.close(code=1003)
            return

        cfg = message.get("config") or {}
        n_prompts = int(cfg.get("n_prompts", 10))
        domain = cfg.get("domain", "specialty coffee retail")
        catalog_excerpt = cfg.get("catalog_excerpt", "(catalog excerpt unavailable)")
        policies_summary = cfg.get("policies_summary", "(policies unavailable)")
        product_categories = cfg.get("product_categories", [])
        merchant_truths_summary = cfg.get("merchant_truths_summary", [])
        customer_questions = cfg.get("customer_questions", [])
        demo_mode = bool(cfg.get("demo_mode", True))

        prompts = generate_buyer_prompts(
            n_prompts=n_prompts,
            domain=domain,
            product_categories=product_categories,
            merchant_truths_summary=merchant_truths_summary,
            customer_questions=customer_questions,
        )
        runner_input = [BuyerPromptInput(id=p.id, text=p.prompt_text) for p in prompts]
        for bp in prompts:
            await upsert_typed(bp, "BuyerPrompt")

        completed = {"n": 0}
        total = max(1, len(runner_input)) * 4

        async def emit(event: dict[str, Any]) -> None:
            try:
                await websocket.send_json(event)
                if event.get("type") == "agent_done":
                    completed["n"] += 1
                    await websocket.send_json(
                        {"type": "run_progress", "completed": completed["n"], "total": total}
                    )
            except Exception:  # noqa: BLE001
                pass

        representations = await run_swarm(
            buyer_prompts=runner_input,
            catalog_excerpt=catalog_excerpt,
            policies_summary=policies_summary,
            system_prompt_template=AGENT_SIMULATOR_SYSTEM_PROMPT,
            on_event=emit,
            demo_mode=demo_mode,
        )

        for rep in representations:
            await upsert_typed(rep, "AgentRepresentation")

        await websocket.send_json(
            {
                "type": "run_complete",
                "total_calls": len(representations),
                "buyer_prompts": len(prompts),
            }
        )

    except WebSocketDisconnect:
        logger.info("simulate.ws.disconnected run_id=%s", safe_log(run_id))
    except Exception:  # noqa: BLE001
        logger.exception("simulate.ws.error run_id=%s", safe_log(run_id))
        try:
            await websocket.send_json({"type": "error", "message": "internal_error"})
            await websocket.close(code=1011)
        except Exception:  # noqa: BLE001
            pass


# ---------------------------------------------------------------------------
# `python main.py` convenience launcher
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.is_local,
    )
