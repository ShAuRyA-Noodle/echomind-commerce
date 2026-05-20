# Technical Document

**Project:** Echomind Commerce
**Track:** Track 5 - AI Representation Optimizer
**Hackathon:** KASPARRO Agentic Commerce Hackathon 2026

---

## 1. Architecture

### 1.1 System overview

```
                        MERCHANT (browser)
                              |
                    Google Sign-In (Firebase Auth)
                              |
              +---------------+---------------+
              |                               |
       Next.js 14 frontend            Browser Mic API
       (TypeScript strict,             (Web Speech API
        Tailwind, shadcn/ui,           transcribes locally,
        react-force-graph-2d)         emits text_input over WS)
              |                               |
              +----------REST + WS------------+
                              |
                    FastAPI backend (Python 3.11)
                    uvicorn, websockets 13, pydantic 2
                              |
          +-------------------+-------------------+
          |           |           |               |
     Shopify     Gemini 2.5   OpenRouter      Neo4j
     Admin +     Flash + Pro  (4-model        AuraDB Free
     Storefront  + embed-004  swarm,          (typed graph
     GraphQL     (extraction, free tier)      + vector index)
                 judge, twin)
          |           |           |               |
          +-----+-----+-----------+---------------+
                |
           Firebase
           (Auth, Firestore, Storage)
```

### 1.2 Services

**Backend (one process, FastAPI)**

| Module | Responsibility |
|---|---|
| `api/endpoints/onboard` | Shopify OAuth + catalog crawl |
| `api/endpoints/interview` | Session lifecycle REST; WS handler in `main.py` |
| `api/endpoints/simulate` | Swarm REST + WS handler |
| `api/endpoints/diagnose` | Gap detection + judge + ranking |
| `api/endpoints/fix` | Fix generation + Shopify mutation + retest |
| `api/endpoints/audit` | Dashboard data (live Neo4j reads) |
| `api/endpoints/graph` | Graph viz + search + node detail |
| `api/endpoints/debug` | Observability (health/swarm/graph/shopify/env) |
| `api/endpoints/public_audit` | Tier S #1: paste-any-Shopify-URL, no Admin auth |

**Core engines**

| Module | Responsibility |
|---|---|
| `core/socratic/` | 5-phase interview: phase manager, frontier scorer, extractor (Gemini Flash), question generator, redundancy checker |
| `core/agents/` | OpenRouter 4-model swarm: typed AgentCall/AgentResponse, concurrent runner with demo mode, buyer-prompt generator |
| `core/diagnose/` | Cypher diff (5 gap types), Gemini Pro judge, calibrator (WINNING_PLAN §9.3 formula), revenue model, ranker, entity resolver |
| `core/fix/` | Gemini Pro copy generator (merchant voice conditioning), Shopify writer (5 fix types, snapshot/revert), retest orchestrator |
| `core/twin/` | Diagnostic twin: subgraph retriever (4 strategies), reasoning chain |
| `core/contradiction/` | Contradiction detector + resolver |

**Services layer**

| Service | Responsibility |
|---|---|
| `services/shopify_service.py` | Full Admin + Storefront client; snapshot/revert on every mutation; public-audit classmethod |
| `services/llm_service.py` | Central retry + rate-limit wrapper for Gemini Flash, Pro, embeddings, OpenRouter |
| `services/firebase_service.py` | Firebase Admin SDK initialization |
| `services/stt_service.py` | Google STT V2 streaming (gated; browser Web Speech API used for demo) |

---

## 2. Data Model

### 2.1 Node types (11)

