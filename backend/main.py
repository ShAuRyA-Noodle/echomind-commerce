"""Echomind Commerce - FastAPI application entrypoint.

Run locally with::

    uvicorn main:app --reload --host 0.0.0.0 --port 8000

The app:
    * mounts every router from `api/endpoints` under `/api`
    * exposes `/health` (pings Neo4j + does one Gemini call)
    * registers the `/api/interview/ws/{session_id}` websocket handler
    * uses a lifespan handler to bring up + tear down Neo4j + Firebase
    * applies CORS for the Next.js dev server (http://localhost:3000)
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
from config.settings import settings
from graph.neo4j_client import neo4j_client
from services.firebase_service import firebase_service
from services.llm_service import llm_service

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

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

    # Neo4j driver - verify_connectivity() runs inside connect()
    try:
        await neo4j_client.connect()
        logger.info("startup.neo4j.ok")
    except Exception:  # noqa: BLE001 - degraded start is acceptable in dev
        logger.exception("startup.neo4j.failed - backend will run degraded")

    # Firebase Admin - optional in local dev if credentials missing
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Mount routers under /api
# ---------------------------------------------------------------------------

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
api_router.include_router(debug.router)
app.include_router(api_router)


# ---------------------------------------------------------------------------
# Root + health
# ---------------------------------------------------------------------------


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
    # 200 even when degraded so /health is always observable; the body tells the truth.
    return JSONResponse(content=body.model_dump(), status_code=200)


# ---------------------------------------------------------------------------
# WebSocket handlers (mounted on app, not on routers, per FastAPI conventions)
# ---------------------------------------------------------------------------


@app.websocket("/api/interview/ws/{session_id}")
async def interview_ws(websocket: WebSocket, session_id: str) -> None:
    """Live interview WebSocket - stub.

    Per WINNING_PLAN §5.5 the eventual contract is bidirectional:
        in:  audio_chunk, text_input, control
        out: interim_transcript, final_transcript, question, extraction,
             phase_change, graph_update, progress

    Today this handler accepts the connection, replies with a structured
    `not_yet_implemented` envelope, echoes inbound messages so the frontend
    can be developed against a live socket, and closes cleanly.
    """
    await websocket.accept()
    logger.info("interview.ws.connected session_id=%s", session_id)
    try:
        await websocket.send_json(
            {
                "status": "not_yet_implemented",
                "endpoint": f"WS /api/interview/ws/{session_id}",
                "detail": (
                    "Echo-mode stub. Real handler streams STT events and Socratic "
                    "questions; will be wired with core/socratic/engine.py."
                ),
            }
        )
        while True:
            message = await websocket.receive_json()
            await websocket.send_json(
                {
                    "type": "echo",
                    "session_id": session_id,
                    "received": message,
                }
            )
    except WebSocketDisconnect:
        logger.info("interview.ws.disconnected session_id=%s", session_id)
    except Exception:  # noqa: BLE001
        logger.exception("interview.ws.error session_id=%s", session_id)
        try:
            await websocket.close(code=1011)
        except Exception:  # noqa: BLE001
            pass


@app.websocket("/api/simulate/ws/{run_id}")
async def simulate_ws(websocket: WebSocket, run_id: str) -> None:
    """Agent-swarm streaming WS - stub. See WINNING_PLAN §5.5 + §15.4."""
    await websocket.accept()
    logger.info("simulate.ws.connected run_id=%s", run_id)
    try:
        await websocket.send_json(
            {
                "status": "not_yet_implemented",
                "endpoint": f"WS /api/simulate/ws/{run_id}",
                "detail": (
                    "Will stream live token-by-token outputs from each agent in the swarm "
                    "(Gemini, Llama, Qwen, DeepSeek). Wires to core/agents/runner.py."
                ),
            }
        )
        while True:
            message = await websocket.receive_json()
            await websocket.send_json({"type": "echo", "run_id": run_id, "received": message})
    except WebSocketDisconnect:
        logger.info("simulate.ws.disconnected run_id=%s", run_id)
    except Exception:  # noqa: BLE001
        logger.exception("simulate.ws.error run_id=%s", run_id)
        try:
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
