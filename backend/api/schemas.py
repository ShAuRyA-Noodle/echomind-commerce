"""Echomind Commerce - pydantic schemas (one source of typing truth).

Maps verbatim to:
    * WINNING_PLAN.md §6.1 - 11 node types
    * WINNING_PLAN.md §6.2 - 12 edge types
    * WINNING_PLAN.md §7   - Tacit Knowledge Taxonomy (6 categories)
    * WINNING_PLAN.md §9.3 - Calibration buckets (5 labels)
    * WINNING_PLAN.md §16  - Five gap types
    * WINNING_PLAN.md §17  - Five fix types

Conventions:
    * Enums use ``Literal`` so every accepted value is documented in the type
      signature and validated at the API boundary.
    * Embedding-bearing nodes (``Product``, ``MerchantTruth``,
      ``CustomerQuestion``, ``BuyerPrompt``) carry a 768-dim float vector.
    * All node IDs are stable, content-derived strings - see
      ``graph/operations.py`` for the deterministic-id construction.

Adding a field: always preserve backwards-compatible defaults (``= None`` /
``= Field(default_factory=list)``) so partial payloads from upstream extractors
don't fail validation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Shared types / enums
# ---------------------------------------------------------------------------

# Tacit-level depth, per Echomind blueprint §2.3 + WINNING_PLAN §7.
TacitLevel = Literal["explicit", "semi-tacit", "deeply-tacit"]

# Tacit Knowledge Taxonomy - the SIX categories from WINNING_PLAN §7.
# Stored as snake_case for Python hygiene; LLM prompts emit these verbatim.
TacitCategory = Literal[
    "procedural",
    "conditional_heuristic",
    "experiential_pattern",
    "intuitive_judgment",
    "edge_case_knowledge",
    "meta_knowledge",
]

# What the MerchantTruth is ABOUT, per WINNING_PLAN §6.1 schema row.
# Distinct from TacitCategory - the two are orthogonal: a single truth has
# both an "about-ness" (positioning) and a tacit-knowledge-type
# (conditional_heuristic).
TruthCategory = Literal[
    "positioning",
    "audience",
    "edge_case",
    "relationship",
    "style",
]

PolicyType = Literal["return", "shipping", "warranty", "exchange", "other"]
PolicyScope = Literal["global", "specific"]
TrustSignalType = Literal["review", "badge", "cert", "testimonial"]
DecisionFrequency = Literal["always", "usually", "sometimes", "rarely"]
IntentClass = Literal["discover", "compare", "objection", "post-purchase"]

# Five gap types, WINNING_PLAN §16.1.
GapType = Literal[
    "omission",
    "contradiction",
    "ambiguity",
    "hallucination",
    "dark_zone",
]

# Five-bucket calibration labels, WINNING_PLAN §9.3.
# These are the canonical labels used everywhere in the system.
CalibrationLabel = Literal[
    "certain",
    "confident",
    "uncertain",
    "low_confidence",
    "dont_know",
]

# Why a calibration is uncertain or "don't know" - distinguishes
# "data exists but is sparse / contradictory" from "no relevant data".
UncertaintyType = Literal[
    "data_sparse",
    "data_contradictory",
    "out_of_domain",
]

# Five fix types, WINNING_PLAN §17.1.
FixType = Literal[
    "copy_rewrite",
    "faq_add",
    "policy_clarify",
    "metafield_add",
    "structured_data",
]

# Twelve edge types, WINNING_PLAN §6.2.
EdgeType = Literal[
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
]

# Five Socratic interview phases, WINNING_PLAN §8.1.
SocraticPhase = Literal[
    "brand_mapping",
    "product_truths",
    "customer_reality",
    "policy_edge_cases",
    "trust_signals",
]

# Sentiment buckets used on MENTIONS edges.
Sentiment = Literal["positive", "neutral", "negative"]


class _Base(BaseModel):
    """Project base model - disallow unknown fields by default.

    ``extra="forbid"`` is intentional. It surfaces upstream LLM schema drift
    immediately at the API boundary instead of silently swallowing fields.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


# ---------------------------------------------------------------------------
# Reasoning Trace primitives - WINNING_PLAN §11
# ---------------------------------------------------------------------------