| # | Label | Source | Key fields |
|---|---|---|---|
| 1 | Product | Shopify Admin GraphQL | id, shopify_gid, title, description, price, tags, embedding |
| 2 | Policy | Shopify pages + metafields | id, type, text, scope, exceptions |
| 3 | TrustSignal | Shopify reviews (metafields) | id, type, value, attached_to |
| 4 | MerchantTruth | Socratic interview | id, statement, verbatim_quote, category, tacit_category, tacit_level, source_phase, confidence, embedding |
| 5 | Decision | Interview | id, question, context, outcome, conditions[], frequency |
| 6 | Pattern | Interview | id, name, description, indicators[], typical_response |
| 7 | CustomerQuestion | Interview + agent prompts | id, question, frequency, intent_class, embedding |
| 8 | BuyerPrompt | Generated for simulator | id, prompt_text, intent_class, length_bucket, is_adversarial, embedding |
| 9 | AgentRepresentation | Agent swarm output | id, agent_model, buyer_prompt_id, response_text, surfaced_products[], latency_ms, parse_failed |
| 10 | Gap | Diagnose engine | id, type, severity, revenue_impact_usd_monthly, calibration_label, uncertainty_type, reasoning_chain |
| 11 | FixSuggestion | Fix generator | id, gap_id, fix_type, proposed_text, applied, predicted_delta_range, observed_delta |

**MerchantTruth carries TWO orthogonal classifications:**
- `category` (what it is about): positioning / audience / edge_case / relationship / style
- `tacit_category` (how tacit): procedural / conditional_heuristic / experiential_pattern / intuitive_judgment / edge_case_knowledge / meta_knowledge

### 2.2 Edge types (12)

DESCRIBES, COVERS, MENTIONS, MISREPRESENTS, REVEALS, HARMS, FIXES, CONTRADICTS, TRIGGERS, EXCEPTION_TO, ANSWERS, SIMILAR_TO.

### 2.3 Scale per audit
~500-1,500 nodes, ~1,500-4,500 edges. Fits AuraDB Free (50K/175K cap) at ~3% utilization.

---

## 3. The AI vs Deterministic Boundary

**The rule:** anything requiring ground truth or determinism is code; anything requiring natural-language understanding is LLM. We do not ask LLMs to do math, and we do not ask Cypher to read prose.

| Capability | Code or LLM | Why |
|---|---|---|
| Shopify API I/O | Code | Deterministic, schemas known, idempotent retries |
| Neo4j writes/reads | Code | Graph mutations are transactional |
| Cypher gap detection queries | Code | Graph algebra is deterministic; predicates are auditable |
| Revenue model arithmetic | Code | Math is math; parameters exposed as UI sliders |
| Calibration bucket assignment | Code | Threshold logic must be auditable - it is the load-bearing trust signal |
| Phase advancement triggers | Code | Statistical predicates over node counts |
| Entity resolution scoring | Code (with LLM embeddings as input) | Cosine similarity + Levenshtein, threshold-based |
| Buyer-intent prompt generation | Gemini Flash | Natural language synthesis |
| Transcript to typed graph nodes | Gemini Flash | Pure NLP; output validated against pydantic |
| Next-question generation | Gemini Flash | Conversational reasoning |
| Agent role-play (the swarm) | OpenRouter 4 LLMs | They are the things being measured |
| Gap classification | Gemini Pro judge | Semantic categorization with rubric |
| Fix copy generation | Gemini Pro | Natural language; conditioned on transcript samples |

Every LLM call returns through `services/llm_service.py`, which validates output against a pydantic schema and raises `LLMOutputInvalid` on failure. Calling code never inspects raw LLM text. This is what prevents "LLM does math" creep at the architectural level.

---

## 4. The Calibration Formula

```
adjusted_confidence = 0.4 * raw_confidence
                    + 0.3 * evidence_factor
                    + 0.3 * coverage_factor

where:
  raw_confidence    = LLM's stated confidence (0..1)
  evidence_factor   = min(1.0, supporting_nodes / 3)
  coverage_factor   = relevant_nodes_in_subgraph / expected_nodes

calibration_label:
  >= 0.80  ->  "certain"
  >= 0.60  ->  "confident"
  >= 0.35  ->  "uncertain"
  >= 0.15  ->  "low_confidence"
  else     ->  "dont_know"
```

**Critical distinction (WINNING_PLAN §9.4):**
- `dont_know` = subgraph has no relevant nodes (coverage < 0.15, we lack information).
- `uncertain` = relevant nodes exist but are sparse / contradictory.

