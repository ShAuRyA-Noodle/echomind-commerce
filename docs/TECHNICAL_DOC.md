# Echomind Commerce - Technical Document

> Track 5 · AI Representation Optimizer · Kasparro Agentic Commerce Hackathon
> Companion to `PRODUCT_DOC.md`. This doc answers: how is it built, where is the AI/deterministic line, and what happens when things break.

---

## 1. System Architecture

### 1.1 High-level data flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       MERCHANT (real user - you)                         │
└──────────────┬───────────────────────────────────────────────────┬──────┘
               │                                                   │
               │ Google Sign-In (Firebase Auth)                    │ Voice + Text
               ▼                                                   ▼
┌──────────────────────────┐                       ┌──────────────────────────┐
│  Next.js 14 Frontend     │                       │   Browser Mic API        │
│  (5 views: onboard /     │                       │   (audio chunks → WS)    │
│   interview / simulate / │                       │                          │
│   audit / diff)          │                       │                          │
└──────┬───────────────────┘                       └──────────┬───────────────┘
       │ REST + WebSocket                                     │
       ▼                                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend (Python 3.11)                      │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ /onboard │  │ /interview  │  │  /simulate   │  │ /diagnose /fix  │  │
│  └────┬─────┘  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘  │
└───────┼───────────────┼─────────────────┼───────────────────┼────────────┘
        │ Admin GraphQL │ Gemini Flash    │ Agent Swarm       │ Gemini Pro
        │               │ + STT V2        │ (OpenRouter)      │ + Cypher
        ▼               ▼                 ▼                   ▼
┌──────────────┐ ┌─────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  Shopify     │ │ Google STT  │  │   OpenRouter     │  │  Gemini API     │
│  Dev Store   │ │  V2 streamg │  │  • Llama-3.3 70B │  │  • Flash (extr) │
│  (real)      │ │  (real)     │  │  • Qwen-2.5 72B  │  │  • Pro (judge)  │
│              │ │             │  │  • DeepSeek V3   │  │  • embed-004    │
│  Admin API   │ │ Free tier:  │  │  • Gemini 2.0    │  │                 │
│  Storefront  │ │ 60 min/mo   │  │  (all :free)     │  │  Free tier      │
└──────────────┘ └─────────────┘  └──────────────────┘  └─────────────────┘
                                          │                    │
                                          └────────┬───────────┘
                                                   ▼
                              ┌────────────────────────────────────┐
                              │  Persistence layer                 │
                              │  • Neo4j AuraDB Free               │
                              │    (50K nodes / 175K edges)        │
                              │    typed graph + vector index      │
                              │  • Firebase Firestore              │
                              │    sessions, transcripts, runs,    │
                              │    change log                      │
                              │  • Firebase Cloud Storage          │
                              │    audio, exports                  │
                              └────────────────────────────────────┘
