"""Echomind Commerce - named Cypher queries (single source of Cypher truth).

Same discipline as `config/prompts.py` for LLM prompts: every Cypher string
lives here as a named module-level constant, callers import by name and
parameterize through `Neo4jClient.run`. Tests verify each query parses on
an empty database.

Layout
------
    INGEST     - Shopify → Neo4j writes (idempotent MERGE on `id`)
    INTERVIEW  - MerchantTruth / Decision / Pattern / CustomerQuestion writes
    SWARM      - BuyerPrompt / AgentRepresentation writes + edges
    GAP_DETECT - five candidate-gap detection queries (§16.1)
    SUBGRAPH   - 4-strategy retrieval for fix generation (§10)
    STATS      - graph metrics for the audit dashboard
    LEGACY     - older registered names kept for back-compat
"""

from __future__ import annotations

from typing import Final


# ---------------------------------------------------------------------------
# INGEST - Shopify → Neo4j writes (idempotent MERGE on `id`)
# ---------------------------------------------------------------------------


UPSERT_PRODUCT: Final[str] = """
MERGE (p:Product {id: $id})
SET p.shopify_gid     = $shopify_gid,
    p.title           = $title,
    p.description     = $description,
    p.price           = $price,
    p.currency        = $currency,
    p.image_urls      = $image_urls,
    p.tags            = $tags,
    p.variants_summary = $variants_summary,
    p.confidence      = coalesce(p.confidence, 1.0),
    p.ingested_at     = $ingested_at
RETURN p.id AS id
"""

UPSERT_POLICY: Final[str] = """
MERGE (pol:Policy {id: $id})
SET pol.type        = $type,
    pol.text        = $text,
    pol.scope       = $scope,
    pol.source_url  = $source_url,
    pol.confidence  = coalesce(pol.confidence, 1.0)
RETURN pol.id AS id
"""

UPSERT_TRUST_SIGNAL: Final[str] = """
MERGE (t:TrustSignal {id: $id})
SET t.type        = $type,
    t.value       = $value,
    t.attached_to = $attached_to,
    t.confidence  = coalesce(t.confidence, 1.0)
RETURN t.id AS id
"""


# ---------------------------------------------------------------------------
# INTERVIEW - extracted nodes from Socratic interview
# ---------------------------------------------------------------------------


UPSERT_MERCHANT_TRUTH: Final[str] = """
MERGE (m:MerchantTruth {id: $id})
SET m.statement       = $statement,
    m.verbatim_quote  = $verbatim_quote,
    m.category        = $category,
    m.tacit_category  = $tacit_category,
    m.tacit_level     = $tacit_level,
    m.source_phase    = $source_phase,
    m.confidence      = $confidence,
    m.embedding       = $embedding,
    m.aliases         = $aliases,
    m.parse_failed    = coalesce($parse_failed, false)
RETURN m.id AS id
"""

UPSERT_DECISION: Final[str] = """
MERGE (d:Decision {id: $id})
SET d.question  = $question,
    d.context   = $context,
    d.outcome   = $outcome,
    d.conditions = $conditions,
    d.frequency = $frequency,
    d.confidence = $confidence
RETURN d.id AS id
"""

UPSERT_PATTERN: Final[str] = """
MERGE (p:Pattern {id: $id})
SET p.name             = $name,
    p.description      = $description,
    p.indicators       = $indicators,
    p.typical_response = $typical_response,
    p.confidence       = $confidence
RETURN p.id AS id
"""

UPSERT_CUSTOMER_QUESTION: Final[str] = """
MERGE (q:CustomerQuestion {id: $id})
SET q.question     = $question,
    q.frequency    = $frequency,
    q.intent_class = $intent_class,
    q.embedding    = $embedding
RETURN q.id AS id
"""


# ---------------------------------------------------------------------------
# SWARM - buyer prompts + agent representations
# ---------------------------------------------------------------------------


UPSERT_BUYER_PROMPT: Final[str] = """
MERGE (b:BuyerPrompt {id: $id})
SET b.prompt_text           = $prompt_text,
    b.intent_class          = $intent_class,
    b.length_bucket         = $length_bucket,
    b.is_adversarial        = $is_adversarial,
    b.generated_from_truths = $generated_from_truths,
    b.embedding             = $embedding
RETURN b.id AS id
"""

