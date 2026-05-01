"""pytest fixtures for Echomind Commerce backend tests.

These fixtures favor pure / in-memory behavior - no real Neo4j connection,
no real Gemini call. The runtime smoke tests (`make health`, `python -m
services.llm_service`) cover real-network paths.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(scope="session", autouse=True)
def _ensure_backend_on_sys_path() -> None:
    """Make `backend/` importable when pytest is invoked from repo root."""
    backend_dir = Path(__file__).resolve().parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))


@pytest.fixture(scope="session", autouse=True)
def _safe_env() -> None:
    """Ensure tests never accidentally use real credentials.

    pydantic-settings will pick up `.env` from disk by default. We blank
    secret-looking vars during tests so a forgotten `os.getenv` doesn't fire
    a real API call.
    """
    keys = (
        "GEMINI_API_KEY",
        "OPENROUTER_API_KEY",
        "NEO4J_PASSWORD",
        "SHOPIFY_ADMIN_ACCESS_TOKEN",
        "FIREBASE_API_KEY",
    )
    for k in keys:
        if os.getenv(k):
            # Replace with deterministic test value rather than empty string so
            # downstream `if settings.X` truthiness checks still flow normally.
            os.environ[k] = f"test-{k.lower()}"


@pytest.fixture
def sample_node_payloads() -> dict[str, dict[str, Any]]:
    """Minimal-but-valid payloads for every node type in the schema.

    Used to verify pydantic round-trip + Cypher MERGE compatibility.
    """
    return {
        "Product": {
            "id": "prod_yirgacheffe_250g",
            "title": "Ethiopia Yirgacheffe - 250g",
            "description": "Fruity floral profile, vibrant acidity, jasmine notes.",
            "price": 18.0,
            "currency": "USD",
            "tags": ["single-origin", "ethiopia", "yirgacheffe"],
            "confidence": 1.0,
        },
        "Policy": {
            "id": "policy_shipping_global",
            "type": "shipping",
            "text": "Free shipping on US orders over $40.",
            "scope": "global",
        },
        "TrustSignal": {
            "id": "trust_review_142",
            "type": "review",
            "value": "Best Yirgacheffe I've had outside of Addis.",
            "attached_to": "prod_yirgacheffe_250g",
        },
        "MerchantTruth": {
            "id": "truth_yirg_chocolate_forward",
            "statement": "Our Yirgacheffe is chocolate-forward, not the typical bright/floral profile.",
            "verbatim_quote": "It's chocolate-forward, honestly - not what most people expect from Yirgacheffe.",
            "category": "positioning",
            "tacit_category": "edge_case_knowledge",
            "tacit_level": "deeply-tacit",
            "source_phase": "product_truths",
            "confidence": 0.92,
        },
        "Decision": {
            "id": "decision_returns_opened_bag",
            "question": "Refund or exchange opened bag?",
            "outcome": "case_by_case",
            "conditions": ["bag opened", "within 14 days", "defect reported"],
            "frequency": "sometimes",
        },
        "Pattern": {
            "id": "pattern_ethiopian_to_kenyan",
            "name": "Ethiopian → Kenyan upgrade",
            "description": "Customers who buy Ethiopian come back for Kenyan within 6 weeks.",
            "indicators": ["first purchase = Yirgacheffe", "second order"],
            "typical_response": "Suggest Kenya AA Nyeri.",
        },
        "CustomerQuestion": {
            "id": "cq_yirg_for_cold_brew",
            "question": "Is the Yirgacheffe good for cold brew?",
            "frequency": 12,
            "intent_class": "compare",
        },
        "BuyerPrompt": {
            "id": "bp_chocolatey_morning",
            "prompt_text": "I want a chocolatey single-origin under $25 for pour-over.",
            "intent_class": "discover",
            "length_bucket": "medium",
            "is_adversarial": False,
        },
        "AgentRepresentation": {
            "id": "agent_repr_llama_yirg_001",
            "agent_model": "meta-llama/llama-3.3-70b-instruct:free",
            "buyer_prompt_id": "bp_chocolatey_morning",
            "response_text": "Try Ethiopia Yirgacheffe - fruity, floral.",
            "surfaced_products": ["prod_yirgacheffe_250g"],
            "confidence_in_recommendation": 0.71,
        },
        "Gap": {
            "id": "gap_yirg_chocolate_contradiction",
            "type": "contradiction",
            "severity": 0.83,
            "revenue_impact_usd_monthly": 1840.0,
            "calibration_label": "confident",
            "affected_products": ["prod_yirgacheffe_250g"],
        },
        "FixSuggestion": {
            "id": "fix_yirg_chocolate_001",
            "gap_id": "gap_yirg_chocolate_contradiction",
            "fix_type": "copy_rewrite",
            "proposed_text": "Yirgacheffe - chocolate-forward, low-acidity, Bourbon varietal.",
            "applied": False,
        },
    }
