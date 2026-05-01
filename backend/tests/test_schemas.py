"""Schema round-trip tests.

Verifies that every pydantic model in `api/schemas.py` accepts the canonical
sample payload from `conftest.py::sample_node_payloads` and that:

    1. The 11 node types in `NODE_MODELS` round-trip cleanly.
    2. The 12 edge types in `EDGE_MODELS` accept a minimal `{from_id, to_id}`.
    3. The 5 calibration labels are exactly the WINNING_PLAN §9.3 set.
    4. The 5 gap types are exactly the WINNING_PLAN §16.1 set.
    5. The 6 tacit-knowledge categories are exactly the WINNING_PLAN §7 set.
    6. The 5 fix types are exactly the WINNING_PLAN §17.1 set.
    7. The reasoning trace structure matches WINNING_PLAN §11.

If a future change drifts any enum away from its canonical set, this file
fails - by design.
"""

from __future__ import annotations

from typing import Any, get_args

import pytest

from api.schemas import (
    EDGE_MODELS,
    NODE_MODELS,
    CalibrationBlock,
    CalibrationLabel,
    ContradictionResolution,
    FixType,
    GapType,
    KnowledgeSource,
    PredictedDelta,
    ReasoningStep,
    ReasoningTrace,
    SocraticPhase,
    TacitCategory,
    TruthCategory,
)


# ---------------------------------------------------------------------------
# Enum canonical-set tests - drift detector
# ---------------------------------------------------------------------------


def test_calibration_labels_are_canonical() -> None:
    """WINNING_PLAN §9.3 defines exactly these 5 labels."""
    assert set(get_args(CalibrationLabel)) == {
        "certain",
        "confident",
        "uncertain",
        "low_confidence",
        "dont_know",
    }


def test_gap_types_are_canonical() -> None:
    """WINNING_PLAN §16.1 defines exactly these 5 gap types."""
    assert set(get_args(GapType)) == {
        "omission",
        "contradiction",
        "ambiguity",
        "hallucination",
        "dark_zone",
    }


def test_tacit_categories_are_canonical() -> None:
    """WINNING_PLAN §7 defines exactly these 6 tacit-knowledge categories."""
    assert set(get_args(TacitCategory)) == {
        "procedural",
        "conditional_heuristic",
        "experiential_pattern",
        "intuitive_judgment",
        "edge_case_knowledge",
        "meta_knowledge",
    }


def test_truth_categories_are_canonical() -> None:
    """WINNING_PLAN §6.1 MerchantTruth row defines exactly these 5 about-ness categories."""
    assert set(get_args(TruthCategory)) == {
        "positioning",
        "audience",
        "edge_case",
        "relationship",
        "style",
    }


def test_fix_types_are_canonical() -> None:
    """WINNING_PLAN §17.1 defines exactly these 5 fix types."""
    assert set(get_args(FixType)) == {
        "copy_rewrite",
        "faq_add",
        "policy_clarify",
        "metafield_add",
        "structured_data",
    }


def test_socratic_phases_are_canonical() -> None:
    """WINNING_PLAN §8.1 defines exactly these 5 commerce phases."""
    assert set(get_args(SocraticPhase)) == {
        "brand_mapping",
        "product_truths",
        "customer_reality",
        "policy_edge_cases",
        "trust_signals",
    }


# ---------------------------------------------------------------------------
# Node round-trip tests
# ---------------------------------------------------------------------------


def test_node_models_cover_all_eleven_types() -> None:
    """The NODE_MODELS registry must contain all 11 node types from §6.1."""
    assert set(NODE_MODELS.keys()) == {
        "Product",
        "Policy",
        "TrustSignal",
        "MerchantTruth",
        "Decision",
        "Pattern",
        "CustomerQuestion",
        "BuyerPrompt",
        "AgentRepresentation",
        "Gap",
        "FixSuggestion",
    }


@pytest.mark.parametrize(
    "node_type",
    [
        "Product",
        "Policy",
        "TrustSignal",
        "MerchantTruth",
        "Decision",
        "Pattern",
        "CustomerQuestion",
        "BuyerPrompt",
        "AgentRepresentation",
        "Gap",
        "FixSuggestion",
    ],
)
def test_node_round_trip(
    node_type: str,
    sample_node_payloads: dict[str, dict[str, Any]],
) -> None:
    """Every node accepts its sample payload and round-trips losslessly."""
    payload = sample_node_payloads[node_type]
    Model = NODE_MODELS[node_type]
    instance = Model.model_validate(payload)
    dumped = instance.model_dump()
    # Re-validate the dumped form to confirm no drift on serialize.
    re_instance = Model.model_validate(dumped)
    assert re_instance == instance


def test_merchant_truth_carries_both_orthogonal_categories(
    sample_node_payloads: dict[str, dict[str, Any]],
) -> None:
    """A MerchantTruth carries BOTH category (about-ness) and tacit_category (taxonomy)."""
    truth = NODE_MODELS["MerchantTruth"].model_validate(
        sample_node_payloads["MerchantTruth"]
    )
    assert truth.category == "positioning"  # type: ignore[attr-defined]
    assert truth.tacit_category == "edge_case_knowledge"  # type: ignore[attr-defined]
    assert truth.tacit_level == "deeply-tacit"  # type: ignore[attr-defined]
    assert truth.verbatim_quote is not None  # type: ignore[attr-defined]