UPSERT_AGENT_REPRESENTATION: Final[str] = """
MERGE (a:AgentRepresentation {id: $id})
SET a.agent_model                 = $agent_model,
    a.buyer_prompt_id             = $buyer_prompt_id,
    a.response_text               = $response_text,
    a.surfaced_products           = $surfaced_products,
    a.cited_policies              = $cited_policies,
    a.confidence_in_recommendation = $confidence_in_recommendation,
    a.latency_ms                  = $latency_ms,
    a.captured_at                 = $captured_at,
    a.parse_failed                = coalesce($parse_failed, false)
RETURN a.id AS id
"""

UPSERT_GAP: Final[str] = """
MERGE (g:Gap {id: $id})
SET g.type                          = $type,
    g.severity                      = $severity,
    g.revenue_impact_usd_monthly    = $revenue_impact_usd_monthly,
    g.calibration_label             = $calibration_label,
    g.uncertainty_type              = $uncertainty_type,
    g.reasoning_chain               = $reasoning_chain,
    g.affected_products             = $affected_products
RETURN g.id AS id
"""

UPSERT_FIX_SUGGESTION: Final[str] = """
MERGE (f:FixSuggestion {id: $id})
SET f.gap_id                = $gap_id,
    f.fix_type              = $fix_type,
    f.proposed_text         = $proposed_text,
    f.applied               = $applied,
    f.applied_at            = $applied_at,
    f.predicted_delta_low   = $predicted_delta_low,
    f.predicted_delta_high  = $predicted_delta_high,
    f.observed_delta        = $observed_delta,
    f.shopify_resource_id   = $shopify_resource_id,
    f.voice_match_notes     = $voice_match_notes
RETURN f.id AS id
"""

# Generic edge upsert; rel_type is f-string'd in (Cypher does not parameterize
# relationship types). Caller must validate `rel_type` against EdgeType enum.
UPSERT_EDGE_TEMPLATE: Final[str] = """
MATCH (a {{id: $from_id}}), (b {{id: $to_id}})
MERGE (a)-[r:{rel_type}]->(b)
SET r += $props
RETURN type(r) AS rel
"""


# ---------------------------------------------------------------------------
# GAP_DETECT - 5 Cypher candidate-detection queries (§16.1).
# Returns CANDIDATES; the LLM judge classifies type+severity downstream.
# ---------------------------------------------------------------------------


CANDIDATE_OMISSION: Final[str] = """
// Products with positioning (≥1 MerchantTruth) but zero agent mentions.
MATCH (p:Product)
OPTIONAL MATCH (m:MerchantTruth)-[:DESCRIBES]->(p)
WITH p, count(DISTINCT m) AS truth_count
WHERE truth_count > 0
OPTIONAL MATCH (a:AgentRepresentation)-[:MENTIONS]->(p)
WITH p, truth_count, count(DISTINCT a) AS mention_count
WHERE mention_count = 0
RETURN p.id AS product_id, p.title AS title, truth_count, mention_count
ORDER BY truth_count DESC
LIMIT 20
"""

CANDIDATE_CONTRADICTION: Final[str] = """
// MerchantTruth + AgentRepresentation pairs about the same product.
// Pre-filter is structural; LLM judge confirms semantic contradiction.
MATCH (m:MerchantTruth)-[:DESCRIBES]->(p:Product)<-[:MENTIONS]-(a:AgentRepresentation)
WHERE m.statement IS NOT NULL AND a.response_text IS NOT NULL
RETURN p.id            AS product_id,
       p.title         AS title,
       m.id            AS truth_id,
       m.statement     AS truth,
       a.id            AS agent_id,
       a.agent_model   AS agent_model,
       a.response_text AS agent_text
LIMIT 50
"""

CANDIDATE_AMBIGUITY: Final[str] = """
// Same product receives divergent characterizations from ≥2 different agents.
MATCH (a:AgentRepresentation)-[:MENTIONS]->(p:Product)
WITH p, a.agent_model AS agent, a.response_text AS text
WITH p, collect(DISTINCT agent) AS agents, collect(text) AS texts
WHERE size(agents) >= 2
RETURN p.id AS product_id, p.title AS title, agents, texts
LIMIT 30
"""