These two are surfaced with different colors and different copy. They are not interchangeable. The distinction is tested in `backend/tests/test_calibration.py`.

### Gap priority formula

```
gap_priority =
    0.40 * revenue_impact_normalized
  + 0.20 * confidence_weight
  + 0.20 * fixability
  + 0.10 * affected_products_share
  + 0.10 * agent_consensus
```

---

## 5. Named Failure Modes (with concrete recovery)

### 5.1 LLM returns malformed JSON
**Trigger:** Gemini Flash extraction call returns text that fails pydantic validation.
**Recovery:** `services/llm_service.py` catches `pydantic.ValidationError`, logs the raw output, retries once with a stricter prompt. On second failure, falls back to a regex-based partial extractor that produces a node with `confidence=0.2` and `parse_failed=true`.
**UI:** Yellow banner: "Extraction needs review - flagged for your review." Frontier scorer down-weights `parse_failed` nodes.

### 5.2 Shopify Admin API down or rate-limited
**Trigger:** `productUpdate` mutation, catalog crawl, or metafield write returns 5xx, 429, or times out.
**Recovery:** `shopify_service.py` uses `tenacity` with exponential backoff (3 retries, 2s/4s/8s). On final failure during ingest: existing graph remains queryable. On final failure during fix application: mutation is rolled back via the inverse mutation if any partial state was committed.
**UI:** Banner: "Merchant data is stale, fixes cannot be applied until reconnect" with a Retry button.

### 5.3 Agent simulator rate-limited mid-run
**Trigger:** OpenRouter free-tier returns 429 or sustained 5xx for one of the four model slots.
**Recovery:** `core/agents/runner.py` uses per-provider concurrency-limited queue with exponential backoff. If a slot stays down, the run continues with the remaining providers; the failed column is labeled "rate-limited, partial sample." The calibrator **automatically downgrades** the calibration label on any gap that depended on that provider's evidence.
**UI:** The affected agent column shows a red dot with partial-sample text. Gap cards show auto-downgraded calibration with a tooltip explaining why.

### 5.4 Neo4j Bolt connection timeout
**Trigger:** AuraDB free-tier momentary unavailability or Bolt session drop during a write batch.
**Recovery:** `graph/operations.py` batches writes with deterministic IDs (re-write is idempotent). On timeout: 3 retries via `tenacity`, then a circuit breaker opens for 30 seconds. Reads are served from Firestore-cached projection during the breaker window.
**UI:** Banner: "Graph store reconnecting, your interview is being recorded."

### 5.5 STT misheard / low-confidence words
**Trigger:** Google STT V2 returns a word with confidence < 0.5, or the merchant's audio is cut off.
**Recovery:** `stt_service.py` exposes per-word confidence. The extraction pipeline refuses to extract `MerchantTruth` from any segment whose dominant words have STT confidence < 0.5, returning `extraction_skipped: true` instead of guessing.
**UI:** The transcript pane is editable. Words with STT confidence < 0.5 render in italic; clicking opens an inline editor. After correction, a "Re-extract this segment" button re-runs extraction.

---

## 6. Subgraph Retrieval (4 Strategies)

When generating a fix for a gap, four retrieval strategies run in parallel, are combined, deduped via entity resolution, and ranked by relevance x confidence x recency:

1. **Direct concept match + 2-hop expansion.** Cypher pattern matches nodes naming entities in the gap, expands 2 hops via DESCRIBES, COVERS, ANSWERS, EXCEPTION_TO.
2. **Embedding semantic search.** Top-12 most similar nodes via `text-embedding-004` cosine similarity over the gap's reasoning chain text.
3. **Decision-specific retrieval.** If the gap implicates a policy, retrieves the relevant Decision node and its full if-then tree.
4. **Contradiction-aware retrieval.** Pulls all CONTRADICTS edges touching the gap's affected nodes. Ensures the fix does not paper over a known contradiction.

---

## 7. The Agent Swarm

### 7.1 Models (verified live 2026-05-01)