class ReasoningStep(_Base):
    """One step in a reasoning chain - claim + cited source nodes + confidence."""

    step: int
    claim: str
    source_node_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)


class KnowledgeSource(_Base):
    """Pointer to a source node + relevance score for the audit trail."""

    node_id: str
    type: str  # NodeType label; not Literal to keep the trace tolerant.
    relevance: float = Field(ge=0.0, le=1.0, default=0.5)


class ContradictionResolution(_Base):
    """Recorded resolution between two contradicting nodes."""

    between: list[str]  # exactly two node ids
    resolution: str


class CalibrationBlock(_Base):
    """Calibration inputs + label, per WINNING_PLAN §9.3."""

    raw_confidence: float = Field(ge=0.0, le=1.0)
    evidence_factor: float = Field(ge=0.0, le=1.0, default=0.0)
    coverage_factor: float = Field(ge=0.0, le=1.0, default=0.0)
    adjusted_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    label: CalibrationLabel = "uncertain"


class ReasoningTrace(_Base):
    """Full reasoning trace JSON, exactly the §11 schema."""

    answer: str | None = None
    reasoning_chain: list[ReasoningStep] = Field(default_factory=list)
    knowledge_sources_used: list[KnowledgeSource] = Field(default_factory=list)
    contradictions_resolved: list[ContradictionResolution] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    calibration: CalibrationLabel = "uncertain"
    uncertainty_type: UncertaintyType | None = None


# ---------------------------------------------------------------------------
# Predicted-delta envelope - used by FixSuggestion + retest panel
# ---------------------------------------------------------------------------


class PredictedDelta(_Base):
    """Range-not-point estimate of a fix's expected impact."""

    low: float
    high: float
    metric: str = "agent_surface_rate_pp"
    rationale: str | None = None


# ---------------------------------------------------------------------------
# 11 Node types (WINNING_PLAN §6.1)
# ---------------------------------------------------------------------------


class Product(_Base):
    """Shopify product - node type #1."""

    id: str
    shopify_gid: str | None = None
    title: str
    description: str | None = None
    price: float | None = None
    currency: str | None = None
    image_urls: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    options: dict[str, Any] | None = None
    variants_summary: str | None = None
    embedding: list[float] | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    ingested_at: datetime | None = None


class Policy(_Base):
    """Shopify page or metafield-derived policy - node type #2."""

    id: str
    type: PolicyType
    text: str
    scope: PolicyScope = "global"
    exceptions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    source_url: str | None = None


class TrustSignal(_Base):
    """Review / badge / cert / testimonial - node type #3."""

    id: str
    type: TrustSignalType
    value: str
    attached_to: str | None = None  # node id of attached entity (e.g. Product.id)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class MerchantTruth(_Base):
    """Tacit knowledge surfaced via interview - node type #4 (preserved Echomind).

    Carries TWO orthogonal classifications:
        * ``category`` - what the truth is ABOUT (positioning / audience / etc.)
        * ``tacit_category`` - the Tacit Knowledge Taxonomy (Procedural /
          Conditional Heuristic / Experiential Pattern / Intuitive Judgment /
          Edge Case Knowledge / Meta-Knowledge), per WINNING_PLAN §7.

    ``verbatim_quote`` anchors every truth back to the exact phrase the
    merchant uttered - load-bearing for the audit trail.
    """

    id: str
    statement: str
    verbatim_quote: str | None = None
    category: TruthCategory
    tacit_category: TacitCategory
    tacit_level: TacitLevel
    source_phase: SocraticPhase
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    embedding: list[float] | None = None
    aliases: list[str] = Field(default_factory=list)
    parse_failed: bool = False


class Decision(_Base):
    """Decision-tree fragment captured during interview - node type #5 (preserved)."""

    id: str
    question: str
    context: str | None = None
    outcome: str
    conditions: list[str] = Field(default_factory=list)
    frequency: DecisionFrequency = "usually"
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)


class Pattern(_Base):
    """Recurring customer behavior pattern - node type #6 (preserved)."""

    id: str
    name: str
    description: str
    indicators: list[str] = Field(default_factory=list)
    typical_response: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)


