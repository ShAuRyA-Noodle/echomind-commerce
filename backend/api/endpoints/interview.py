"""Echomind Commerce - `/api/interview/*` endpoints + WS handler.

Wired to the Socratic engine modules (phase manager, frontier scorer,
extractor, question generator). The WS handler lives on the FastAPI app
(see `main.py`); this router exposes the REST hooks for session lifecycle.

Endpoints
    POST /api/interview/start              - create session, return ws_url
    POST /api/interview/{session_id}/end   - finalize session, return summary
    POST /api/interview/{session_id}/extract - text-mode chunk extraction (no audio)
    GET  /api/interview/{session_id}/next  - next question via frontier scoring
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from api.schemas import NotImplementedResponse, SocraticPhase
from core.socratic.extractor import extract_chunk
from core.socratic.question_gen import generate_question
from graph.operations import deterministic_id, graph_stats, upsert_typed

logger = logging.getLogger("echomind.api.interview")
router = APIRouter(prefix="/interview", tags=["interview"])


class StartInterviewRequest(BaseModel):
    domain: str = Field(default="specialty coffee retail")
    merchant_name: str | None = None


class ExtractChunkRequest(BaseModel):
    transcript_chunk: str = Field(..., min_length=4)
    phase: SocraticPhase = Field(default="brand_mapping")
    phase_name: str = Field(default="Brand Mapping")
    domain: str = Field(default="specialty coffee retail")
    recent_entity_names: list[str] = Field(default_factory=list)
    existing_truths_summary: str = Field(default="")


class NextQuestionRequest(BaseModel):
    phase: SocraticPhase = Field(default="brand_mapping")
    question_count: int = Field(default=0, ge=0)
    elapsed_minutes: float = Field(default=0.0, ge=0.0)
    domain: str = Field(default="specialty coffee retail")
    top_3_frontiers: list[dict[str, Any]] = Field(default_factory=list)
    last_5_qa_pairs: list[dict[str, str]] = Field(default_factory=list)
    underrepresented_tacit_category: str | None = None


@router.post("/start", summary="Create a Socratic interview session, return WebSocket URL")
async def start_interview(req: StartInterviewRequest) -> dict[str, Any]:
    """Issue a stable session_id; the WS handler in main.py picks it up."""
    started = datetime.now(timezone.utc)
    session_id = deterministic_id("session", started.isoformat(), req.domain)
    return {
        "status": "ok",
        "session_id": session_id,
        "ws_url": f"/api/interview/ws/{session_id}",
        "domain": req.domain,
        "merchant_name": req.merchant_name,
        "started_at": started.isoformat(),
    }


@router.post(
    "/{session_id}/extract",
    summary="Text-mode extraction over a transcript chunk (no audio path)",
)
async def extract_text_chunk(session_id: str, req: ExtractChunkRequest) -> dict[str, Any]:
    """Run Gemini Flash extraction over a transcript chunk + persist to Neo4j."""
    result = extract_chunk(
        transcript_chunk=req.transcript_chunk,
        phase=req.phase,
        phase_name=req.phase_name,
        domain=req.domain,
        recent_entity_names=req.recent_entity_names,
        existing_truths_summary=req.existing_truths_summary,
    )
    for t in result.merchant_truths:
        await upsert_typed(t, "MerchantTruth")
    for d in result.decisions:
        await upsert_typed(d, "Decision")
    for p in result.patterns:
        await upsert_typed(p, "Pattern")
    for q in result.customer_questions:
        await upsert_typed(q, "CustomerQuestion")
    for pol in result.policies:
        await upsert_typed(pol, "Policy")
    return {
        "status": "ok",
        "session_id": session_id,
        "extracted": {
            "merchant_truths": len(result.merchant_truths),
            "decisions": len(result.decisions),
            "patterns": len(result.patterns),
            "customer_questions": len(result.customer_questions),
            "policies": len(result.policies),
        },
        "edges_proposed": len(result.edges),
        "parse_failed": result.parse_failed,
    }


@router.post("/{session_id}/next", summary="Generate next Socratic question via frontier scoring")
async def next_question(session_id: str, req: NextQuestionRequest) -> dict[str, Any]:
    """Render the next-question prompt + return the generated question."""
    stats = await graph_stats()
    q = generate_question(
        phase=req.phase,
        question_count=req.question_count,
        elapsed_minutes=req.elapsed_minutes,
        domain=req.domain,
        graph_stats=stats,
        top_3_frontiers=req.top_3_frontiers,
        last_5_qa_pairs=req.last_5_qa_pairs,
        underrepresented_tacit_category=req.underrepresented_tacit_category,
    )
    return {
        "status": "ok",
        "session_id": session_id,
        "question": q.question,
        "follow_up_if_brief": q.follow_up_if_brief,
        "targets_frontier_id": q.targets_frontier_id,
        "targets_tacit_category": q.targets_tacit_category,
        "phase_style_used": q.phase_style_used,
        "rationale": q.rationale,
        "uncertainty_notes": q.uncertainty_notes,
    }


@router.post(
    "/{session_id}/end",
    response_model=NotImplementedResponse,
    summary="Finalize the interview session, emit summary",
)
async def end_interview(session_id: str) -> NotImplementedResponse:
    """Final-pass extraction + persist summary blob (Firestore v2)."""
    return NotImplementedResponse(
        endpoint=f"POST /api/interview/{session_id}/end",
        detail="Final pass extraction + Firestore session summary, v2 work.",
    )