| Slot | Model | Represents |
|---|---|---|
| gpt_oss | `openai/gpt-oss-120b:free` | OpenAI / GPT-class agents |
| llama | `meta-llama/llama-3.3-70b-instruct:free` | Meta AI + open-weight stacks |
| qwen | `qwen/qwen3-next-80b-a3b-instruct:free` | Qwen / Alibaba ecosystem |
| glm | `z-ai/glm-4.5-air:free` | Chinese frontier |
| adversarial | `nousresearch/hermes-3-llama-3.1-405b:free` | 405B for hostile prompts |

### 7.2 Buyer-intent prompt distribution
40% discover, 25% compare, 20% objection, 15% post-purchase. Generated by Gemini Flash conditioned on MerchantTruth nodes and CustomerQuestion nodes. Every prompt is persisted as a BuyerPrompt node for full audit-trail replayability.

### 7.3 Concurrency
Default 8 concurrent calls (4 slots x 2 prompts in-flight). Demo mode caps to 10 prompts, completing 40 calls in approximately 30 seconds wall-clock.

---

## 8. Cost Model

### 8.1 Hackathon (all free tier)

| Component | Volume | Free headroom |
|---|---|---|
| Gemini 2.5 Flash | ~200K tokens/audit | 1.5M tokens/day |
| Gemini 2.5 Pro | ~150K tokens/audit | 50 RPM, 32K TPM |
| text-embedding-004 | ~100K tokens/audit | Generous |
| Google STT V2 | 20 min/audit | 60 min/month |
| OpenRouter free swarm | ~400K tokens/audit | Per-model daily caps |

**Total marginal cost per audit: $0.**

### 8.2 Production projection
$5-8 per audit, dominated by paid model inclusion (OpenAI/Claude) for fuller coverage. Documents in docs/TECHNICAL_DOC.md §9.

---

## 9. Stack

**Backend:** Python 3.11, FastAPI 0.115, uvicorn, websockets 13, pydantic 2.9, neo4j 5.25, google-generativeai 0.8, openai 1.50 (for OpenRouter), firebase-admin 6.6, httpx, numpy, tenacity.

**Frontend:** Next.js 14.2, React 18.3, TypeScript 5.5 (strict), TailwindCSS 3.4, shadcn/ui, react-force-graph-2d 1.25, @tanstack/react-query 5.50, recharts, firebase 10.14, zod.

**Data:** Neo4j AuraDB Free (typed property graph + 768-dim cosine vector index), Firestore (sessions, transcripts, agent run logs, change log), Cloud Storage (audio, exports).

**Infrastructure:** Docker Compose (one-command local boot); Cloud Run + Vercel documented as production target.

---

## 10. Known Limitations

1. **Single-merchant scope.** No cross-merchant benchmarking.
2. **Synthetic buyer prompts.** Production would seed from real shopper search logs.
3. **Revenue model is parameterized, not measured.** Ranges shown, not point estimates.
4. **One-shot audit.** No persistent drift monitoring.
5. **Free-tier swarm.** No GPT-4/Claude Opus. Reframed honestly as more representative of real agentic infrastructure.
6. **Calibration is label-only.** We claim auditable 5-bucket labels, not numerical accuracy.
7. **English-only at submission.** Multilingual swarm is a documented stretch feature.
8. **Local Docker Compose.** Not deployed publicly; judges replicate via README.

---

## 11. Testing

- **Schema round-trip:** every pydantic node and edge accepts its sample payload, dumps, re-parses, equals original.
- **Enum drift detector:** every Literal enum locked against its canonical set; any silent drift fails CI.
- **Calibration boundary tests:** every bucket cutoff (0.80, 0.60, 0.35, 0.15) locked with inside-and-outside assertions. Three demo scenarios encoded.
- **CI:** GitHub Actions runs backend pytest + frontend tsc/eslint + em-dash detector + required-doc check on every push.

```
56 tests passing, 0 failures (last green: 2026-05-01)
```

---

*Companion: `PRODUCT_DOCUMENT.md` (problem, decisions, scope, tradeoffs).*
*Full decision history: `docs/DECISION_LOG.md`.*