class CustomerQuestion(_Base):
    """Real-world customer question - node type #7."""

    id: str
    question: str
    frequency: int = 1
    intent_class: IntentClass = "discover"
    embedding: list[float] | None = None


class BuyerPrompt(_Base):
    """Generated buyer-intent prompt for the agent swarm - node type #8."""

    id: str
    prompt_text: str
    intent_class: IntentClass
    length_bucket: Literal["short", "medium", "long"] = "medium"
    is_adversarial: bool = False
    generated_from_truths: list[str] = Field(default_factory=list)
    embedding: list[float] | None = None


class AgentRepresentation(_Base):
    """Captured agent output for one (agent, prompt) pair - node type #9."""

    id: str
    agent_model: str
    buyer_prompt_id: str
    response_text: str
    surfaced_products: list[str] = Field(default_factory=list)
    cited_policies: list[str] = Field(default_factory=list)
    confidence_in_recommendation: float | None = None
    latency_ms: int | None = None
    captured_at: datetime | None = None
    parse_failed: bool = False


class Gap(_Base):
    """Detected gap between merchant truth and agent representation - node type #10.

    ``calibration_label`` carries the WINNING_PLAN §9.3 5-bucket label -
    ``certain | confident | uncertain | low_confidence | dont_know``. The
    diagnostic surfaces ``dont_know`` as a first-class output rather than
    fabricating a number.
    """

    id: str
    type: GapType
    severity: float = Field(ge=0.0, le=1.0)
    revenue_impact_usd_monthly: float = 0.0
    calibration_label: CalibrationLabel = "uncertain"
    uncertainty_type: UncertaintyType | None = None
    reasoning_chain: str | None = None
    affected_products: list[str] = Field(default_factory=list)


class FixSuggestion(_Base):
    """Proposed fix for a gap - node type #11.

    ``predicted_delta_range`` is a range, not a point estimate. The product
    principle is calibrated honesty over inflated promises.
    """

    id: str
    gap_id: str
    fix_type: FixType
    proposed_text: str
    applied: bool = False
    applied_at: datetime | None = None
    predicted_delta_range: PredictedDelta | None = None
    observed_delta: float | None = None
    shopify_resource_id: str | None = None
    voice_match_notes: str | None = None


# ---------------------------------------------------------------------------
# 12 Edge types (WINNING_PLAN §6.2)
# ---------------------------------------------------------------------------


class _BaseEdge(_Base):
    """Common edge envelope - every edge carries from/to ids and a type."""

    type: EdgeType
    from_id: str
    to_id: str


class DescribesEdge(_BaseEdge):
    """MerchantTruth → Product (the truth describes a product)."""

    type: Literal["DESCRIBES"] = "DESCRIBES"
    weight: float = Field(ge=0.0, le=1.0, default=1.0)
    scope: PolicyScope = "specific"


class CoversEdge(_BaseEdge):
    """Policy → Product (the policy covers a product)."""

    type: Literal["COVERS"] = "COVERS"
    weight: float = Field(ge=0.0, le=1.0, default=1.0)
    exception_rule: str | None = None


class MentionsEdge(_BaseEdge):
    """AgentRepresentation → Product (the agent mentions a product)."""

    type: Literal["MENTIONS"] = "MENTIONS"
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    sentiment: Sentiment | None = None


class MisrepresentsEdge(_BaseEdge):
    """AgentRepresentation → Product (the agent misrepresents a product)."""

    type: Literal["MISREPRESENTS"] = "MISREPRESENTS"
    severity: float = Field(ge=0.0, le=1.0, default=0.5)
    delta_description: str | None = None


class RevealsEdge(_BaseEdge):
    """AgentRepresentation → Gap (the agent output reveals a gap)."""

    type: Literal["REVEALS"] = "REVEALS"
    weight: float = Field(ge=0.0, le=1.0, default=1.0)


class HarmsEdge(_BaseEdge):
    """Gap → Product (the gap harms a product's surface rate / revenue)."""

    type: Literal["HARMS"] = "HARMS"
    revenue_impact_share: float = Field(ge=0.0, le=1.0, default=1.0)


class FixesEdge(_BaseEdge):
    """FixSuggestion → Gap (the fix targets a gap)."""

    type: Literal["FIXES"] = "FIXES"
    predicted_delta: float | None = None