CANDIDATE_HALLUCINATION: Final[str] = """
// Agent surfaced a product title that doesn't exist in the catalog.
MATCH (a:AgentRepresentation)
WHERE size(a.surfaced_products) > 0
WITH a, a.surfaced_products AS surfaced
UNWIND surfaced AS surfaced_title
OPTIONAL MATCH (p:Product) WHERE toLower(p.title) = toLower(surfaced_title)
WITH a, surfaced_title, p
WHERE p IS NULL
RETURN a.id           AS agent_id,
       a.agent_model  AS agent_model,
       surfaced_title AS hallucinated_title,
       a.response_text AS agent_text
LIMIT 30
"""

CANDIDATE_DARK_ZONE: Final[str] = """
// Subcategories with zero agent mentions across any buyer prompt.
MATCH (p:Product)
WITH coalesce(p.productType, p.tags[0]) AS subcat,
     count(p) AS product_count,
     collect(DISTINCT p.id) AS product_ids
WHERE subcat IS NOT NULL
OPTIONAL MATCH (a:AgentRepresentation)-[:MENTIONS]->(p2:Product)
WHERE coalesce(p2.productType, p2.tags[0]) = subcat
WITH subcat, product_count, product_ids, count(DISTINCT a) AS mention_count
WHERE mention_count = 0
RETURN subcat AS subcategory, product_count, product_ids, mention_count
ORDER BY product_count DESC
LIMIT 10
"""


# ---------------------------------------------------------------------------
# SUBGRAPH retrieval (§10) - 4 strategies, combined for fix generation
# ---------------------------------------------------------------------------


SUBGRAPH_DIRECT_2HOP: Final[str] = """
MATCH (seed) WHERE seed.id IN $seed_ids
CALL {
  WITH seed
  MATCH (seed)-[r:DESCRIBES|COVERS|ANSWERS|EXCEPTION_TO*1..2]-(n)
  RETURN seed AS s, n
  LIMIT 60
}
RETURN DISTINCT n AS node, head(labels(n)) AS type, n.confidence AS confidence
LIMIT 60
"""

SUBGRAPH_DECISIONS: Final[str] = """
MATCH (seed) WHERE seed.id IN $seed_ids
OPTIONAL MATCH (seed)-[*1..2]-(d:Decision)
OPTIONAL MATCH (d)-[r:TRIGGERS|EXCEPTION_TO]-(neighbour)
RETURN DISTINCT d AS decision, collect(DISTINCT neighbour) AS neighbours
LIMIT 20
"""

SUBGRAPH_CONTRADICTIONS: Final[str] = """
MATCH (a)-[r:CONTRADICTS]-(b)
WHERE a.id IN $seed_ids OR b.id IN $seed_ids
RETURN a AS node_a, b AS node_b, r.resolution AS resolution
LIMIT 30
"""


# ---------------------------------------------------------------------------
# STATS - graph health for the audit dashboard
# ---------------------------------------------------------------------------


GRAPH_NODE_COUNTS: Final[str] = """
MATCH (n)
WITH labels(n)[0] AS label, count(*) AS c
RETURN label, c
ORDER BY label
"""

GRAPH_EDGE_COUNTS: Final[str] = """
MATCH ()-[r]->()
WITH type(r) AS rel, count(*) AS c
RETURN rel, c
ORDER BY rel
"""

SHOPIFY_INGEST_SUMMARY: Final[str] = """
MATCH (p:Product)
WITH count(p) AS products
OPTIONAL MATCH (po:Policy)
WITH products, count(po) AS policies
OPTIONAL MATCH (t:TrustSignal)
RETURN products, policies, count(t) AS trust_signals
"""


# ---------------------------------------------------------------------------
# LEGACY - older registered names kept for back-compat with operations.py +
# any caller already wired against them.
# ---------------------------------------------------------------------------


NODE_COUNTS_BY_LABEL: Final[str] = """
MATCH (n)
WITH labels(n) AS lbls
UNWIND lbls AS label
RETURN label, count(*) AS count
ORDER BY count DESC
""".strip()