```

### 1.2 What lives where

- **Frontend (Next.js 14, TypeScript)** - five views: `/onboard`, `/interview/[id]`, `/simulate/[runId]`, `/audit/[storeId]`, `/diff/[gapId]` (+ stretch: `/graph`, `/policies`, `/replay`). All interactive UI; force-directed graph via `react-force-graph-2d`; radar via `recharts`; runtime validation via `zod`.
- **Backend (FastAPI, Python 3.11)** - REST + WebSocket. Five logical endpoints: onboard, interview, simulate, diagnose, fix. One process for the hackathon; documented as five Cloud Run services for v2.
- **Core modules** - `socratic/` (engine, question generator, extractor, phase manager, frontier scorer, redundancy checker, decision tree builder), `agents/` (OpenRouter client, Gemini client, prompt generator, runner, adversarial mode), `diagnose/` (Cypher diff, Gemini Pro judge, calibrator, revenue model, ranker), `fix/` (copy generator, policy clarifier, Shopify writer, retest orchestrator), `twin/` (query analyzer, subgraph retriever, reasoning chain, confidence calibrator), `contradiction/` (detector, resolver).
- **Services** - `shopify_service.py` (Admin GraphQL + Storefront), `stt_service.py` (Google STT V2 streaming), `llm_service.py` (central retry + rate-limit + provider router - every LLM call goes through here), `firebase_service.py`, `audio_service.py`.
- **Persistence** - Neo4j AuraDB Free (graph + vector index for embedding search), Firestore (session metadata, transcripts, agent run logs, change log for the Replay Theater), Cloud Storage (audio blobs, PDF exports).
- **Prompts** - every LLM prompt is centralized in `backend/config/prompts.py`. This is non-negotiable Echomind discipline. "60% of debugging is prompt tuning" remains true; centralization compounds across the 11-day build.

## 2. Stack

**Backend.** Python 3.11; FastAPI 0.115; uvicorn; websockets 13; pydantic 2.9; neo4j 5.25; google-generativeai 0.8; google-cloud-speech 2.27; openai 1.50 (used as the OpenAI-compatible client for OpenRouter); firebase-admin 6.6; httpx; numpy; tenacity (retries with exponential backoff).

**Frontend.** Next.js 14.2; React 18.3; TypeScript 5.5; TailwindCSS 3.4; shadcn/ui; react-force-graph-2d 1.25; @tanstack/react-query 5.50; recharts; firebase 10.14; zod.

**Data.** Neo4j AuraDB Free (Bolt protocol); Firebase Firestore; Firebase Cloud Storage; Firebase Auth.

**LLMs.** Direct Gemini API: `gemini-2.5-flash` for extraction, question gen, buyer prompt gen, fix copy (configured via `GEMINI_FLASH_MODEL` in `.env`); `gemini-2.5-pro` for twin reasoning, gap judge, contradiction resolver (configured via `GEMINI_PRO_MODEL`); `text-embedding-004` for entity resolution and semantic redundancy. The model layer is parameterized - if Google rotates a key to a 2.0 vs. 2.5 generation, the call path is unchanged (see Decision Log #19). OpenRouter `:free` tier: `meta-llama/llama-3.3-70b-instruct:free`, `qwen/qwen-2.5-72b-instruct:free`, `deepseek/deepseek-chat:free`, `google/gemini-2.0-flash-exp:free` (the 4-model agent swarm, plus the redundant Gemini path that lets us A/B direct-API vs. OpenRouter-routed Gemini for fairness verification).

**Speech.** Google Cloud STT V2 streaming, `long` model, auto-punctuation, word time offsets, voice activity events. Free tier: 60 min/month - covers the demo and a couple of dev runs.

**Infra.** Docker Compose (one-command local boot for judges to replicate). Cloud Run is a documented v2 stretch.

## 3. AI vs Deterministic Boundary (judge-graded)

**The rule, verbatim:** anything requiring ground truth or determinism is code; anything requiring natural-language understanding is LLM. We do not ask LLMs to do math, and we do not ask Cypher to read prose.

| Capability | Code or LLM? | Why |
|---|---|---|
| Shopify Admin / Storefront API I/O | Code | Deterministic, schemas known, idempotent retries |
| Neo4j writes/reads | Code | Same - graph mutations are transactional |
| Cypher gap-detection queries | Code | Graph algebra is deterministic; predicates are auditable |
| Revenue model arithmetic | Code | Math is math; every parameter is exposed in the UI as a slider |
| Confidence calibration thresholds (5-bucket assignment) | Code | Threshold logic must be auditable - it's the load-bearing trust signal |
| Phase advancement triggers | Code | Statistical predicates over node counts and edge density |
| Entity resolution scoring (Levenshtein + cosine + threshold) | Code | LLM provides the embedding, code does the comparison |
| Frontier score & gap priority computation | Code | Weighted sum of normalized features; needs to be reproducible |
| OAuth / token storage / Firebase auth verification | Code | Security-critical, never delegated |
| Buyer-intent prompt generation | LLM (Gemini Flash) | Natural language synthesis, conditioned on graph stats |
| Transcript chunk → typed graph nodes | LLM (Gemini Flash) | Pure NLP; output validated against pydantic schemas |
| Next-question generation in the Socratic loop | LLM (Gemini Flash) | Conversational reasoning over recent Q&A and graph state |
| Agent role-play (the swarm) | LLM | They *are* the things being measured |
| Gap classification (omission / contradiction / ambiguity / hallucination / dark_zone) | LLM (Gemini Pro judge) | Semantic categorization with rubric |
| Fix copy generation in merchant voice | LLM (Gemini Pro) | Natural language; conditioned on transcript voice samples |
| Policy decision-tree extraction from interview narrative | LLM extracts → code formalizes into JSON tree | LLM captures conversational logic, code formalizes the structure for testing |
| Contradiction adjudication between two text claims | LLM (Gemini Pro) | Requires reading both; code only flags the candidate pair via Cypher |

**Where the line is enforced in code.** Every LLM call returns through `services/llm_service.py`, which wraps the provider, validates output against a pydantic schema, and either returns a typed object or raises `LLMOutputInvalid`. Calling code never inspects raw text from an LLM - it inspects a typed object. This is what stops "LLM does math" creep at the architectural level.

## 4. Data Model

11 node types, 12 edge types. Six node types are direct ports from Echomind's original blueprint; five are commerce-native; one (Concept) was dropped because it added no value here.

### 4.1 Node types (11)

| # | Type | Source | Key fields |
|---|---|---|---|
| 1 | `Product` | Shopify Admin GraphQL | id, shopify_gid, title, description, price, currency, image_urls[], tags[], options, variants_summary, embedding (768d), confidence, ingested_at |
| 2 | `Policy` | Shopify pages + metafields | id, type (return / shipping / warranty / exchange), text, scope (specific products / global), confidence, source_url |
| 3 | `TrustSignal` | Shopify reviews + storefront | id, type (review / badge / cert / testimonial), value, attached_to, confidence |
| 4 | `MerchantTruth` (Echomind's Heuristic + Experience + Rule fused) | Interview | id, statement, category (positioning / audience / edge_case / relationship / style), tacit_level (explicit / semi-tacit / deeply-tacit), source_phase, confidence, embedding |
| 5 | `Decision` (preserved) | Interview | id, question, context, outcome, conditions[], frequency (always / usually / sometimes / rarely), confidence |
| 6 | `Pattern` (preserved) | Interview | id, name, description, indicators[], typical_response, confidence |
| 7 | `CustomerQuestion` | Interview + agent prompts | id, question, frequency, intent_class (discover / compare / objection / post-purchase), embedding |
| 8 | `BuyerPrompt` | Generated for simulator | id, prompt_text, intent_class, generated_from_truths[], embedding |
| 9 | `AgentRepresentation` | Agent swarm output | id, agent_model, buyer_prompt_id, response_text, surfaced_products[], cited_policies[], confidence_in_recommendation, latency_ms, captured_at |
| 10 | `Gap` | Diagnose engine | id, type (omission / contradiction / ambiguity / hallucination / dark_zone), severity (0..1), revenue_impact_usd_monthly, calibration_label (5 buckets), reasoning_chain (text), affected_products[] |
| 11 | `FixSuggestion` | Fix generator | id, gap_id, fix_type (copy_rewrite / faq_add / policy_clarify / metafield_add / structured_data), proposed_text, applied (bool), applied_at, predicted_delta_range, observed_delta |

### 4.2 Edge types (12)

| # | Edge | From → To | Properties |
|---|---|---|---|
| 1 | `DESCRIBES` | MerchantTruth → Product | weight, scope |
| 2 | `COVERS` | Policy → Product | weight, exception_rule |
| 3 | `MENTIONS` | AgentRepresentation → Product | confidence, sentiment |
| 4 | `MISREPRESENTS` | AgentRepresentation → Product | severity, delta_description |
| 5 | `REVEALS` | AgentRepresentation → Gap | weight |
| 6 | `HARMS` | Gap → Product | revenue_impact_share |
| 7 | `FIXES` | FixSuggestion → Gap | predicted_delta |
| 8 | `CONTRADICTS` (preserved) | (any) → (any) | resolution, context_a, context_b |
| 9 | `TRIGGERS` (preserved) | Decision → Action / Pattern → Decision | condition, probability |
| 10 | `EXCEPTION_TO` (preserved) | Policy → Policy / MerchantTruth → Policy | condition, frequency |
| 11 | `ANSWERS` | Policy / MerchantTruth → CustomerQuestion | confidence |
| 12 | `SIMILAR_TO` | (any) → (any) | embedding_similarity |

### 4.3 Cardinality per audit

Product 30-60, Policy 5-12, TrustSignal 20-80, MerchantTruth 60-120, Decision 15-30, Pattern 10-20, CustomerQuestion 40-80, BuyerPrompt 50-150, AgentRepresentation 200-600, Gap 15-40, FixSuggestion 15-40. Total ~500-1,500 nodes / ~1,500-4,500 edges per audit. Comfortably fits AuraDB Free's 50K / 175K cap.

### 4.4 Honest accounting on "10,000 questions"

Per audit, total **LLM-mediated micro-queries** are: verbal Q&A 30-50; internal extraction prompts ~120 (each transcript chunk extracted independently); buyer-intent prompts 50-150 (the simulator); per-agent gap-classification calls ~200; decision-tree decomposition ~80; contradiction probe ~40. **Total: ~5,000-8,000 per audit** when multiplied across documents, chunks, and re-extraction passes. Defensible if a judge unpacks it. We do not carry the round-number "10,000" framing into the demo or docs.

## 5. Failure Modes (five named, with concrete fallback behavior)

The rules call this out explicitly: "a team that says 'if the LLM returns a malformed response, we retry once and then show a fallback' has thought harder than a team with a perfect-looking diagram and no failure handling." Five real modes, each with code-level recovery and UI-level user message.

### 5.1 LLM returns malformed JSON / off-schema output

**Trigger.** Gemini Flash extraction call returns text that fails pydantic validation against the typed extraction schema (e.g., a `MerchantTruth` extraction missing `category` or with a free-form value outside the enum).

**Recovery (code).** `services/llm_service.py` catches `pydantic.ValidationError`, logs the raw output to Firestore (for prompt-tuning postmortems), retries **once** with a stricter prompt that quotes the prior failure ("the previous output failed validation because X - return only valid JSON matching this schema"). On a second failure, falls back to a regex-based partial extractor that captures whatever fields it can and produces a node with `confidence=0.2` and `parse_failed=true`.

**UI-level behavior.** A yellow banner appears on the affected interview turn: "Extraction needs review - the system pulled what it could, but flagged this segment for your review." The Living Update Loop surfaces these for merchant correction post-interview. The frontier scorer down-weights `parse_failed` nodes so they don't drive question generation.

### 5.2 Shopify Admin / Storefront API down or rate-limited

**Trigger.** A `productUpdate` mutation, a catalog crawl, or a metafield write returns 5xx, 429, or times out.

**Recovery (code).** `shopify_service.py` uses `tenacity` with exponential backoff (3 retries, 2s/4s/8s). On final failure during ingest: existing graph remains queryable (Neo4j data is not invalidated); ingest job is marked `paused`; the change is queued for retry on the next reconnect. On final failure during fix application: mutation is rolled back via the inverse mutation if any partial state was committed; the fix is marked `apply_failed` with the upstream error preserved.

**UI-level behavior.** During ingest: banner reads "Merchant data is N hours stale, fixes can't be applied until reconnect," with a "Retry connection" button. During fix application: re-test panel is disabled with an explanatory tooltip; the fix card itself shows a red "apply failed - Shopify returned 429, will retry automatically in 60s" message. The audit dashboard remains fully functional against the cached graph.

### 5.3 Agent simulator rate-limited or provider unavailable mid-run

**Trigger.** OpenRouter free-tier returns 429 or a sustained 5xx for one of {Llama, Qwen, DeepSeek, Gemini-routed} mid-simulation.

**Recovery (code).** `core/agents/runner.py` uses a per-provider concurrency-limited queue with exponential backoff (max 3 retries per call). If a single provider stays down, the run continues with the remaining providers; the failed column is labeled `rate-limited - partial sample (N of 50 prompts completed)`. The calibrator detects reduced sample size and **automatically downgrades** the calibration label on any gap that depended on that provider's evidence (`confident` → `uncertain`, `uncertain` → `low_confidence`). Already-completed responses persist as `AgentRepresentation` nodes - nothing is discarded.

**UI-level behavior.** The affected agent column shows a red dot with the partial-sample text. Gap cards downstream show their auto-downgraded calibration with a tooltip explaining: "Calibration downgraded because Llama-3.3 only completed 12 of 50 prompts; verify before acting." Demo narration: "OpenRouter free tier is rate-limited mid-run - this is real-world infra reality, and the calibration label reflects it."

### 5.4 Neo4j Bolt connection timeout / transient unavailability

**Trigger.** AuraDB free-tier momentary unavailability or Bolt session drop during a write batch.

**Recovery (code).** `graph/operations.py` batches writes by node type with deterministic IDs derived from a content hash (so re-write is idempotent - re-applying the same batch is safe). On a Bolt timeout: 3 retries with `tenacity`, then a circuit breaker opens for 30 seconds before allowing further writes. Reads are served from a Firestore-cached projection of recent nodes during the breaker window so the UI keeps rendering. On breaker close, queued writes are flushed in order.

**UI-level behavior.** Banner: "Graph store reconnecting - your interview is being recorded and will be persisted in a few seconds." The interview WebSocket does not drop; Firestore captures every transcript turn regardless. No data loss; the user sees a brief "Saving..." indicator.

### 5.5 STT misheard transcript / low-confidence words

**Trigger.** Google STT V2 returns a word with confidence < 0.5, or the merchant's audio is cut off mid-word, or background noise inserts hallucinated words.

**Recovery (code).** `stt_service.py` exposes per-word confidence and time offsets. The extraction pipeline reads these and adds a `low_confidence_segments[]` field to each transcript chunk. The extractor is instructed in `prompts.py` to refuse to extract `MerchantTruth` from any segment whose dominant words have STT confidence < 0.5 - it returns `extraction_skipped: true` instead of guessing.

**UI-level behavior.** The transcript pane is editable post-interview. Words with STT confidence < 0.5 render in italic with a subtle highlight; clicking opens a small inline editor. After the merchant corrects a segment, a "Re-extract this segment" button re-runs the extraction over the corrected text and updates the graph in place. No silent hallucinated extractions ever land in the diagnostic substrate.

### 5.6 Bonus mode - staged demo contradiction goes missing

**Trigger.** The pre-baked Yirgacheffe contradiction (the demo's headline gap) fails to be detected because the merchant's interview answer this time didn't mention "chocolate-forward" with enough strength.

**Recovery.** Multiple gaps are baked in (Yirgacheffe contradiction, cold-brew dark zone, shipping policy contradiction, grind size FAQ omission, decaf line dark zone, return policy edge case). The demo doesn't pre-script which one is the headline; whichever gap the system surfaces highest gets the deep-dive. The product's job is to surface real misrepresentation; if Yirgacheffe is buried this run, the cold-brew dark zone or the policy contradiction is the headline instead.

## 6. Calibration Formula (verbatim from §9.3)

For every twin output (gap diagnosis, fix recommendation, predicted delta):

```
adjusted_confidence = 0.4 × raw_confidence
                    + 0.3 × evidence_factor
                    + 0.3 × coverage_factor