class ContradictsEdge(_BaseEdge):
    """(any) → (any) - preserved Echomind contradiction primitive."""

    type: Literal["CONTRADICTS"] = "CONTRADICTS"
    resolution: str | None = None
    context_a: str | None = None
    context_b: str | None = None


class TriggersEdge(_BaseEdge):
    """Decision → Action / Pattern → Decision (preserved)."""

    type: Literal["TRIGGERS"] = "TRIGGERS"
    condition: str | None = None
    probability: float | None = None


class ExceptionToEdge(_BaseEdge):
    """Policy → Policy / MerchantTruth → Policy (preserved)."""

    type: Literal["EXCEPTION_TO"] = "EXCEPTION_TO"
    condition: str | None = None
    frequency: DecisionFrequency = "sometimes"


class AnswersEdge(_BaseEdge):
    """Policy or MerchantTruth → CustomerQuestion."""

    type: Literal["ANSWERS"] = "ANSWERS"
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)


class SimilarToEdge(_BaseEdge):
    """(any) → (any) - embedding-similarity edge (deduped to high-confidence pairs)."""

    type: Literal["SIMILAR_TO"] = "SIMILAR_TO"
    embedding_similarity: float = Field(ge=0.0, le=1.0, default=0.0)


# ---------------------------------------------------------------------------
# Endpoint helper envelopes
# ---------------------------------------------------------------------------


class HealthResponse(_Base):
    """Live `/health` payload - surfaced on every backend boot."""

    status: Literal["ok", "degraded", "error"]
    neo4j: dict[str, Any]
    gemini: dict[str, Any]
    env: str
    version: str = "0.1.0"


class NotImplementedResponse(_Base):
    """Standard envelope returned by route handlers that aren't wired yet."""

    status: Literal["not_yet_implemented"] = "not_yet_implemented"
    endpoint: str
    detail: str | None = None


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

NODE_MODELS: dict[str, type[_Base]] = {
    "Product": Product,
    "Policy": Policy,
    "TrustSignal": TrustSignal,
    "MerchantTruth": MerchantTruth,
    "Decision": Decision,
    "Pattern": Pattern,
    "CustomerQuestion": CustomerQuestion,
    "BuyerPrompt": BuyerPrompt,
    "AgentRepresentation": AgentRepresentation,
    "Gap": Gap,
    "FixSuggestion": FixSuggestion,
}

EDGE_MODELS: dict[str, type[_BaseEdge]] = {
    "DESCRIBES": DescribesEdge,
    "COVERS": CoversEdge,
    "MENTIONS": MentionsEdge,
    "MISREPRESENTS": MisrepresentsEdge,
    "REVEALS": RevealsEdge,
    "HARMS": HarmsEdge,
    "FIXES": FixesEdge,
    "CONTRADICTS": ContradictsEdge,
    "TRIGGERS": TriggersEdge,
    "EXCEPTION_TO": ExceptionToEdge,
    "ANSWERS": AnswersEdge,
    "SIMILAR_TO": SimilarToEdge,
}

__all__ = [
    # nodes
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
    # edges
    "DescribesEdge",
    "CoversEdge",
    "MentionsEdge",
    "MisrepresentsEdge",
    "RevealsEdge",
    "HarmsEdge",
    "FixesEdge",
    "ContradictsEdge",
    "TriggersEdge",
    "ExceptionToEdge",
    "AnswersEdge",
    "SimilarToEdge",
    # reasoning trace
    "ReasoningStep",
    "KnowledgeSource",
    "ContradictionResolution",
    "CalibrationBlock",
    "ReasoningTrace",
    "PredictedDelta",
    # envelopes
    "HealthResponse",
    "NotImplementedResponse",
    # registries
    "NODE_MODELS",
    "EDGE_MODELS",
    # enums
    "TacitLevel",
    "TacitCategory",
    "TruthCategory",
    "PolicyType",
    "PolicyScope",
    "TrustSignalType",
    "DecisionFrequency",
    "IntentClass",
    "GapType",
    "CalibrationLabel",
    "UncertaintyType",
    "FixType",
    "EdgeType",
    "SocraticPhase",
    "Sentiment",
]