PRODUCTS_WITHOUT_MERCHANT_TRUTH: Final[str] = """
MATCH (p:Product)
WHERE NOT (p)<-[:DESCRIBES]-(:MerchantTruth)
RETURN p.id AS id, p.title AS title, p.shopify_gid AS shopify_gid
ORDER BY p.title ASC
LIMIT $limit
""".strip()

TOP_FRONTIER_MERCHANT_TRUTHS: Final[str] = """
MATCH (m:MerchantTruth)
OPTIONAL MATCH (m)-[r]->()
WITH m, count(r) AS out_edges
RETURN m.id AS id,
       m.statement AS statement,
       m.category AS category,
       m.tacit_level AS tacit_level,
       coalesce(m.confidence, 0.0) AS confidence,
       out_edges
ORDER BY (1.0 - coalesce(m.confidence, 0.0)) + (1.0 / (1 + out_edges)) DESC
LIMIT $limit
""".strip()

SIMILAR_MERCHANT_TRUTHS_BY_VECTOR: Final[str] = """
CALL db.index.vector.queryNodes('merchanttruth_embedding_vec', $k, $embedding)
YIELD node, score
RETURN node.id AS id,
       node.statement AS statement,
       node.category AS category,
       score
""".strip()

GAPS_WITH_AFFECTED_PRODUCTS: Final[str] = """
MATCH (g:Gap)-[h:HARMS]->(p:Product)
RETURN g.id AS gap_id,
       g.type AS gap_type,
       g.severity AS severity,
       g.calibration_label AS calibration_label,
       g.revenue_impact_usd_monthly AS revenue_impact,
       collect({
         product_id: p.id,
         title: p.title,
         impact_share: h.revenue_impact_share
       }) AS affected_products
ORDER BY severity DESC
""".strip()


# Registry: name -> Cypher (kept for back-compat with legacy callers).
QUERIES: Final[dict[str, str]] = {
    "node_counts_by_label": NODE_COUNTS_BY_LABEL,
    "products_without_merchant_truth": PRODUCTS_WITHOUT_MERCHANT_TRUTH,
    "top_frontier_merchant_truths": TOP_FRONTIER_MERCHANT_TRUTHS,
    "similar_merchant_truths_by_vector": SIMILAR_MERCHANT_TRUTHS_BY_VECTOR,
    "gaps_with_affected_products": GAPS_WITH_AFFECTED_PRODUCTS,
}


def get(name: str) -> str:
    return QUERIES[name]


__all__ = [
    # ingest
    "UPSERT_PRODUCT",
    "UPSERT_POLICY",
    "UPSERT_TRUST_SIGNAL",
    # interview
    "UPSERT_MERCHANT_TRUTH",
    "UPSERT_DECISION",
    "UPSERT_PATTERN",
    "UPSERT_CUSTOMER_QUESTION",
    # swarm
    "UPSERT_BUYER_PROMPT",
    "UPSERT_AGENT_REPRESENTATION",
    "UPSERT_GAP",
    "UPSERT_FIX_SUGGESTION",
    "UPSERT_EDGE_TEMPLATE",
    # gap detect
    "CANDIDATE_OMISSION",
    "CANDIDATE_CONTRADICTION",
    "CANDIDATE_AMBIGUITY",
    "CANDIDATE_HALLUCINATION",
    "CANDIDATE_DARK_ZONE",
    # subgraph
    "SUBGRAPH_DIRECT_2HOP",
    "SUBGRAPH_DECISIONS",
    "SUBGRAPH_CONTRADICTIONS",
    # stats
    "GRAPH_NODE_COUNTS",
    "GRAPH_EDGE_COUNTS",
    "SHOPIFY_INGEST_SUMMARY",
    # legacy (back-compat)
    "QUERIES",
    "get",
    "NODE_COUNTS_BY_LABEL",
    "PRODUCTS_WITHOUT_MERCHANT_TRUTH",
    "TOP_FRONTIER_MERCHANT_TRUTHS",
    "SIMILAR_MERCHANT_TRUTHS_BY_VECTOR",
    "GAPS_WITH_AFFECTED_PRODUCTS",
]