where:
  raw_confidence    = LLM's stated confidence (0..1)
  evidence_factor   = min(1.0, supporting_nodes / 3)
  coverage_factor   = relevant_nodes_in_subgraph / expected_nodes_for_query

calibration_label =
  ≥ 0.80  → "certain"
  ≥ 0.60  → "confident"
  ≥ 0.35  → "uncertain"
  ≥ 0.15  → "low_confidence"
  else    → "dont_know"
```

**The critical distinction we draw, verbatim:**

> "I don't know" = coverage < 0.15 (no relevant nodes in subgraph - we lack information).
> "I'm uncertain" = nodes exist but low-confidence / contradictory / sparse - we have information but it's not solid.

The two are surfaced with different colors and different copy in the UI. We do **not** claim that "80% adjusted confidence ≈ 80% accuracy" - we claim only the 5-bucket *labels*, which are auditable and don't require a calibrated probability calibration we haven't earned.

For the gap ranker (which gap to fix first):

```
gap_priority(gap) =
    0.40 × revenue_impact_normalized
  + 0.20 × confidence (only `confident` or `certain` rank high)
  + 0.20 × fixability (FixSuggestion exists with predicted_delta_range > 10%)
  + 0.10 × affected_products_share
  + 0.10 × agent_consensus (multiple agents reveal this gap)
