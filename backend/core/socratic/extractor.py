"""Echomind Commerce - Socratic transcript extractor.

Wraps `EXTRACTION_PROMPT_FLASH` (in `config/prompts.py`). Takes a transcript
chunk + interview context, returns typed `MerchantTruth`, `Decision`,
`Pattern`, `CustomerQuestion`, `Policy` rows + edge intents.

The extractor never INVENTS - if the chunk yields nothing, it returns empty
arrays. Each MerchantTruth carries a `verbatim_quote` for the audit trail.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from api.schemas import (
    CustomerQuestion,
    Decision,
    MerchantTruth,
    Pattern,
    Policy,
    SocraticPhase,
)
from config.prompts import EXTRACTION_PROMPT_FLASH
from graph.operations import deterministic_id
from services.llm_service import llm_service, safe_json_loads

logger = logging.getLogger("echomind.socratic.extractor")


@dataclass
class ExtractionResult:
    """One extraction pass over one transcript chunk."""

    merchant_truths: list[MerchantTruth] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    patterns: list[Pattern] = field(default_factory=list)
    customer_questions: list[CustomerQuestion] = field(default_factory=list)
    policies: list[Policy] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    parse_failed: bool = False
    raw_text: str = ""


def _coerce_truth(d: dict[str, Any], phase: SocraticPhase) -> MerchantTruth | None:
    statement = d.get("statement")
    if not statement:
        return None
    tid = deterministic_id("truth", statement)
    return MerchantTruth(
        id=tid,
        statement=str(statement),
        verbatim_quote=d.get("verbatim_quote"),
        category=str(d.get("category", "positioning")).lower(),  # type: ignore[arg-type]
        tacit_category=str(d.get("tacit_category", "procedural")).lower(),  # type: ignore[arg-type]
        tacit_level=str(d.get("tacit_level", "explicit")).lower(),  # type: ignore[arg-type]
        source_phase=phase,
        confidence=float(d.get("confidence", 0.7) or 0.7),
        aliases=[d["alias_of_existing"]] if d.get("alias_of_existing") else [],
    )


def _coerce_decision(d: dict[str, Any]) -> Decision | None:
    if not d.get("question") or not d.get("outcome"):
        return None
    did = deterministic_id("decision", d["question"], d["outcome"])
    return Decision(
        id=did,
        question=str(d["question"]),
        context=d.get("context"),
        outcome=str(d["outcome"]),
        conditions=[str(c) for c in d.get("conditions", [])],
        frequency=str(d.get("frequency", "usually")).lower(),  # type: ignore[arg-type]
        confidence=float(d.get("confidence", 0.7) or 0.7),
    )


def _coerce_pattern(d: dict[str, Any]) -> Pattern | None:
    if not d.get("name") or not d.get("description"):
        return None
    pid = deterministic_id("pattern", d["name"])
    return Pattern(
        id=pid,
        name=str(d["name"]),
        description=str(d["description"]),
        indicators=[str(i) for i in d.get("indicators", [])],
        typical_response=d.get("typical_response"),
        confidence=float(d.get("confidence", 0.7) or 0.7),
    )


def _coerce_customer_question(d: dict[str, Any]) -> CustomerQuestion | None:
    if not d.get("question"):
        return None
    qid = deterministic_id("cq", d["question"])
    freq_raw = d.get("frequency", 1)
    try:
        freq = int(freq_raw) if isinstance(freq_raw, (int, float)) else 1
    except (TypeError, ValueError):
        freq = 1
    return CustomerQuestion(
        id=qid,
        question=str(d["question"]),
        frequency=max(1, freq),
        intent_class=str(d.get("intent_class", "discover")).lower(),  # type: ignore[arg-type]
    )


def _coerce_policy(d: dict[str, Any]) -> Policy | None:
    if not d.get("text"):
        return None
    pid = deterministic_id("policy", d.get("type", "other"), d["text"])
    return Policy(
        id=pid,
        type=str(d.get("type", "other")).lower(),  # type: ignore[arg-type]
        text=str(d["text"]),
        scope=str(d.get("scope", "global")).lower() if d.get("scope") else "global",  # type: ignore[arg-type]
        exceptions=[str(e) for e in d.get("exceptions", [])],
    )


def extract_chunk(
    *,
    transcript_chunk: str,
    phase: SocraticPhase,
    phase_name: str,
    domain: str = "specialty coffee retail",
    recent_entity_names: list[str] | None = None,
    existing_truths_summary: str = "",
) -> ExtractionResult:
    """Run Gemini Flash extraction over a transcript chunk."""
    prompt = EXTRACTION_PROMPT_FLASH.format(
        domain=domain,
        transcript_chunk=transcript_chunk,
        phase=phase,
        phase_name=phase_name,
        recent_entity_names=recent_entity_names or [],
        existing_truths_summary=existing_truths_summary,
    )
    text = ""
    try:
        text = llm_service.gemini_flash(prompt)
    except Exception as exc:  # noqa: BLE001
        logger.exception("extractor.gemini_failed exc=%r", exc)
        return ExtractionResult(parse_failed=True, raw_text=text)

    parsed = safe_json_loads(text)
    if not isinstance(parsed, dict):
        logger.warning("extractor.parse_failed")
        return ExtractionResult(parse_failed=True, raw_text=text)

    truths = [t for t in (_coerce_truth(d, phase) for d in parsed.get("merchant_truths", [])) if t]
    decisions = [d for d in (_coerce_decision(x) for x in parsed.get("decisions", [])) if d]
    patterns = [p for p in (_coerce_pattern(x) for x in parsed.get("patterns", [])) if p]
    customer_questions = [
        q for q in (_coerce_customer_question(x) for x in parsed.get("customer_questions", [])) if q
    ]
    policies = [p for p in (_coerce_policy(x) for x in parsed.get("policies", [])) if p]
    edges = [e for e in parsed.get("edges", []) if isinstance(e, dict)]

    return ExtractionResult(
        merchant_truths=truths,
        decisions=decisions,
        patterns=patterns,
        customer_questions=customer_questions,
        policies=policies,
        edges=edges,
        parse_failed=False,
        raw_text=text,
    )


__all__ = ["ExtractionResult", "extract_chunk"]