def test_extra_fields_are_rejected() -> None:
    """`_Base` sets `extra='forbid'` - schema drift surfaces immediately."""
    with pytest.raises(Exception):
        NODE_MODELS["Product"].model_validate(
            {"id": "p1", "title": "x", "shenanigans": True}
        )


# ---------------------------------------------------------------------------
# Edge round-trip tests
# ---------------------------------------------------------------------------


def test_edge_models_cover_all_twelve_types() -> None:
    """The EDGE_MODELS registry must contain all 12 edge types from §6.2."""
    assert set(EDGE_MODELS.keys()) == {
        "DESCRIBES",
        "COVERS",
        "MENTIONS",
        "MISREPRESENTS",
        "REVEALS",
        "HARMS",
        "FIXES",
        "CONTRADICTS",
        "TRIGGERS",
        "EXCEPTION_TO",
        "ANSWERS",
        "SIMILAR_TO",
    }


@pytest.mark.parametrize("edge_type", list(EDGE_MODELS.keys()))
def test_edge_minimal_payload(edge_type: str) -> None:
    """Every edge type accepts a minimal {type, from_id, to_id} payload."""
    Model = EDGE_MODELS[edge_type]
    instance = Model.model_validate(
        {"type": edge_type, "from_id": "a", "to_id": "b"}
    )
    dumped = instance.model_dump()
    assert dumped["type"] == edge_type
    assert dumped["from_id"] == "a"
    assert dumped["to_id"] == "b"


# ---------------------------------------------------------------------------
# Reasoning-trace structure tests (WINNING_PLAN §11)
# ---------------------------------------------------------------------------


def test_reasoning_trace_full_payload() -> None:
    """The reasoning trace JSON shape from §11 round-trips cleanly."""
    payload = {
        "answer": "We position our Yirgacheffe as chocolate-forward.",
        "reasoning_chain": [
            {
                "step": 1,
                "claim": "MerchantTruth says chocolate-forward.",
                "source_node_ids": ["truth_yirg_chocolate_forward"],
                "confidence": 0.92,
            },
            {
                "step": 2,
                "claim": "Three agents say fruity-acidic.",
                "source_node_ids": [
                    "agent_repr_llama_yirg_001",
                    "agent_repr_qwen_yirg_001",
                    "agent_repr_deepseek_yirg_001",
                ],
                "confidence": 0.88,
            },
        ],
        "knowledge_sources_used": [
            {
                "node_id": "truth_yirg_chocolate_forward",
                "type": "MerchantTruth",
                "relevance": 0.95,
            }
        ],
        "contradictions_resolved": [
            {
                "between": ["truth_yirg_chocolate_forward", "agent_repr_llama_yirg_001"],
                "resolution": "Trust merchant; agent description omits 'chocolate'.",
            }
        ],
        "confidence": 0.83,
        "calibration": "confident",
        "uncertainty_type": None,
    }
    trace = ReasoningTrace.model_validate(payload)
    assert trace.calibration == "confident"
    assert len(trace.reasoning_chain) == 2
    assert trace.contradictions_resolved[0].between == [
        "truth_yirg_chocolate_forward",
        "agent_repr_llama_yirg_001",
    ]


def test_reasoning_trace_dont_know_payload() -> None:
    """The §16.3 'I don't know' fallback is a valid trace, not an error path."""
    payload = {
        "answer": "We don't have enough information in our knowledge graph to answer that.",
        "reasoning_chain": [],
        "knowledge_sources_used": [],
        "contradictions_resolved": [],
        "confidence": 0.0,
        "calibration": "dont_know",
        "uncertainty_type": "out_of_domain",
    }
    trace = ReasoningTrace.model_validate(payload)
    assert trace.calibration == "dont_know"
    assert trace.uncertainty_type == "out_of_domain"


def test_predicted_delta_is_a_range_not_a_point() -> None:
    """Fix predictions emit ranges, per WINNING_PLAN §18.1 + §19.3."""
    delta = PredictedDelta.model_validate(
        {"low": 0.4, "high": 0.65, "metric": "agent_surface_rate_pp"}
    )
    assert delta.high >= delta.low


def test_calibration_block_full_payload() -> None:
    """CalibrationBlock carries the §9.3 inputs + the bucketed label."""
    block = CalibrationBlock.model_validate(
        {
            "raw_confidence": 0.85,
            "evidence_factor": 0.7,
            "coverage_factor": 0.6,
            "adjusted_confidence": 0.73,
            "label": "confident",
        }
    )
    assert block.label == "confident"


def test_knowledge_source_open_node_type() -> None:
    """KnowledgeSource keeps `type` as plain str so it doesn't drift with new nodes."""
    src = KnowledgeSource.model_validate(
        {"node_id": "x", "type": "FuturePlannedNodeType", "relevance": 0.5}
    )
    assert src.type == "FuturePlannedNodeType"


def test_reasoning_step_confidence_is_bounded() -> None:
    """Step confidence is clamped to [0, 1]; out-of-range is rejected."""
    with pytest.raises(Exception):
        ReasoningStep.model_validate(
            {"step": 1, "claim": "x", "source_node_ids": [], "confidence": 1.5}
        )


def test_contradiction_resolution_payload() -> None:
    """ContradictionResolution carries between+resolution exactly."""
    res = ContradictionResolution.model_validate(
        {"between": ["a", "b"], "resolution": "Trust merchant."}
    )
    assert res.resolution == "Trust merchant."