```

`uncertain` gaps surface but flagged "verify first." `low_confidence` gaps are hidden by default, visible in advanced view. `dont_know` gaps are listed under "needs more data" - never presented as actionable.

## 7. Subgraph Retrieval Strategies

When generating a Fix for a Gap, four retrieval strategies run in parallel, are combined, deduped via entity resolution, and ranked by `relevance × confidence × recency`:

1. **Direct concept match + 2-hop expansion.** Cypher pattern matches nodes naming entities in the gap's reasoning trace, then expands 2 hops via `DESCRIBES`, `COVERS`, `ANSWERS`, `EXCEPTION_TO`. Captures structurally related context.
2. **Embedding semantic search.** Top-K (default 12) most similar nodes via `text-embedding-004` cosine similarity over the gap's reasoning chain text. Captures semantically related context that isn't graph-adjacent.
3. **Decision-specific retrieval.** If the gap implicates a policy, retrieves the relevant `Decision` node and its full if-then tree (built by `decision_tree_builder.py` from interview narrative). Ensures the fix respects the merchant's actual edge-case logic.
4. **Contradiction-aware retrieval.** Pulls all `CONTRADICTS` edges touching the gap's affected nodes. Ensures the fix doesn't introduce or paper over a known contradiction.

The combined subgraph (typically 20-50 nodes) feeds Gemini Pro with: the gap reasoning trace, the subgraph nodes (with type and confidence), and 3-5 verbatim transcript samples for voice conditioning. This is the same Echomind multi-strategy retrieval pattern reused for fix generation rather than twin Q&A.

## 8. Reasoning Trace Format (preserved verbatim)

Every Gap and every FixSuggestion exposes a reasoning trace structured as:

```json
{
  "answer": "...",
  "reasoning_chain": [
    {"step": 1, "claim": "...", "source_node_ids": ["..."], "confidence": 0.x},
    {"step": 2, "claim": "...", "source_node_ids": ["..."], "confidence": 0.x}
  ],
  "knowledge_sources_used": [
    {"node_id": "...", "type": "MerchantTruth", "relevance": 0.x}
  ],
  "contradictions_resolved": [
    {"between": ["a", "b"], "resolution": "..."}
  ],
  "confidence": 0.x,
  "calibration": "confident",
  "uncertainty_type": null
}
```

`uncertainty_type` is one of `null` / `data_sparse` / `data_contradictory` / `out_of_domain`. The UI renders this as an expandable accordion under each gap card; every `node_id` is clickable and jumps to the corresponding node in the graph view. **This is the single biggest trust mechanism in the product.** A judge asking "how do we know the gap is real?" gets a click-by-click audit trail back to specific MerchantTruth nodes from interview, specific AgentRepresentation outputs from the swarm, and any contradictions resolved along the way.

## 9. Cost Model (free-tier-first, real numbers)

Per merchant audit, hackathon free tier:

| Component | Volume | Free-tier headroom |
|---|---|---|
| Gemini Flash (extraction + question gen + buyer prompts + fix copy) | ~30 calls × 2K tokens + ~30 × 1K + ~150 × 0.5K + ~30 × 1K ≈ 200K tokens | 1.5M tokens/day - fits 7+ audits/day |
| Gemini Pro (twin reasoning + gap judge + contradiction resolver) | ~50 calls × 3K tokens ≈ 150K tokens | 50 RPM, 32K TPM - fits |
| `text-embedding-004` (entity resolution + semantic redundancy) | ~500 strings × 200 tokens ≈ 100K tokens | Generous free tier - fits |
| Google STT V2 streaming | 20 min × 1 channel | 60 min/month - covers demo + 2 dev runs |
| OpenRouter swarm (4 models × 50 prompts × 500 tokens) | ~400K tokens total | `:free` daily caps vary; spread across morning/afternoon if rate-limited |
| Shopify Dev Store | unlimited | free |
| Neo4j AuraDB | ~1.5K nodes / 4.5K edges | 50K / 175K cap - 3% utilization |
| Firebase (Spark plan) | session metadata + transcripts + audio blobs | generous |

**Total marginal cost per audit during hackathon: $0.**

**Production projection:** $5-8 per audit at production volume, dominated by paid GPT/Claude inclusion in the swarm for fuller coverage and Pro-tier STT minutes. This unit economics is part of the product story - Kasparro builds commerce *infrastructure* and tools merchants can't afford to run are not tools.

## 10. Known Limitations

1. **Single-merchant scope.** No cross-merchant benchmarking ("you score 67/100 vs. category median 73/100"). Requires a population we don't yet have.
2. **Buyer prompts are LLM-generated, not from real shopper logs.** A production system would seed prompts from Shopify session search-query data; we generate them from MerchantTruths and CustomerQuestions. Risk: synthetic prompts may under-represent edge cases real shoppers actually surface.
3. **Revenue model is parameterized estimate, not measured uplift.** Every parameter is exposed as a slider; we emit ranges, not point estimates. Calibration of the *prediction* itself is shown next to it. Observed deltas after fix application are reported as ground truth; predictions are explicitly labeled.
4. **One-shot audit, not persistent monitoring.** No drift alerting. The Living Update Loop supports longitudinal audits if the merchant returns and re-runs, but we do not push notifications.
5. **Free-tier model swarm.** No GPT-4 / Claude Opus in the simulator. Reframed honestly - most agentic shopping infrastructure runs on open-weight models - but a production version would add paid models for fuller coverage of the ChatGPT and Claude exposure surfaces.
6. **Calibration is label-only.** We claim the 5-bucket labels are auditable and meaningful; we do **not** claim numerical calibration ("80% confidence ≈ 80% accuracy"). That requires a labeled validation set we don't have.
7. **No formal voice cloning.** Brand voice is preserved via in-context conditioning on transcript samples, not via a fine-tuned voice model. Acceptable for fix copy in normal cases; would need real voice cloning for a production rollout where merchants demand stylistic perfection.
8. **English-only at submission.** Multilingual agent simulation (Hindi, Spanish, Mandarin) is an elevation feature, pulled in only if Day 9 has slack.
9. **Demo "aha moment" depends on baked-in gaps in Fulcrum Coffee's catalog.** The gaps are real (we wrote weak product copy on purpose), but a third-party merchant would need our system to find their *own* gaps - which the architecture supports unchanged. This is a hackathon framing limitation, not an architectural one.
10. **Local Docker Compose for hackathon.** Not deployed publicly. Judges replicate via README.

## 11. What We'd Improve With More Time

1. **Connect to merchant's real shopper search logs** to seed buyer prompts. Most credible single improvement - turns synthetic prompts into observed intent.
2. **Cross-merchant cohort benchmarking.** Once we have ≥20 audited stores, percentile rankings per category transform every score from "is 67 good?" to "you are at the 41st percentile in your category."
3. **Persistent monitoring with drift alerts.** Weekly auto-audit cron + Slack/email when a key product's surface rate drops below a threshold. Turns the one-shot audit into a product surface that earns retention.
4. **Shopify App Store wrapper.** One-click distribution. Multi-week review process; not a hackathon item.
5. **Voice cloning for fix-copy generation.** Merchants with strong stylistic identity will demand fix copy that is indistinguishable from theirs. In-context conditioning gets ~80% there; a fine-tuned voice model gets to 95%.
6. **Multilingual agent simulation.** Same swarm, prompts re-rendered in target languages. Surfaces international AI representation collapse - a major undocumented gap for any merchant doing cross-border GMV.
7. **A/B fix mode.** Apply fix to a duplicated product variant (shadow product); re-test; only commit to the real product if the delta exceeds threshold. Demonstrates safety-first product instinct and protects the merchant from regressions.
8. **Numerical calibration validation set.** Build a labeled set of merchant-confirmed gaps and fixes, fit a calibration curve, and *then* claim numerical calibration. Requires real merchant time we don't have in 11 days.
9. **Cloud Run public deploy.** Judges (and real merchants) can self-serve onboard. DNS + IAM + cost surface; doable in a weekend post-submission.
10. **Pluggable agent providers.** Today the swarm is hard-pinned to four models. A merchant who wants to test against their actual shopper-facing agent (e.g., a custom embedded assistant) should be able to plug it in via OpenAI-compatible endpoint.

---

*Companion: `PRODUCT_DOC.md` (problem, target user, decisions, scope cuts, tradeoffs). Source of truth: `WINNING_PLAN.md` at repo root. Decision Log in `DECISION_LOG.md` documents the running history of choices made during the build.*
