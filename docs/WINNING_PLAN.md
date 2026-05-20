# ECHOMIND COMMERCE - World-Class Winning Plan

## KASPARRO Agentic Commerce Hackathon · Track 5 (AI Representation Optimizer)

> Authored: 2026-05-01 · Pivot confirmed: 2026-05-01 · Registration deadline: 2026-05-04 · Build window: 2026-05-10 → 2026-05-20 23:59 IST · Submission target: 2026-05-20 18:00 IST.

> **This document is the single source of truth.** [ECHOMIND_BLUEPRINT.md](ECHOMIND_BLUEPRINT.md) is now ancestral notes - it remains the philosophical mother of everything here, and we preserve every transferable primitive it defined, but it is no longer the spec. [RULES.md](RULES.md) and [BLUEPRINT_DIGEST.md](BLUEPRINT_DIGEST.md) are reference. This plan is the build.

> **Hard constraints (locked from user):**
> 1. **Pivot confirmed** - Echomind Commerce supersedes Echomind Expert-Twin.
> 2. **Brand identity** - Specialty coffee. Demo store: "Fulcrum Coffee Co." (rename freely).
> 3. **API budget** - Zero paid OpenAI / Anthropic credits. Available: direct Gemini API key + OpenRouter key. All paid agent calls re-routed through OpenRouter free-tier models. Architecture must work end-to-end on free tier.
> 4. **Real-world alignment** - Everything real, live, end-to-end. No synthetic responses presented as live, no scripted magic, no mocks. The "real-world user" is the merchant (you). Real Shopify, real Neo4j, real LLM calls.
> 5. **Real merchant outreach (deferred)** - Stretch goal, last-priority, build everything else first.
> 6. **Capture as much from the original Echomind blueprint as possible** - every primitive that maps to commerce is preserved and reused.

---

## TABLE OF CONTENTS

1. [The Brutal Truth (read first)](#1-the-brutal-truth)
2. [The Product - Echomind Commerce](#2-the-product--echomind-commerce)
3. [Why This Wins - Rubric Mapping](#3-why-this-wins--rubric-mapping)
4. [The Everything-Real Manifesto](#4-the-everything-real-manifesto)
5. [Architecture - Complete System](#5-architecture--complete-system)
6. [Commerce Graph Schema](#6-commerce-graph-schema)
7. [Tacit Knowledge Taxonomy (preserved from Echomind)](#7-tacit-knowledge-taxonomy)
8. [Five-Phase Socratic Interview (commerce-tuned)](#8-five-phase-socratic-interview)
9. [Frontier Scoring & Calibration Formulas (preserved)](#9-frontier-scoring--calibration-formulas)
10. [Subgraph Retrieval Strategies (preserved)](#10-subgraph-retrieval-strategies)
11. [Reasoning Trace Format (preserved)](#11-reasoning-trace-format)
12. [Living Update Loop (preserved, recommerced)](#12-living-update-loop)
13. [Entity Resolution (preserved)](#13-entity-resolution)
14. [Contradiction Detection (preserved, expanded)](#14-contradiction-detection)
15. [The Agent Swarm - OpenRouter-Native Design](#15-the-agent-swarm)
16. [Gap Detection Engine](#16-gap-detection-engine)
17. [Fix → Re-Test Closed Loop](#17-fix--re-test-closed-loop)
18. [Revenue Impact Model](#18-revenue-impact-model)
19. [The Nine Elevation Features (world-class moves)](#19-the-nine-elevation-features)
20. [UI / UX - All Five Views](#20-ui--ux--all-five-views)
21. [The Five-Minute Demo (all live)](#21-the-five-minute-demo)
22. [Day-by-Day Build Plan (10-20 May)](#22-day-by-day-build-plan)
23. [API Strategy - Gemini + OpenRouter Only](#23-api-strategy)
24. [Submission Checklist (mandatory gates)](#24-submission-checklist)
25. [Risk Register](#25-risk-register)
26. [Decision Log Seed (commit Day 1)](#26-decision-log-seed)
27. [Product Doc Skeleton](#27-product-doc-skeleton)
28. [Technical Doc Skeleton](#28-technical-doc-skeleton)
29. [Brand Identity - Fulcrum Coffee Co.](#29-brand-identity--fulcrum-coffee-co)
30. [Stretch / Undeniable Moves](#30-stretch--undeniable-moves)
31. [Open Questions](#31-open-questions)
32. [The Elevator Pitch](#32-the-elevator-pitch)

---

## 1. THE BRUTAL TRUTH

The Echomind blueprint is a digital-twin-of-an-expert product. The Kasparro hackathon is about AI agents that help shoppers buy on Shopify. Submitting Echomind unchanged scores ~0/15 on Business Relevance and disqualifies via misalignment.

We pivot. We keep **every transferable Echomind primitive** - the typed knowledge graph, the five-phase Socratic interview, the calibrated "I don't know" twin, the reasoning trace, the frontier scoring formula, the contradiction detection, the entity resolution, the decision tree builder, the living update loop, the tacit knowledge taxonomy - and we point it at **Track 5 (AI Representation Optimizer)**, the rules-confirmed highest-internship-signal track, with a real Shopify merchant problem.

The result is not a downgrade. It's the same intellectual machinery, applied to a problem with a real customer (Kasparro themselves), real revenue stakes (every Shopify merchant by 2027), and a real demo where the magic isn't curated - it's measured.

---

## 2. THE PRODUCT - ECHOMIND COMMERCE

### 2.1 One-line pitch
**Echomind Commerce turns every Shopify merchant into the agentic-commerce era's most representable store - by interviewing their tacit knowledge into a typed graph, simulating four real AI shopping agents querying their catalog, diagnosing the gaps with calibrated confidence, applying revenue-ranked fixes, and re-testing live to prove the delta.**

### 2.2 The three layers (the soul of the product)

**Layer 1 - THE MIRROR.** Show merchants how AI agents actually see them today. Run a live multi-model agent swarm (Gemini, Llama, Qwen, DeepSeek) against 50-150 buyer-intent prompts. Capture verbatim outputs. The merchant reads them and recoils.

**Layer 2 - THE TRUTH CAPTURE.** Run a 20-minute AI-driven Socratic interview with the merchant. Surface the tacit knowledge no document holds - who their products are really for, what they handle by hand, why customers actually buy. Build a typed knowledge graph live. **This is the unfair advantage no other AI-readiness tool will have.**

**Layer 3 - THE CLOSED LOOP.** Diff the agents' actual representation against the merchant's intended representation (interview graph). Produce a typed Gap Graph with calibrated confidence, revenue impact, and reasoning trace. One-click fix generation. Push to Shopify Admin API. Re-run the simulator. **Show the measured delta.**

### 2.3 The differentiating insight
Every other AI-readiness tool in 2026 will be a static checklist or a RAG-over-docs scan. **Echomind Commerce is the only tool where the diagnostic ground truth comes from the merchant's brain, captured by Socratic AI, rather than from the documents the merchant already failed to write.** That's the moat.

### 2.4 What dies, what lives, what's reincarnated from the original Echomind

| Original primitive | Status | New role in commerce |
|---|---|---|
| 5-phase Socratic engine | ✅ Reused, retuned | 5 commerce phases (§8) |
| Typed knowledge graph (6 nodes / 9 edges) | ✅ Reused, expanded to 11 node types | Same architectural backbone (§6) |
| Real-time graph build during interview | ✅ Reused | Same UX magic moment |
| Calibrated confidence + "I don't know" | ✅ Reused, applied to gaps + fixes | Single biggest credibility differentiator |
| Reasoning trace per twin answer | ✅ Reused | Now per-gap and per-fix |
| Frontier scoring formula | ✅ Reused, retuned weights | Now ranks gaps by revenue × fixability × confidence (§9) |
| Subgraph retrieval (multi-strategy) | ✅ Reused | Used during fix generation (§10) |
| Decision Tree Builder | ✅ Reused | Captures merchant's policy decision trees (§14) |
| Contradiction detection (CONTRADICTS edges + Cypher + Gemini) | ✅ Reused, expanded | Detects merchant↔store, store↔store, merchant↔agent contradictions (§14) |
| Entity resolution via embedding | ✅ Reused | Dedups product names across agent outputs (§13) |
| Living Update Loop | ✅ Reused, post-audit version | Merchant reviews each gap, accept/dismiss/customize, system learns (§12) |
| Multiple extraction passes | ✅ Reused | Applied to interview AND each agent output |
| Tacit knowledge taxonomy (6 cats) | ✅ Reused | Tags every MerchantTruth node (§7) |
| Confidence/Calibration Dashboard (radar chart) | ✅ Reused | Becomes "AI Readiness Radar" |
| Coverage heatmap (treemap) | ✅ Reused | "AI Representation Coverage" by category |
| Comparison Dashboard | ✅ Reused | Side-by-side: intent vs. agent representation |
| Three-view frontend (interview/graph/twin) | ✅ Reused, +2 views | Now 5 views (§20) |
| Voice-first interview (Google STT V2) | ✅ Reused | Real STT streaming on demo day |
| TTS for questions | ⚠️ Stretch | Stub for hackathon; real for v2 |
| Graph versioning + audit trail | ✅ Reused | Firestore changelog + Neo4j snapshots |
| Cost model | ✅ Reused, retuned for free-tier | $0 for hackathon, $2-5 per merchant in production |
| Cloud Run service architecture | ⚠️ Local for hackathon | Documented for v2; local Docker compose for demo |
| `prompts.py` centralization | ✅ Reused - non-negotiable | "60% of debugging is prompt tuning" remains true |
| `gemini_service.py` retry+rate-limit wrapper | ✅ Reused, extended to OpenRouter | All LLM calls go through this layer |
| 24-hour build sprint structure | ✅ Reused, expanded to 11 days | (§22) |
| Chess demo content | ❌ Dropped | Coffee replaces it |
| Digital immortality framing | ❌ Dropped | Agentic representability replaces it |
| 2-hour interview length | ❌ Compressed to 20 min | Realistic for merchants |
| Multi-LLM agent simulator | 🆕 New for commerce | Core of Layer 1 (§15) |
| Closed-loop fix → re-test | 🆕 New for commerce | Core of Layer 3 (§17) |
| Revenue impact model | 🆕 New for commerce | §18 |
| Nine elevation features | 🆕 New | §19 |

We retain 22 of the original blueprint's primitives. Five are dropped because they don't transfer (chess content, digital immortality, 2-hour length, plus minor scoping). The architectural soul is intact.

---

## 3. WHY THIS WINS - RUBRIC MAPPING

| Criterion | Weight | How we win it |
|---|---|---|
| **Product Thinking & Documentation** | 25% | Sharp ≤3-page Product Doc + comprehensive Technical Doc + Decision Log started Day 1 with 15 seeded entries (§26). Scope cuts explicit. Every decision references real merchant pain. **Documentation gate cleared before Day 1 ends.** |
| **Technical Execution & Architecture** | 25% | AI/deterministic boundary explicitly diagrammed (§5.4). Failure handling for ≥5 named modes (§25). Atomic commits ≥45 over 11 days. AI vs. code split: Cypher does graph math, LLMs do NLP, calibrator does threshold logic - never crossed. |
| **Product Experience** | 20% | Five coherent views (§20). Live graph growth during interview. Real-time agent swarm with streaming tokens visible. Before/after delta visualization. Calibration badges everywhere - including honest "I don't know" labels. |
| **Business Relevance** | 15% | Solves the *exact* problem Kasparro builds infrastructure for. Concrete revenue model. Ties directly to all three trends Kasparro's own cover page calls out (ChatGPT purchase flow, Google AI Mode, Shopify Agentic Plan). |
| **Originality & Insight** | 15% | Nine elevation features (§19), no team will combine them. Tacit-knowledge-as-ground-truth is structurally novel. "Calibrated diagnostic" is a category nobody is shipping. |

### Off-rubric multipliers
- **Track 5 internship-signal advantage** (per rules text).
- **Documentation-first Day 1** = clear the mandatory hard gate before code is committed.
- **Atomic git history** as graded artifact.
- **Decision Log** = "single strongest signal that a team thinks before it codes - hardest thing to fake." 15 entries seeded Day 1, +1/day after.
- **Calibrated honesty** as product principle = directly answers Kasparro's "AI assistants without real product logic" red flag.

---

## 4. THE EVERYTHING-REAL MANIFESTO

The user's hard constraint: nothing fake, synthetic, scripted, or simulated-as-live. Real merchant. Real Shopify. Real LLMs. Real graph. Real fixes. Real deltas.

### 4.1 What "real" means per component

| Component | Real means | Banned shortcuts |
|---|---|---|
| Shopify store | Real Partner account + dev store + populated catalog (synthetic *products* allowed by rules; *infrastructure* must be real Shopify) | Hardcoded JSON, mocked GraphQL responses |
| Catalog ingestion | Real Admin GraphQL pulls during demo | Pre-loaded fixtures presented as live ingest |
| Merchant interview | Live audio interview on demo day, real Google STT V2 streaming | Pre-recorded scripted "interview" replayed |
| Knowledge graph | Real Neo4j AuraDB free tier, Bolt protocol writes | Pre-seeded graph imported before demo |
| Agent swarm | Real OpenRouter calls + real Gemini calls during demo | Cached agent outputs from prior runs labelled as live |
| Gap detection | Deterministic Cypher + real LLM judge calls | Hand-curated gap list shown as auto-detected |
| Fix application | Real Shopify Admin GraphQL mutation that changes the live dev store | Showing a diff without writing |
| Re-test | Re-runs the actual simulator after fix is applied; shows real delta | Faked "after" screenshot |
| Auth | Real Firebase Google Sign-In | Bypass flag |
| Demo recording | Single-take or transparently re-taken; failures visible if they occur | Edited cuts that hide failures |

### 4.2 The realness checkpoint
Every Day's acceptance test ends with:
> *"If a judge cloned this repo right now, signed into the demo merchant Shopify store, and ran the loop, would they get genuine results?"*
> If the answer is "no," it goes back on the todo list.

### 4.3 The one acceptable form of "synthetic"
Rules explicitly allow synthetic Shopify product data (i.e., made-up coffee SKUs in our dev store). What's *not* allowed by our manifesto: mocking infrastructure. The products may be fictional; the Shopify, the Neo4j, the LLMs, the auth, the API mutations - all real.

### 4.4 The "real-world user" is you
You are the merchant. You created Fulcrum Coffee Co. You know its products, its target customer, its policies, its tacit knowledge - because you wrote them. The Socratic interview captures *your* brain. The agent swarm shows *you* how AI sees *your* store. The fixes apply to *your* live store. End-to-end, every node in the system is anchored to a real human (you) acting through real infrastructure.

If we later recruit a real third-party Shopify merchant (deferred stretch), the architecture supports it without changes.

---

## 5. ARCHITECTURE - COMPLETE SYSTEM

### 5.1 High-level data flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       MERCHANT (You - real user)                         │
└──────────────┬───────────────────────────────────────────────────┬──────┘
               │                                                   │
               │ Google Sign-In (Firebase Auth)                    │ Voice + Text
               ▼                                                   ▼
┌──────────────────────────┐                       ┌──────────────────────────┐
│  Next.js 14 Frontend     │                       │   Browser Mic API        │
│  (5 views, §20)          │                       │   (audio chunks → WS)    │
└──────┬───────────────────┘                       └──────────┬───────────────┘
       │ REST + WebSocket                                     │
       ▼                                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend (Python 3.11)                      │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ /onboard │  │ /interview  │  │  /simulate   │  │ /diagnose /fix  │  │
│  └────┬─────┘  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘  │
└───────┼───────────────┼─────────────────┼───────────────────┼────────────┘
        │               │                 │                   │
        │ Admin GraphQL │ Gemini Flash    │ Agent Swarm       │ Gemini Pro
        │               │ + STT V2        │ (OpenRouter)      │ + Cypher
        ▼               ▼                 ▼                   ▼
┌──────────────┐ ┌─────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  Shopify     │ │ Google STT  │  │   OpenRouter     │  │  Gemini API     │
│  Dev Store   │ │  V2 streamg │  │  • Llama-3.3 70B │  │  • Flash (extr) │
│  (real)      │ │  (real)     │  │  • Qwen-2.5 72B  │  │  • Pro (judge)  │
│              │ │             │  │  • DeepSeek V3   │  │  • embed-004    │
│  • Admin API │ │ Free tier:  │  │  • Gemini 2.0    │  │                 │
│  • Storefrnt │ │ 60 min/mo   │  │  (free-tier MWFs)│  │  Free tier      │
└──────────────┘ └─────────────┘  └──────────────────┘  └─────────────────┘
                                          │                    │
                                          └────────┬───────────┘
                                                   ▼
                              ┌────────────────────────────────────┐
                              │  Persistence layer                 │
                              │  ┌──────────────────────────────┐  │
                              │  │  Neo4j AuraDB Free           │  │
                              │  │  (50K nodes / 175K edges)    │  │
                              │  │  Typed graph, vector index   │  │
                              │  └──────────────────────────────┘  │
                              │  ┌──────────────────────────────┐  │
                              │  │  Firebase Firestore          │  │
                              │  │  Sessions, transcripts,      │  │
                              │  │  agent runs, change log      │  │
                              │  └──────────────────────────────┘  │
                              │  ┌──────────────────────────────┐  │
                              │  │  Firebase Cloud Storage      │  │
                              │  │  Audio, exports              │  │
                              │  └──────────────────────────────┘  │
                              └────────────────────────────────────┘
```

### 5.2 Backend service layout

```
backend/
├── api/
│   ├── endpoints/
│   │   ├── onboard.py       # Shopify connect + catalog crawl
│   │   ├── interview.py     # WS for live interview
│   │   ├── simulate.py      # agent swarm orchestration
│   │   ├── diagnose.py      # gap detection + ranking
│   │   ├── fix.py           # fix gen + Shopify mutate + re-test
│   │   ├── audit.py         # audit dashboard data
│   │   ├── graph.py         # graph queries (search, node detail)
│   │   └── auth.py          # session validation
│   └── schemas/             # pydantic 2 models - one source of typing truth
├── core/
│   ├── socratic/
│   │   ├── engine.py        # main interview loop
│   │   ├── question_gen.py  # Gemini Flash next-question
│   │   ├── extractor.py     # Gemini Flash typed extraction
│   │   ├── phase_manager.py # 5-phase advancement triggers
│   │   ├── gap_analyzer.py  # interview gap detection (graph completeness)
│   │   ├── frontier_scorer.py    # what to ask next
│   │   ├── redundancy_checker.py # don't repeat semantic equivalents
│   │   └── decision_tree_builder.py  # narrative → if-then JSON
│   ├── agents/
│   │   ├── base.py          # AgentClient ABC
│   │   ├── openrouter.py    # OpenRouter client (one path for all 4)
│   │   ├── gemini_agent.py  # direct Gemini agent simulator
│   │   ├── prompt_gen.py    # buyer-intent prompt generator
│   │   ├── runner.py        # concurrency + retries + persistence
│   │   └── adversarial.py   # "frustrated buyer" mode (§19.7)
│   ├── diagnose/
│   │   ├── cypher_diff.py   # deterministic graph diff
│   │   ├── judge.py         # Gemini Pro classifier with rubric
│   │   ├── calibrator.py    # 5-bucket calibration
│   │   ├── revenue_model.py # parameterized revenue impact
│   │   └── ranker.py        # frontier-style gap ranking
│   ├── fix/
│   │   ├── copy_generator.py    # product copy / FAQ / structured data
│   │   ├── policy_clarifier.py  # decision-tree-based policy fixes
│   │   ├── shopify_writer.py    # real Admin API mutations
│   │   └── retest_orchestrator.py # scoped re-run + delta
│   ├── twin/                # the "diagnostic twin" - preserved from Echomind
│   │   ├── query_analyzer.py
│   │   ├── subgraph_retriever.py # 4 retrieval strategies (§10)
│   │   ├── reasoning_chain.py
│   │   └── confidence_calibrator.py
│   └── contradiction/
│       ├── detector.py      # Cypher + Gemini hybrid
│       └── resolver.py      # context-aware resolution
├── graph/
│   ├── neo4j_client.py
│   ├── operations.py        # CRUD + batched writes
│   ├── queries.py           # named Cypher queries
│   ├── embeddings.py        # text-embedding-004 wrapper
│   └── schema.py            # node + edge types (§6)
├── services/
│   ├── shopify_service.py   # Admin GraphQL + Storefront client
│   ├── stt_service.py       # Google STT V2 streaming
│   ├── llm_service.py       # central retry + rate-limit + provider router
│   ├── firebase_service.py  # Firestore + Storage + Auth admin
│   └── audio_service.py
├── config/
│   ├── settings.py          # pydantic Settings, all env vars
│   └── prompts.py           # ⭐ ALL prompts - highest-leverage file
└── main.py                  # FastAPI app + WS routes
```

```
frontend/
├── app/
│   ├── (auth)/
│   ├── onboard/             # Shopify connect wizard
│   ├── interview/[id]/      # 3-column live interview
│   ├── audit/[storeId]/     # main dashboard
│   ├── simulate/[runId]/    # agent comparison view
│   ├── diff/[gapId]/        # gap deep-dive
│   ├── graph/[storeId]/     # full graph viz (force-directed)
│   ├── policies/[type]/     # decision tree visualizer
│   ├── replay/[auditId]/    # the Replay Theater (§19)
│   └── api/                 # NextAuth, Shopify OAuth callback
├── components/
│   ├── graph/               # ForceGraph2D wrappers + node-detail panel
│   ├── interview/           # transcript pane, question pane, mini-graph pane
│   ├── agents/              # agent cards, streaming token display
│   ├── gaps/                # gap card, calibration badge, reasoning trace
│   ├── decision-trees/      # flowchart renderer
│   └── ui/                  # shadcn/ui primitives
├── lib/
│   ├── api-client.ts        # typed REST client (zod-validated)
│   ├── ws-client.ts         # WS reconnection + dedup
│   └── revenue-model.ts     # client-side parameter sliders
└── styles/
```

### 5.3 Stack (every entry real, every entry working)

**Backend**: Python 3.11, FastAPI 0.115, uvicorn, websockets 13, pydantic 2.9, neo4j 5.25, google-generativeai 0.8, google-cloud-speech 2.27, openai (for OpenRouter compatibility) 1.50, firebase-admin 6.6, httpx, numpy, tenacity (retries).

**Frontend**: Next.js 14.2, React 18.3, TypeScript 5.5, TailwindCSS 3.4, shadcn/ui, react-force-graph-2d 1.25, @tanstack/react-query 5.50, recharts (radar chart), firebase 10.14, zod (runtime validation).

**Data**: Neo4j AuraDB Free, Firebase Firestore, Firebase Cloud Storage, Firebase Auth.

**LLMs**: Gemini 2.0 Flash, Gemini 2.0 Pro (or experimental), `text-embedding-004` (all direct Gemini API). OpenRouter for `meta-llama/llama-3.3-70b-instruct:free`, `qwen/qwen-2.5-72b-instruct:free`, `deepseek/deepseek-chat:free`, and `google/gemini-2.0-flash-exp:free` (redundant but lets us A/B Gemini-direct vs. Gemini-routed). All free tier (§23).

**Speech**: Google Cloud STT V2 streaming, `long` model, auto-punctuation, word time offsets, voice activity events. Free tier covers the demo (60 min/month).

**Infra**: Docker Compose (one-command boot for judges). Optional Cloud Run on Day 11 if time. Otherwise local-only - judges replicate via README.

### 5.4 The AI vs deterministic boundary (judge gold)

| Capability | Code or LLM? | Why |
|---|---|---|
| Shopify API I/O | Code | Deterministic, schemas known |
| Neo4j writes/reads | Code | Same |
| Cypher gap-detection queries | Code | Graph algebra, deterministic |
| Revenue model arithmetic | Code | Math is math; transparent parameters |
| Confidence calibration thresholds | Code | Threshold logic must be auditable |
| Phase advancement triggers | Code | Statistical predicates |
| Entity resolution scoring | Code (with LLM embeddings as input) | Cosine similarity, threshold-based |
| Buyer prompt generation | LLM | Natural language synthesis |
| Transcript → typed nodes | LLM | Pure NLP |
| Next-question generation | LLM | Conversational reasoning |
| Agent role-play | LLM | They ARE the things being measured |
| Gap classification | LLM | Semantic categorization |
| Fix copy generation | LLM | Natural language |
| Policy decision tree extraction | LLM (then code-formalized) | Capture conversational logic, formalize structurally |

**Rule**: anything requiring ground truth or determinism is code; anything requiring natural-language understanding is LLM. We do not ask LLMs to do math, and we do not ask Cypher to read prose. **This sentence belongs verbatim in the Technical Doc.**

### 5.5 API endpoints (verbatim spec)

```
POST   /api/onboard/shopify-oauth-start    → {redirect_url}
GET    /api/onboard/shopify-oauth-callback → {store_id, ingest_job_id}
GET    /api/onboard/ingest/{job_id}        → {status, products, policies, reviews}

POST   /api/interview/start                → {session_id, ws_url}
WS     /api/interview/ws/{session_id}      → bidirectional:
                                                in:  audio_chunk, text_input, control
                                                out: interim_transcript, final_transcript,
                                                     question, extraction, phase_change,
                                                     graph_update, progress
POST   /api/interview/{id}/end             → {summary, node_count, edge_count}

POST   /api/simulate/run                   → {run_id, prompt_count, agent_count}
WS     /api/simulate/ws/{run_id}           → live agent token streams + per-agent progress
GET    /api/simulate/{run_id}              → {agents: [{model, prompts, responses, surface_rates}]}

POST   /api/diagnose/run                   → {diagnose_id}
GET    /api/diagnose/{id}                  → {gaps: [Gap], readiness_score, calibration_summary}
GET    /api/diagnose/{id}/gap/{gap_id}     → {gap, reasoning_chain, source_nodes, fix_candidates}

POST   /api/fix/generate/{gap_id}          → {fix_id, proposed_text, predicted_delta_range}
POST   /api/fix/apply/{fix_id}             → {applied, shopify_resource_id}
POST   /api/fix/retest/{fix_id}            → {retest_run_id, delta}

GET    /api/audit/{store_id}               → {readiness_score, gap_count, fix_count, last_audit_at}
GET    /api/graph/{store_id}               → {nodes, edges} (paginated)
GET    /api/graph/{store_id}/search?q=     → {nodes}
GET    /api/graph/{store_id}/node/{node_id}→ {node, neighbors, contradictions}

GET    /api/replay/{audit_id}/timeline     → ordered events for Replay Theater
```

### 5.6 Cost model (real, free-tier first)

Per merchant audit:
- Gemini Flash: extraction (~30 calls × ~2K tokens) + question gen (~30 calls × ~1K tokens) ≈ 90K tokens. Free tier: 1.5M tokens/day.
- Gemini Pro judge + twin: ~50 calls × ~3K tokens ≈ 150K tokens. Free tier: 50 RPM, 32K TPM - fits.
- text-embedding-004: ~500 strings × ~200 tokens ≈ 100K tokens. Free.
- Google STT V2: 20 min × 1 channel = 20 streaming-minutes. Free tier: 60 min/month.
- OpenRouter free-tier swarm: 4 models × 50 prompts × ~500 tokens response = ~100K tokens × 4 = 400K. Free-tier daily caps vary by model; spread across morning/afternoon if rate-limited.
- Shopify Dev Store: free.
- Neo4j AuraDB Free: free.
- Firebase: free (Spark plan covers our usage).

**Total marginal cost per audit during hackathon: $0.** Documented in Technical Doc as "free-tier-first architecture, scales to $5-8/audit at production volume."

---

## 6. COMMERCE GRAPH SCHEMA

11 node types, 12 edge types. Six are direct ports from the original Echomind blueprint; five are commerce-native; one (Concept) is dropped because it doesn't add value here.

### 6.1 Node types

| # | Type | Source | Key fields |
|---|---|---|---|
| 1 | `Product` | Shopify | id, shopify_gid, title, description, price, currency, image_urls[], tags[], options, variants_summary, embedding (768d), confidence, ingested_at |
| 2 | `Policy` | Shopify pages + metafields | id, type (return/shipping/warranty/exchange), text, scope (specific products / global), confidence, source_url |
| 3 | `TrustSignal` | Shopify reviews + storefront | id, type (review/badge/cert/testimonial), value, attached_to, confidence |
| 4 | `MerchantTruth` (= Echomind's Heuristic + Experience + Rule fused) | Interview | id, statement, category (positioning/audience/edge_case/relationship/style), tacit_level (explicit/semi-tacit/deeply-tacit), source_phase, confidence, embedding |
| 5 | `Decision` (preserved from Echomind) | Interview | id, question, context, outcome, conditions[], frequency (always/usually/sometimes/rarely), confidence |
| 6 | `Pattern` (preserved from Echomind) | Interview | id, name, description, indicators[], typical_response, confidence |
| 7 | `CustomerQuestion` | Interview + agent prompts | id, question, frequency, intent_class (discover/compare/objection/post-purchase), embedding |
| 8 | `BuyerPrompt` | Generated for simulator | id, prompt_text, intent_class, generated_from_truths[], embedding |
| 9 | `AgentRepresentation` | Agent swarm output | id, agent_model, buyer_prompt_id, response_text, surfaced_products[], cited_policies[], confidence_in_recommendation, latency_ms, captured_at |
| 10 | `Gap` | Diagnose engine | id, type (omission/contradiction/ambiguity/hallucination/dark_zone), severity (0..1), revenue_impact_usd_monthly, calibration_label (5 buckets), reasoning_chain (text), affected_products[] |
| 11 | `FixSuggestion` | Fix generator | id, gap_id, fix_type (copy_rewrite/faq_add/policy_clarify/metafield_add/structured_data), proposed_text, applied (bool), applied_at, predicted_delta_range, observed_delta |

### 6.2 Edge types (12)

| Edge | From → To | Properties |
|---|---|---|
| `DESCRIBES` | MerchantTruth → Product | weight, scope |
| `COVERS` | Policy → Product | weight, exception_rule |
| `MENTIONS` | AgentRepresentation → Product | confidence, sentiment |
| `MISREPRESENTS` | AgentRepresentation → Product | severity, delta_description |
| `REVEALS` | AgentRepresentation → Gap | weight |
| `HARMS` | Gap → Product | revenue_impact_share |
| `FIXES` | FixSuggestion → Gap | predicted_delta |
| `CONTRADICTS` (preserved) | (any node) → (any node) | resolution, context_a, context_b |
| `TRIGGERS` (preserved) | Decision → Action / Pattern → Decision | condition, probability |
| `EXCEPTION_TO` (preserved) | Policy → Policy / MerchantTruth → Policy | condition, frequency |
| `ANSWERS` | Policy / MerchantTruth → CustomerQuestion | confidence |
| `SIMILAR_TO` | (any) → (any) | embedding_similarity |

### 6.3 Cardinality target (per audit)

- Product: 30-60 (Shopify catalog)
- Policy: 5-12
- TrustSignal: 20-80
- MerchantTruth: 60-120 (interview output)
- Decision: 15-30
- Pattern: 10-20
- CustomerQuestion: 40-80
- BuyerPrompt: 50-150
- AgentRepresentation: 200-600 (4 agents × 50-150 prompts)
- Gap: 15-40
- FixSuggestion: 15-40

Total: ~500-1,500 nodes, ~1,500-4,500 edges per audit. Comfortably fits AuraDB Free (50K/175K).

---

## 7. TACIT KNOWLEDGE TAXONOMY (preserved from Echomind §2.3)

Every `MerchantTruth` node is tagged with one of these categories. The taxonomy is core Echomind IP - preserved verbatim, retuned to commerce.

| # | Category | Commerce example | Extraction difficulty |
|---|---|---|---|
| 1 | **Procedural** | "When a customer requests an exchange, we ship the new item before receiving the return." | Low |
| 2 | **Conditional Heuristic** | "If a customer asks about caffeine content, lead with origin not roast level." | Medium |
| 3 | **Experiential Pattern** | "Customers who buy our Ethiopian first usually come back for the Kenyan within 6 weeks." | Medium |
| 4 | **Intuitive Judgment** | "I just *know* this customer is going to ask for a refund - the language pattern matches three prior cases." | High |
| 5 | **Edge Case Knowledge** | "If shipping to Hawaii, USPS Priority is unreliable past December 10 - I switch to UPS automatically." | Med-High |
| 6 | **Meta-Knowledge** | "I know my product copy is weak on grind size guidance, but I've never had time to fix it." | Medium |

**Why this matters for the demo**: judges asking "isn't this just RAG over docs?" get the answer: *"RAG can't extract any of categories 4, 5, or 6 - that knowledge has never been written down. Our Socratic interview surfaces it as graph nodes, and those nodes are the diagnostic ground truth other tools can't access."*

---

## 8. FIVE-PHASE SOCRATIC INTERVIEW (commerce-tuned)

Direct port of Echomind's five-phase methodology. Same machinery (phase manager, frontier scorer, gap analyzer, redundancy checker, question generator), retuned content.

### 8.1 The five phases

| # | Phase | Goal | Sample opener | Phase advance trigger |
|---|---|---|---|---|
| 1 | **Brand Mapping** | Capture positioning, voice, target buyer | "If a customer described your brand to a friend in one sentence, what would you want them to say - and what do they actually say?" | ≥4 high-confidence MerchantTruth nodes in `positioning` category, each with ≥2 outbound edges |
| 2 | **Product Truths** | Surface tacit product knowledge - fit, failure modes, hidden differentiators | "Walk me through your top product. Who buys it that you wish wouldn't, and why?" | ≥60% of `Product` nodes have ≥1 incoming `DESCRIBES` from a non-trivial MerchantTruth |
| 3 | **Customer Reality** | Capture the questions, objections, and edge cases customers actually surface (especially in DMs / email / phone) | "What's a question customers ask you that's never made it to your FAQ?" | ≥10 `CustomerQuestion` nodes with ≥1 `ANSWERS` edge each |
| 4 | **Policy Edge Cases** | Surface tacit policy decisions - when do rules bend, who gets exceptions | "When does your return policy actually bend? What's the rule you'd never write down but always follow?" | ≥3 `Decision` nodes built into formal trees, ≥2 `EXCEPTION_TO` edges per Policy |
| 5 | **Trust Signals** | Why customers choose you over the cheaper option | "Why do customers choose you over Amazon? What do they say in reviews you wish all buyers saw first?" | ≥5 `TrustSignal` nodes connected to MerchantTruth, ≥2 `Pattern` nodes recognized |

### 8.2 Question generation (preserved Echomind algorithm)

Centralized prompt in `backend/config/prompts.py`. Every question generation receives:
- Current phase + question count + elapsed minutes
- Domain (e.g., "specialty coffee retail")
- Full graph stats (node counts by type, edge density, coverage map)
- Top 3 frontier nodes (highest gap score, §9)
- Last 5 Q&A pairs (verbatim)
- Tacit-knowledge category currently underrepresented

Output rules (preserved verbatim from Echomind):
- Exactly one question
- Conversational, not interview-formal
- Phase-appropriate style (broad in phase 1, specific in phase 4)
- `follow_up_if_brief` field (the next question if merchant gives ≤10-word answer)
- No semantic repeats (redundancy_checker validates against last 30 questions)

### 8.3 The "10,000 micro-questions" - honest accounting (preserved framing, retuned numbers)

Per merchant audit:
- **Verbal Q&A**: 30-50 spoken questions (the visible ones)
- **Internal extraction prompts**: ~120 (each transcript chunk extracted independently)
- **Buyer-intent prompts**: 50-150 (the simulator)
- **Per-agent gap-classification calls**: ~200 (one per AgentRepresentation × Gap candidate)
- **Decision-tree decomposition prompts**: ~80
- **Contradiction probe prompts**: ~40

Total LLM-mediated micro-questions: **~5,000-8,000 per audit.** Honest accounting; defensible if a judge unpacks it.

---

## 9. FRONTIER SCORING & CALIBRATION FORMULAS (preserved verbatim)

### 9.1 Frontier scoring (preserved from Echomind §4.4, retuned for commerce)

For interview question selection (which graph node is the highest-priority gap to probe next):

```
frontier_score(node) =
    0.30 × depth_need
  + 0.25 × connectivity_gap
  + 0.15 × recency_decay
  + 0.20 × centrality (PageRank approx, incrementally maintained)
  + 0.10 × phase_weight

where:
  depth_need        = 1 - confidence(node)
  connectivity_gap  = 1 - (outbound_edges(node) / expected_edges_for_type)
  recency_decay     = exp(-Δt / 600s)  // last touched
  centrality        = personalized PageRank from Product nodes
  phase_weight      = 1.0 if node.category fits current phase else 0.4
```

### 9.2 Gap ranking (commerce-specific repurposing of frontier formula)

For sorting Gap nodes by which to fix first:

```
gap_priority(gap) =
    0.40 × revenue_impact_normalized
  + 0.20 × confidence (only `confident` or `certain` rank high; `uncertain` and below are deprioritized - Echomind's calibration discipline)
  + 0.20 × fixability (does FixSuggestion exist with predicted_delta_range > 10%?)
  + 0.10 × affected_products_share
  + 0.10 × agent_consensus (do multiple agents reveal this gap?)
```

`uncertain` gaps surface but are flagged as "verify first." `low_confidence` gaps are hidden by default but visible in advanced view. `dont_know` gaps are listed under "needs more data" - never presented as actionable.

### 9.3 Calibration formula (preserved verbatim from Echomind §6.5)

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

### 9.4 The critical distinction (preserved verbatim from blueprint)

> "I don't know" = coverage <0.15 (no relevant nodes in subgraph - we lack information).
> "I'm uncertain" = nodes exist but low-confidence / contradictory / sparse - we have information but it's not solid.

This distinction is product principle. Surface both labels with different colors and different messages. Judges will love it.

---

## 10. SUBGRAPH RETRIEVAL STRATEGIES (preserved from Echomind, applied to fix generation)

When generating a Fix for a Gap, we retrieve a relevant subgraph using four strategies (preserved verbatim from Echomind §6.3), combined and deduplicated:

1. **Direct concept match + 2-hop expansion** - nodes naming entities in the gap, expanded 2 hops.
2. **Embedding semantic search** - top-K most similar nodes via `text-embedding-004` cosine.
3. **Decision-specific retrieval** - if gap implicates a policy, retrieve the relevant Decision node + its tree.
4. **Contradiction-aware retrieval** - pull all CONTRADICTS edges touching the gap's affected nodes.

Combined → deduped (entity resolution, §13) → ranked by relevance × confidence × recency → fed into Gemini Pro fix-copy prompt.

---

## 11. REASONING TRACE FORMAT (preserved verbatim from Echomind §6.4)

Every Gap and every FixSuggestion exposes a reasoning trace structured as:

```json
{
  "answer": "...",
  "reasoning_chain": [
    {"step": 1, "claim": "...", "source_node_ids": [...], "confidence": 0.x},
    {"step": 2, ...},
    ...
  ],
  "knowledge_sources_used": [{"node_id": "...", "type": "MerchantTruth", "relevance": 0.x}, ...],
  "contradictions_resolved": [{"between": [a, b], "resolution": "..."}],
  "confidence": 0.x,
  "calibration": "confident",
  "uncertainty_type": null  | "data_sparse" | "data_contradictory" | "out_of_domain"
}
```

UI renders this as an expandable accordion under each gap card. Each `node_id` is clickable → jumps to graph view.

**This is the single biggest trust mechanism.** Judges asking "how do we know the gap is real?" get a click-by-click audit trail back to specific MerchantTruth nodes the merchant said in interview, specific AgentRepresentation outputs the agents produced live, specific contradictions resolved.

---

## 12. LIVING UPDATE LOOP (preserved from Echomind §11, recommerced)

Post-audit, the merchant enters the Living Update Loop:

1. Review each Gap → accept / dismiss / customize.
2. Edit MerchantTruth nodes the system extracted incorrectly.
3. Add MerchantTruths the system didn't catch.
4. Resolve flagged contradictions explicitly.
5. Rate fix quality 1-5.
6. Trigger re-extraction over the original transcript with corrections applied.

Every mutation is timestamped in Firestore changelog + Neo4j snapshotted. **The graph versions over time. Audits become longitudinal.** This is the retention story - answers the blueprint's "no retention model" weakness directly.

---

## 13. ENTITY RESOLUTION (preserved verbatim from Echomind §11)

Across multiple agent outputs and multiple extraction passes, the same entity gets named differently ("Yirgacheffe" / "YGC" / "Yirgacheffe Natural" / "the Ethiopian"). Entity resolution dedupes:

```
resolve(name_a, name_b):
  if levenshtein(name_a, name_b) / max_len < 0.3: return MERGE
  if cosine(embed(name_a), embed(name_b)) > 0.92: return MERGE
  if Gemini-disambiguate({a, b, context}).same_entity == true and confidence > 0.85: return MERGE
  else: return DISTINCT
```

Run after each extraction pass and after each agent run. Merged nodes accumulate `mention_count` and `aliases[]` field.

Without this, surface-rate calculations are garbage (an agent mentioning "YGC" 5 times and "Yirgacheffe" 3 times appears as 0% surface rate for either name). This is load-bearing.

---

## 14. CONTRADICTION DETECTION (preserved + expanded)

Echomind's first-class contradiction primitive, expanded for commerce. Three contradiction classes:

### 14.1 Internal store contradictions (Policy↔Policy, Policy↔Product)
- Cypher heuristic: same-scope policies with conflicting numerical values (e.g., shipping page says "10 days," FAQ says "5-7 days").
- Example detector:
  ```cypher
  MATCH (a:Policy), (b:Policy)
  WHERE a.type = b.type AND a.scope = b.scope AND a.id < b.id
    AND a.text_embedding <> b.text_embedding  // cosine < 0.85
  CALL {WITH a,b RETURN gemini_judge(a.text, b.text) AS j}
  WITH a, b, j WHERE j.contradicts = true
  MERGE (a)-[r:CONTRADICTS {resolution: j.resolution, detected_at: timestamp()}]->(b);
  ```

### 14.2 Merchant↔store contradictions (MerchantTruth↔Policy / Product)
- Merchant said in interview: "We always free-ship over $40."
- Store data says: "Free shipping over $50."
- Detected by Gemini Pro semantic check against MerchantTruth statements.
- Surfaces as a Gap of type `contradiction`.

### 14.3 Merchant↔agent contradictions (MerchantTruth↔AgentRepresentation)
- The headline gap class. Merchant said "chocolate-forward Yirgacheffe," agent says "fruity acidic." → Gap with reasoning trace pointing to both nodes.

### 14.4 Decision Tree Builder (preserved from Echomind §2.4)

For each policy or major decision (returns, exchanges, escalation), Gemini extracts a structured if-then tree from the merchant's narrative answer:

```json
{
  "decision": "Refund or exchange?",
  "tree": {
    "if": "item_unopened AND within_30_days",
    "then": {"action": "full_refund", "confidence": 0.95},
    "else_if": "item_opened AND within_14_days AND defect_reported",
    "then": {"action": "exchange_or_refund", "confidence": 0.85},
    ...
    "else": {"action": "case_by_case", "confidence": 0.4, "note": "merchant intuition required"}
  }
}
```

The tree is rendered as a flowchart in `/policies/[type]`. Agents are tested directly against the tree by sending edge-case prompts and checking whether their answers match each leaf. **This is unique to us. No other AI-readiness tool will have a formal merchant decision tree they can test agents against.**

---

## 15. THE AGENT SWARM - OPENROUTER-NATIVE DESIGN

### 15.1 Lineup (4 agents, all free-tier, all real)

| Slot | Provider | Model | Represents | Why included |
|---|---|---|---|---|
| 1 | Direct Gemini API | `gemini-2.0-flash-exp` | Google AI Mode / Google Shopping integration | Most likely real-world AI shopping agent (Google AI Mode powers a meaningful share of agentic search) |
| 2 | OpenRouter | `meta-llama/llama-3.3-70b-instruct:free` | Meta AI + most open-weight agent frameworks | Llama-class is the most common open-weight choice in production agent stacks |
| 3 | OpenRouter | `qwen/qwen-2.5-72b-instruct:free` | Alibaba ecosystem + China-region agentic shopping | Captures non-Western agent diversity |
| 4 | OpenRouter | `deepseek/deepseek-chat:free` (DeepSeek V3) | Emerging frontier open weights | Captures the "new wave" of cost-efficient agent backends |

If user later approves a small budget (<$5), we can add `openai/gpt-4o-mini` and `anthropic/claude-3-haiku` via OpenRouter for the final demo recording - but the architecture must work without them.

### 15.2 The narrative reframing (rock solid)

**We do NOT pretend Llama is GPT-5.** We label every column honestly. The framing:

> "AI shopping agents in 2026 run on a diverse model ecosystem. ChatGPT and Google AI Mode are visible because they're consumer products, but the long tail of agentic shopping infrastructure - Shopify Agentic Plan integrations, third-party AI shopping apps, embedded retailer assistants - runs predominantly on open-weight models for cost reasons. Echomind Commerce tests your store across a representative sample of model families (Gemini, Llama, Qwen, DeepSeek) so you see how you're represented across your real exposure surface, not just one provider."

This is *more* defensible than testing only ChatGPT. It also flatters Kasparro (who as commerce infrastructure builders know the model landscape is multi-vendor).

### 15.3 Buyer-intent prompt generation

Gemini Flash generates 50-150 buyer prompts per audit, seeded by:
- Product categories from catalog
- MerchantTruth nodes (especially `audience` and `positioning` categories)
- CustomerQuestion nodes
- Common e-commerce intent classes (discover / compare / objection / post-purchase)

Each prompt is a `BuyerPrompt` node, tagged with intent class. This is auditable - judges can see every prompt.

Intent class distribution targets:
- Discover: 40% ("I want a coffee that...")
- Compare: 25% ("Which of your coffees is better for...")
- Objection: 20% ("Is your shipping reliable to Hawaii?")
- Post-purchase: 15% ("How do I store this once opened?")

### 15.4 Agent execution

Each agent gets a uniform system prompt (preserved Echomind discipline - centralized in `prompts.py`):

```
You are an AI shopping assistant. The user is shopping for products.
You have access to the following catalog data from a Shopify store:
{catalog_excerpt - top 30 products by relevance to user's likely category}

You also have access to these store policies: {policies_summary}

When the user asks a question, recommend products from the catalog that fit
their needs, citing your reasoning. If you cannot find a fit, say so honestly.

Output JSON with keys: recommended_products (list of product titles + reasoning),
confidence (0..1), notes.
```

Agents respond. Outputs persisted as `AgentRepresentation` nodes. **No mocking - every response is real and saved verbatim.**

### 15.5 Failure handling (Technical Doc gold)

| Failure | Response |
|---|---|
| OpenRouter rate-limit (free tier) | Exponential backoff, then automatic switch to paid tier (only if user-approved); else partial-run with that column labelled "rate-limited - partial sample" |
| Malformed JSON | Validate against pydantic schema → retry once with stricter prompt → fallback to regex extraction → if still failing, persist as `AgentRepresentation` with `parse_failed=true` and surface in UI |
| Provider unavailable mid-run | Log, continue with remaining providers, mark column "unavailable," recompute readiness score with reduced sample, downgrade calibration confidence |
| Slow response (>30s) | Async per-agent timeout; UI continues showing "still thinking..." dots; if total run exceeds 5 min, fallback to caching but ONLY for that gap, never presented as live |

---

## 16. GAP DETECTION ENGINE

### 16.1 Five gap types

| Type | Detection | Example |
|---|---|---|
| `omission` | Product has MerchantTruth/positioning but no agent ever surfaces it for relevant prompts | Top-3 product never appears for prompts in its own category |
| `contradiction` | MerchantTruth statement contradicts AgentRepresentation claim about same product | "chocolate-forward" vs. "fruity acidic" |
| `ambiguity` | Multiple agents make divergent claims about same product | Llama says "for espresso," Qwen says "for filter only" |
| `hallucination` | Agent claims a product feature/policy not in catalog or policies | "comes with free grinder" - not true |
| `dark_zone` | Entire product subcategory has zero `MENTIONS` from any agent for any relevant prompt | Whole "decaf" line invisible to agents |

### 16.2 Detection pipeline

```
Step 1 (deterministic Cypher): identify candidate gaps via graph predicates per type.
Step 2 (Gemini Pro judge): for each candidate, classify type + severity + reasoning.
Step 3 (revenue model): compute monthly $-at-risk per gap.
Step 4 (calibrator): apply Echomind formula → 5-bucket label.
Step 5 (ranker): sort by gap_priority (§9.2).
Step 6 (entity resolver): merge gaps that target the same underlying entity.
```

Each step's output is a graph mutation, not an in-memory transient - so the audit is fully replayable from Firestore + Neo4j alone.

### 16.3 The "what we don't know" surfaces

Critical: the engine emits gaps with `dont_know` calibration when:
- Buyer prompt sample is too small (<10 prompts in category)
- All 4 agents returned `parse_failed`
- Subgraph for the gap is empty (no MerchantTruth covering it)

These are surfaced in a separate "Needs more data - try a longer interview or broader category sample" panel. **The product visibly refuses to fake numbers.** Demo gold.

---

## 17. FIX → RE-TEST CLOSED LOOP

### 17.1 Fix types

| Type | Generated by | Applied via |
|---|---|---|
| `copy_rewrite` | Gemini Pro using merchant's voice (sampled from interview transcripts) | Shopify `productUpdate` mutation |
| `faq_add` | Gemini Pro from CustomerQuestion + MerchantTruth | Shopify pages or product metafields |
| `policy_clarify` | Gemini Pro from Decision Tree | Shopify policy pages |
| `metafield_add` | Generated structured data (JSON-LD) | Shopify metafields API |
| `structured_data` | Schema.org Product/FAQ JSON-LD | Theme injection (or metafields) |

Each fix carries:
- Proposed text (editable by merchant before apply)
- Predicted delta range (e.g., "expected GPT-class agent surface rate +40 to +65 percentage points, confidence: confident")
- Reasoning trace for the prediction

### 17.2 The closed-loop sequence (real, observable)

```
1. Merchant clicks "Generate fix" on a Gap.
2. Gemini Pro generates proposed text, conditioned on:
     - Gap reasoning trace
     - Subgraph retrieved via 4 strategies (§10)
     - Merchant voice samples (preserves brand tone)
3. UI shows diff: current copy vs. proposed copy.
4. Merchant edits if desired, clicks "Apply."
5. Backend calls Shopify Admin GraphQL mutation. Returns new resource version.
6. Backend triggers retest_orchestrator: re-runs simulator scoped to:
     - Affected products only
     - Buyer prompts that previously surfaced this gap (for valid before/after comparison)
7. Re-test results persist as new AgentRepresentation nodes (versioned).
8. UI renders before/after panel with delta:
     - Surface rate before / after / delta
     - Sentiment shift
     - Calibration of the delta itself
9. Living Update Loop logs the merchant-rated outcome.
```

### 17.3 Demo magic moment guarantee

**The before/after delta is computed from real measurements, not predictions.** If the fix doesn't actually move the needle, that's surfaced too - the system says "applied, but observed delta below predicted range; possible cause: agent caching or prompt drift." This calibrated honesty is the product principle.

---

## 18. REVENUE IMPACT MODEL

### 18.1 The formula

```
monthly_revenue_at_risk(gap) =
    severity (0..1)
  × surface_loss_rate (% of relevant buyer prompts where agents fail to surface)
  × estimated_monthly_agent_traffic (merchant-input or default 100 sessions)
  × baseline_AOV (computed from catalog or merchant-input)
  × baseline_conversion_rate (default 2.5%, adjustable)
```

Every parameter:
- Is exposed in the UI as a slider with default value
- Emits a sensitivity range (low/mid/high estimate), not a point estimate
- Cites its source ("default industry conversion 2.5%, adjustable")

### 18.2 Why this beats a number on a slide

The blueprint's biggest weakness called out in BLUEPRINT_DIGEST.md §16 was "no quantitative validation." We address it by being *transparent about the model rather than confident about the number*. Judges who push will get an answer:

> "We model revenue impact as a parameterized estimate, not a measurement. Every parameter is editable; we emit a range, not a point. The framework reports observed deltas after fix application as ground truth, while predictions are explicitly labelled with calibration confidence. This is how diagnostic tools should report uncertainty."

That answer is more impressive than a fake number.

### 18.3 Aggregate metrics

- **AI Readiness Score** (0-100): weighted sum across categories (catalog clarity, policy completeness, FAQ coverage, trust signal density, edge case handling). Each sub-score is calibrated.
- **Tacit Knowledge Capture**: % of MerchantTruth nodes vs. expected for category. Surfaces "you've captured 67% of your own brain - here's what's still missing."
- **Agent Coverage**: % of buyer prompts where ≥3 of 4 agents surface a relevant product. Measures the merchant's "agent-discoverable surface area."

These three numbers go on the Audit Dashboard, each with a calibration badge.

---

## 19. THE NINE ELEVATION FEATURES

These are what take this from "winning" to "world-class." Every one is grounded in the architecture above; none is decoration.

### 19.1 Multi-agent live disagreement panel
Side-by-side streaming token feeds from all 4 agents during simulation. When agents disagree about your store, the disagreement itself is highlighted (visual diff) and auto-promoted as a `Gap` of type `ambiguity`. The graph grows live with new `AgentRepresentation` nodes. **Visceral demo.**

### 19.2 The Contradiction Cascade view
Full-page graph viz showing ALL `CONTRADICTS` edges in your store: MerchantTruth↔Policy, Policy↔Policy, MerchantTruth↔AgentRepresentation. Reveals systemic issues at a glance. Click any edge → drilldown to the resolution.

### 19.3 Calibrated fix prediction
Before applying a fix, the system predicts the delta with explicit calibration: "I expect this fix to improve GPT-class agent surfacing by 40-65 percentage points (confidence: confident, based on 12 similar gaps observed in [hypothetical] benchmark)." After apply + re-test, observed delta is compared to predicted range - overconfidence is logged and feeds back into calibration tuning.

### 19.4 Tacit Knowledge Score & "What I Didn't Know I Knew" report
End-of-interview summary that surfaces:
- Total MerchantTruths captured
- Distribution by tacit-knowledge category (§7)
- Top 5 nodes the merchant rated as "I didn't realize I knew this" (post-interview review prompt)
- Tacit Knowledge Capture score

Preserves Echomind's original "experts don't know what they know" insight, surfaced explicitly in the merchant's hands.

### 19.5 Decision Tree Vault
For every policy decision (returns, shipping, exchanges, refunds, escalation), render the merchant's tacit decision tree from interview as an interactive flowchart. Each leaf is testable: send the leaf's edge case as a buyer prompt to all 4 agents and check whether any agent's answer matches the leaf. Per-agent compliance score per leaf. **Nobody else will have this.**

### 19.6 The Replay Theater (`/replay/[auditId]`)
Time-scrubbing UI that replays the entire audit timeline:
- Each interview question being asked
- Each MerchantTruth node being added (graph animates)
- Each agent simulation call firing
- Each gap appearing
- Each fix applied
- Each re-test result

Judges can scrub to any moment and see exactly what happened. **This is the strongest possible "everything is real" receipt** - the timeline is reconstructed from Firestore changelog + Neo4j snapshots, not staged.

### 19.7 Adversarial Buyer Mode
Optional simulator mode where Gemini plays a frustrated/skeptical/confused buyer asking gotcha questions ("Why is your coffee 3× more expensive than Walmart's?", "Will this actually arrive before Christmas?"). Tests how agents handle pressure and surface trust signals. Reveals trust gaps no normal buyer would surface.

### 19.8 Multilingual Agent Simulation (stretch)
Re-run simulation in Hindi / Spanish / Mandarin (just adds prompt layer). Reveals that your AI representation collapses for non-English buyers - a major undocumented gap. Big differentiator if Day 9 has slack.

### 19.9 The PDF Audit Report
One-click branded PDF export of the full audit: AI Readiness Score, top 10 gaps with reasoning chains, before/after deltas for applied fixes, tacit knowledge taxonomy report, recommended next actions. Rendered server-side with Puppeteer. Merchant can send it to their team. Becomes the artifact-out-of-the-product that drives retention.

---

## 20. UI / UX - ALL FIVE VIEWS

Visual identity: dark mode default, monospace accents on technical metadata, large readable type for merchant-facing content, calibration badges color-coded everywhere (green/yellow/orange/red/grey-stripe).

### 20.1 `/onboard` - Shopify connection wizard
- Step 1: Sign in with Google.
- Step 2: Connect Shopify (real OAuth → callback → token stored in Firebase).
- Step 3: Live ingest counter ("12 / 42 products... 28 / 42... done · 7 policies · 18 reviews").
- Step 4: "Ready to start your AI Readiness Audit. Estimated 25 min: 20 min interview + 5 min agent simulation."

### 20.2 `/interview/[id]` - three-column live interview (preserved Echomind UX)

| Column | Width | Contents |
|---|---|---|
| Left | 30% | Live transcript (interim italic, final solid). Speaker labels. Extracted-as-node phrases highlighted, clickable → graph view. Auto-scroll with manual lock. |
| Center | 40% | Current question (large readable type). 5-segment phase indicator. Elapsed timer + phase timer. Audio controls (mute, volume meter, voice-activity LED, text fallback input). Skip button. |
| Right | 30% | Mini graph preview (force-directed). New nodes pulse in. Color by type (per palette below). Live counter: "Nodes: 287 · Edges: 612 · Coverage: 71%". Phase progress bar. |

**Color palette (preserved from Echomind):**
- Product: `#3B82F6` blue
- Policy: `#F59E0B` amber
- TrustSignal: `#10B981` green
- MerchantTruth: `#8B5CF6` purple
- Decision: `#F43F5E` rose
- Pattern: `#06B6D4` cyan
- CustomerQuestion: `#EAB308` yellow
- AgentRepresentation: `#EC4899` pink
- Gap: `#EF4444` red
- FixSuggestion: `#22C55E` bright green

### 20.3 `/audit/[storeId]` - main dashboard
- **Top strip**: AI Readiness Score (0-100, calibrated), Tacit Knowledge Capture %, Agent Coverage %, last audit timestamp.
- **Center**: ranked gap list. Each card shows: type badge, severity bar, $-at-risk, calibration badge, affected products count, "Generate fix" button. Sortable by revenue / confidence / severity.
- **Right rail**: AI Readiness Radar (recharts) - 5 axes: catalog clarity, policy completeness, FAQ coverage, trust signals, edge cases.
- **Bottom**: Coverage heatmap (treemap colored green / yellow / red) - which product categories are well-represented vs. dark zones.

### 20.4 `/simulate/[runId]` - agent comparison
- 4 columns, one per agent.
- Each column: model name, response count, surface rate, average sentiment, sample of recent verbatim responses.
- Streaming token feed during live runs.
- Filter by buyer-prompt intent class (discover / compare / objection / post-purchase).
- Click any response → see the BuyerPrompt + which products were surfaced + which were NOT.

### 20.5 `/diff/[gapId]` - gap deep dive
- **Left**: agent's verbatim misreading (or missing mention).
- **Right**: merchant's stated MerchantTruth + supporting interview transcript snippet + relevant Policy nodes.
- **Below**: reasoning chain accordion. Each step links to source nodes (jump to graph).
- **Below that**: revenue impact panel with editable parameters + sensitivity range.
- **Bottom**: FixSuggestion card with proposed copy, predicted delta range (calibrated), edit + apply buttons.
- **Right rail (after fix applied)**: before/after panel with measured delta.

### 20.6 `/graph/[storeId]` - full graph viz
- Force-directed graph (react-force-graph-2d), all node types.
- Node size ∝ centrality, opacity ∝ confidence, edge thickness ∝ weight, color by type.
- Sidebar filters: type, min confidence, phase, name search, tacit-knowledge category.
- Click node → detail panel: full props, all incoming/outgoing edges, contradictions flagged.

### 20.7 `/policies/[type]` - Decision Tree visualizer (§19.5)
- Flowchart rendered from Decision node tree.
- Each leaf shows per-agent compliance score (which agents would correctly answer this edge case).
- "Test this leaf" button → sends edge-case prompt to live simulator.

### 20.8 `/replay/[auditId]` - Replay Theater (§19.6)
- Horizontal timeline at bottom, scrubbable.
- Top half: current state of all 5 views at the timestamp.
- "Play" button auto-advances at 4× real time.
- Every event has a tooltip with metadata.

---

## 21. THE FIVE-MINUTE DEMO (all live, all real)

Single take. Network tab visible at start. No edits hiding failures.

### 0:00 - 0:25 · The hook
Voice over Kasparro's own framing on screen: "ChatGPT is completing purchases. Google AI Mode is recommending products. Shopify just launched its Agentic Plan. AI agents are about to mediate every shopping decision - and right now, your merchants don't know how those agents see them."

### 0:25 - 0:55 · Connect (real Shopify OAuth)
Sign in with Google. Click "Connect Shopify Store." Browser redirects to real partners.shopify.com OAuth. Approve. Live counter ticks: "Ingesting Fulcrum Coffee Co... 42 products · 7 policies · 64 reviews." Mention: "This is the real Admin GraphQL API. Network tab open if you want to verify."

### 0:55 - 2:00 · The interview (live, voice, graph grows)
Open `/interview`. Click Start. Mic permission. Real Google STT V2 streams interim transcripts on the left. The system asks an unscripted phase-3 question pulled from frontier scoring: *"Customers buying your Yirgacheffe - what's the question they ask in DMs that's never made it to your FAQ?"* You answer with a tacit truth ("they always ask if it's good for cold brew, and it isn't, but the FAQ doesn't say so"). On the right, three new nodes pulse in live: a `CustomerQuestion`, a `MerchantTruth`, an `EXCEPTION_TO` edge to the brewing recommendation. Counter ticks: "Nodes: 287 · Edges: 612."

### 2:00 - 3:00 · The agent swarm (live, 4 columns, streaming)
Click "Run Agent Simulation." `/simulate` opens. Four columns appear: Gemini, Llama-3.3, Qwen-2.5, DeepSeek V3. Buyer-intent prompts fan out, 50 per agent. Streaming tokens scroll in each column live. Per-agent counter: "23/50 · 41/50 · 50/50 done." Voiceover: "Real OpenRouter calls. Real Gemini calls. Nothing cached."

### 3:00 - 4:00 · The diagnosis (calibrated, ranked, brutal)
Auto-jump to `/audit`. Top gap card:

> **CONTRADICTION · severity 0.83 · $1,840/mo at risk · calibration: confident**
> *Three agents represent your Yirgacheffe as "fruity, acidic." Your interview said your positioning is "chocolate-forward." Likely cause: product description missing the words "chocolate," "low acidity," "Bourbon varietal."*

Click → `/diff/[gapId]`. Reasoning chain expands. Source nodes clickable (jump to graph). Voiceover: "This is the audit trail. Every claim links back to either an agent response or a MerchantTruth from the interview. No black box."

Scroll the gap list. Show one card with **"calibration: I don't know - only 2 buyer prompts in this category, can't estimate revenue impact reliably."** Voiceover: *"The product refuses to fake numbers it doesn't have. That's the difference between a diagnostic and a marketing tool."*

### 4:00 - 4:40 · The fix → re-test (real Shopify mutation)
Click "Generate fix." Gemini Pro proposes new product copy on screen, in Fulcrum Coffee's voice. Click "Apply." UI shows: "Pushing to Shopify..." Mutation succeeds. Open the live dev store in another tab - show the product page changed. Click "Re-test." Spinner. ~60 seconds (we don't cut). Before/after panel opens:

> **GPT-class agents now surface this product 71% of the time, up from 12%. Observed monthly recovery: $1,840 (matches predicted range). Calibration: confident.**

### 4:40 - 5:00 · The close
Voiceover: *"Echomind Commerce. Built on a typed knowledge graph and calibrated confidence engine. The only AI-readiness tool that captures merchant tacit knowledge as ground truth - and the only one that knows what it doesn't know. Track 5. End to end. Live."*

---

## 22. DAY-BY-DAY BUILD PLAN

### Pre-build: 1-4 May 2026

| Date | Task |
|---|---|
| **1 May (today)** | Read this plan. Confirm pivot ✅. Start Shopify Partner account (free). Procure all API keys: Gemini direct (free tier), OpenRouter (existing key), Firebase project, Neo4j AuraDB Free, Google Cloud STT (free tier 60 min/mo). Stand up empty GitHub repo `echomind-commerce`. |
| **2 May** | Create Fulcrum Coffee Co. dev store (or rename - see §29). Populate 42 SKUs of believable specialty coffee products with intentional gaps (descriptions weak on grind size, FAQ missing brew guidance, one policy contradiction baked in for demo gold). Write 7 store policies, 60+ reviews. |
| **3 May** | Register for hackathon (https://forms.gle/dG64ot2vizEqETcA6). Track 5. Decide solo vs. duo. Lock brand identity. Initial idea line pre-written: *"AI Representation Optimizer that interviews merchants, simulates 4 real AI agents (Gemini, Llama, Qwen, DeepSeek), diagnoses gaps with calibrated confidence, applies fixes via Shopify Admin API, and re-tests live to prove deltas."* |
| **4 May** | Last call for registration. All API keys verified working with hello-world calls. Initial Docker compose drafted. Repo skeleton committed. |

### Build window: 10-20 May 2026

#### Day 1 (Sat 10 May) - Foundation + docs-first moat
- 09:00-11:00: First commits to public GitHub. README v0.1 with problem statement.
- 11:00-14:00: **Product Doc v0.1** (≤3 pages, sharp, every section per §27).
- 14:00-17:00: **Technical Doc v0.1** (architecture diagram, AI/det boundary, 5 named failure modes).
- 17:00-19:00: **Decision Log v0.1** with 15 entries (per §26). Commit each entry as a separate commit (provable thinking history).
- 19:00-22:00: Docker compose: Next.js + FastAPI + Neo4j + Firebase emulator. Health-check route. Each service pings each other. Commit `feat: services boot end-to-end`.
- **End of day**: ≥10 atomic commits. **Mandatory documentation gate cleared on Day 1.**

#### Day 2 (Sun 11 May) - Shopify integration (real, no mocks)
- Shopify OAuth flow (real partners.shopify.com).
- Admin GraphQL crawler → Firestore.
- Neo4j writer turning Shopify data into `Product`, `Policy`, `TrustSignal` nodes.
- `/onboard` page with live counter.
- **Acceptance**: clone repo on a fresh machine, docker compose up, sign in, click connect, see real product count. If it works on a fresh machine, it's real.

#### Day 3 (Mon 12 May) - Socratic engine + extraction
- Port `core/socratic` skeleton from blueprint.
- 5 commerce phases in `prompts.py` (§8).
- Gemini Flash typed extraction (pydantic schemas for MerchantTruth, CustomerQuestion, Policy, Decision, Pattern).
- Phase manager + frontier scorer + redundancy checker.
- Text-mode interview loop (no audio yet).
- **Acceptance**: text interview yourself for 10 min produces ≥40 nodes, ≥60 edges, advances at least one phase.

#### Day 4 (Tue 13 May) - STT + interview UI
- Google STT V2 streaming integration.
- WebSocket route for audio chunks.
- 3-column `/interview/[id]` view (transcript / question / live graph).
- Mini graph component (react-force-graph-2d).
- Phase indicator (5 segments).
- Skip button + text fallback.
- **Acceptance**: 10-minute audio interview works, graph grows live, no mocks.

#### Day 5 (Wed 14 May) - Agent swarm (the unique-to-us thing)
- `core/agents/openrouter.py` (one OpenAI-compatible client, model param switches between Llama/Qwen/DeepSeek/Gemini).
- `core/agents/gemini_agent.py` (direct Gemini path).
- Buyer-intent prompt generator (Gemini Flash).
- Agent runner with concurrency, retries, JSON validation, schema fallback.
- `/simulate/[runId]` 4-column view with streaming.
- Persistence: `BuyerPrompt`, `AgentRepresentation` nodes in Neo4j; raw run data in Firestore.
- **Acceptance**: 50 prompts × 4 agents → 200 AgentRepresentation nodes in Neo4j Browser, all real responses, no caching, run completes <5 min.

#### Day 6 (Thu 15 May) - Gap detector + revenue model + judge
- `core/diagnose/cypher_diff.py` for the 5 gap types (§16).
- `core/diagnose/judge.py` Gemini Pro classifier with rubric in `prompts.py`.
- `core/diagnose/calibrator.py` (Echomind formula).
- `core/diagnose/revenue_model.py`.
- `core/diagnose/ranker.py`.
- Entity resolver (§13).
- **Acceptance**: ≥15 ranked Gap nodes, at least 2 each of `omission` / `contradiction` / `dark_zone`, at least one `dont_know` calibration.

#### Day 7 (Fri 16 May) - Diagnosis UI + reasoning trace
- `/audit/[storeId]` dashboard.
- `/diff/[gapId]` deep-dive.
- AI Readiness Radar (recharts).
- Coverage heatmap (treemap).
- Reasoning trace accordion (per §11 spec).
- Calibration badges everywhere.
- **Acceptance**: judge could navigate store → audit → top gap → reasoning chain → source node in graph, in 4 clicks.

#### Day 8 (Sat 17 May) - Fix gen + Shopify writer + re-test
- `core/fix/copy_generator.py` with merchant voice samples.
- `core/fix/policy_clarifier.py` from Decision Trees.
- `core/fix/shopify_writer.py` real Admin GraphQL mutations.
- Approval UI in `/diff/[gapId]`.
- Retest orchestrator (scoped re-run).
- Before/after delta computation + viz.
- **Acceptance**: 3 different gaps go through full loop end-to-end, with verified Shopify product page changes and non-trivial measured deltas.

#### Day 9 (Sun 18 May) - Hardening + elevation features
- Failure handling for ≥5 modes (kill components on purpose, document recovery).
- Living Update Loop (§12) wired in `/audit`.
- Decision Tree Vault (§19.5) at `/policies/[type]`.
- Replay Theater (§19.6) at `/replay/[id]`.
- Adversarial Buyer Mode toggle (§19.7).
- **Cut list** if behind: skip multilingual (§19.8), skip PDF export (§19.9), skip Replay Theater. Core loop must be bulletproof first.

#### Day 10 (Mon 19 May) - Docs final + demo recording
- Final pass on Product Doc, Technical Doc, Decision Log, Contribution Note, README.
- Record demo video (4-5 min, single take). If first take fails - re-record clean. **No edits hiding failures.**
- Upload to YouTube unlisted. Add link to README.
- README setup instructions tested on a fresh machine (live).

#### Day 11 (Tue 20 May) - Submission day with margin
- 09:00: dry-run full setup on a fresh machine using only README.
- 10:00-14:00: fix any gaps found.
- 14:00: final commit, tag `v1.0-submission`, push.
- 16:00: submit via https://forms.gle/sYaqxeyBAajNPV9t7. **Submit at 18:00 IST, not 23:59. Assume the form crashes at the deadline.**
- 18:30: post-submission note in WhatsApp group.
- 19:00-23:59: nothing. The clock is your enemy after submission.

### Commit cadence target
- ≥45 atomic commits over 11 days.
- Each commit message explains *why*, not just *what* ("add merchant-voice sampler so fix copy preserves brand tone" not "add file").
- Day 1 commits include 5 doc commits (one per major section) - proves docs-first discipline.

---

## 23. API STRATEGY - GEMINI + OPENROUTER ONLY

### 23.1 Provider matrix (all real, all free where stated)

| Service | Provider | Tier | Daily limit | Used for |
|---|---|---|---|---|
| Gemini Flash | Direct Gemini API | Free | 1.5M tokens/day | Extraction, question gen, buyer prompt gen, fix copy gen |
| Gemini Pro / Experimental | Direct Gemini API | Free | 50 RPM, 32K TPM | Twin reasoning, gap judge, contradiction resolver |
| text-embedding-004 | Direct Gemini API | Free | Generous | Entity resolution, semantic redundancy |
| Google STT V2 | Google Cloud | Free | 60 min/month streaming | Interview transcription |
| OpenRouter Llama-3.3-70B | OpenRouter | `:free` | varies (rate-limited) | Agent swarm slot 2 |
| OpenRouter Qwen-2.5-72B | OpenRouter | `:free` | varies | Agent swarm slot 3 |
| OpenRouter DeepSeek V3 | OpenRouter | `:free` | varies | Agent swarm slot 4 |
| OpenRouter Gemini 2.0 Flash | OpenRouter | `:free` | varies | Agent swarm slot 1 (or use direct Gemini) |
| Shopify Dev Store | Shopify | Free | Unlimited | Real merchant data infra |
| Neo4j AuraDB | Neo4j | Free | 50K nodes / 175K edges | Graph DB |
| Firebase | Google | Spark plan | Generous | Auth, Firestore, Storage |

### 23.2 Free-tier resilience pattern

Every LLM call goes through `services/llm_service.py` which:
1. Tries the primary provider for that call type.
2. On rate-limit or failure, automatically falls back to OpenRouter equivalent.
3. Logs every fallback (so we can document which providers held up under load).
4. If all providers fail for a call, returns a `parse_failed` result that the calling code handles gracefully - never crashes.

### 23.3 Honest narrative for the demo
"Echomind Commerce runs entirely on free-tier infrastructure for the hackathon - direct Gemini API for our own reasoning layer, OpenRouter free-tier models (Llama, Qwen, DeepSeek) for the agent swarm. This is by design: AI commerce infrastructure must be cost-efficient at scale, and a tool merchants can't afford to run is no tool at all. At production volume, we'd add paid OpenAI/Anthropic models to the swarm for fuller coverage at ~$5-8/audit total cost."

This frame *flatters* Kasparro's commerce-infrastructure thesis (cost matters) and is true.

---

## 24. SUBMISSION CHECKLIST

| Item | Status |
|---|---|
| [ ] Public GitHub repo `echomind-commerce` | |
| [ ] Product Document (≤3 pages, sharp, root of repo) | Day 1 |
| [ ] Technical Document (full, root of repo) | Day 1 |
| [ ] README with project name, problem statement, setup instructions, demo video link | Day 1 + Day 10 |
| [ ] Demo video 3-5 min narrated, unlisted YouTube, link in README | Day 10 |
| [ ] Screenshots / walkthrough in `/docs/screenshots` | Day 10 |
| [ ] Contribution note (even solo: how time was split product vs. engineering) | Day 11 |
| [ ] Decision Log in repo, ≥20 entries | Day 1+ |
| [ ] Atomic commit history ≥45 commits, all meaningful messages | Throughout |
| [ ] All API keys via env vars, `.env.example` checked in, real `.env` gitignored | Day 1 |
| [ ] No hardcoded data, no mocks; everything wired to live services | Throughout |
| [ ] Submission form completed by 18:00 IST 20 May 2026 | Day 11 |

If any mandatory item is incomplete: **hard reject** per rules ("Submissions without both documents will not be evaluated, regardless of code quality").

---

## 25. RISK REGISTER

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Shopify OAuth flow breaks on demo day | M | H | Pre-record OAuth-completed state as fallback; live OAuth as primary. Network outage tested in dev. |
| 2 | OpenRouter free-tier rate-limited mid-demo | H | M | Concurrency limits + exponential backoff; if hit during demo, narrate honestly: "free tier rate-limited mid-run, partial sample shown - this is real-world infra reality." |
| 3 | Gemini returns malformed JSON | M | M | JSON-mode + schema validation + retry once + low-confidence fallback node. Failure mode #1 in Tech Doc. |
| 4 | Neo4j AuraDB free tier hits cap during dev iteration | L | M | Periodic cleanup query; one audit < 1.5K nodes (5% of cap). |
| 5 | Solo bandwidth fails 11-day window | M | H | Day 1 docs-first means even 70%-built product passes the documentation gate. Day 9 is buffer. Cut elevation features (§19) before cutting docs or core loop. |
| 6 | Confused as "ChatGPT wrapper" | L | H | Lead Tech Doc with typed-graph + calibrated-twin angle. Show Cypher diff queries verbatim. Reasoning trace UI is the proof. |
| 7 | Track 5 difficulty + smaller field = pressure to finish | M | M | Per rules: highest internship signal. Better strong Track 5 finalist than mid-pack Track 1 entry. |
| 8 | Live Shopify mutation corrupts dev store mid-demo | L | M | Snapshot dev store before demo; revert script ready; mutations recorded so any "after" state is reversible. |
| 9 | Internet drops during demo recording | M | M | Wired connection. Day 10 has slack to re-record. Local replay theater works offline if needed. |
| 10 | "10,000 questions" framing called hype | L | M | Provide honest accounting (§8.3): ~5,000-8,000 LLM-mediated micro-questions per audit, defensible. |
| 11 | Calibration claim "80% confidence ≈ 80% accuracy" challenged | M | M | Don't claim it. Claim the calibration *labels* (the 5 buckets), not the numerical equivalence. Honest about limitations. |
| 12 | Demo "aha moment" depends on staged contradiction | M | H | The contradiction is real (you'll bake it into Fulcrum Coffee's product copy in pre-build). Multiple gaps - if one is unimpressive, show another. |
| 13 | Privacy / IP / liability unaddressed | L | M | Add §11 to Product Doc: "graph + transcripts owned by merchant, deletable on demand, our role is processor, no posthumous querying without consent flag." Cheap insurance against judge poke. |
| 14 | Multiple provider outages on demo day | L | H | Pre-recorded backup demo video. Submit primary live recording; have backup uploaded as unlisted secondary in README "in case of provider outage on viewing day." |
| 15 | Scope creep into elevation features before core loop is solid | H | H | Hard rule: §19 features only after Day 8 acceptance test passes. Discipline matters more than ambition. |

---

## 26. DECISION LOG SEED - first 15 entries (commit Day 1, one per commit)

1. **Track 5 (AI Representation Optimizer).** Considered Tracks 1-4. Chose 5 because rules state highest internship signal, lower competition (labelled "Advanced"), closest to Kasparro's day job. Tradeoff: harder problem.
2. **Pivot from Echomind Expert-Twin to Echomind Commerce.** Considered submitting Echomind unchanged. Chose pivot because original product scores ~0/15 on Business Relevance for this hackathon. Preserve technical thesis (typed graph + calibrated twin), repoint at merchant AI readiness.
3. **Multi-agent swarm across 4 model families (Gemini, Llama, Qwen, DeepSeek).** Considered single-LLM simulator (cheaper). Chose 4 because the unique product insight is *comparison* - you cannot tell a merchant "AI agents misrepresent you" using one agent.
4. **OpenRouter free-tier-only for swarm; no paid OpenAI/Anthropic.** Considered paying for GPT-4 / Claude. Chose free tier because (a) user budget constraint, (b) more representative of real 2026 agent infrastructure (most agentic shopping is open-weight under the hood), (c) keeps cost-to-merchant story compelling.
5. **Neo4j AuraDB Free over Postgres + pgvector.** Cypher gap-detection queries are 3 lines vs. 30 in SQL. Graph algebra is the right primitive for our diagnostic substrate.
6. **Gemini Flash for extraction + question gen, Gemini Pro for judge + twin.** Flash is 10× cheaper, native JSON mode, 3× faster. Pro for the calls where reasoning depth matters.
7. **Calibrated "I don't know" applied to gap diagnoses, not just twin answers.** Considered always emitting numbers. Chose calibration because diagnostic tools that overclaim are useless to merchants. This is also our Originality differentiator.
8. **15-25 minute interview, not Echomind's 2 hours.** No merchant in production sits 2 hours. Demo videos are 5 min. Realistic > impressive.
9. **Local Docker compose for hackathon, Cloud Run as v2 stretch.** Demo runs on laptop. Judges replicate locally via README. Cloud deployment is unnecessary risk we're not taking.
10. **Documentation-first Day 1, code Day 2+.** Mandatory documentation gate is hard reject. Cheapest moat. Plus docs catch architecture problems before code commits to them.
11. **Synthetic but believable Fulcrum Coffee Co. catalog over real merchant.** Rules permit synthetic. Faster iteration. Real merchant outreach is deferred stretch (user constraint).
12. **Specialty coffee over running shoes for demo.** Coffee has richer tacit knowledge surface (origin, processing, varietal, brew guidance) and more visceral AI misrepresentation moments (tasting notes get mangled by LLMs). Shoes is v2 vertical.
13. **5 gap types (omission, contradiction, ambiguity, hallucination, dark_zone).** Considered 3 (just the obvious ones). Chose 5 because each maps to a different fix type and a different agent failure mode - gives the diagnostic real teeth.
14. **`prompts.py` centralized, never inline.** Preserved verbatim from Echomind blueprint. "60% of debugging is prompt tuning" remains true; centralization compounds across the build.
15. **Real Shopify Admin GraphQL mutations during demo, not staged.** Considered showing diffs without applying. Chose live mutations because the closed-loop fix → re-test is the demo's load-bearing magic. Reversal script ready as safety net.

(Day 2+: add ~1 entry per day for major decisions. Target ≥20 entries by submission.)

---

## 27. PRODUCT DOC SKELETON (target ≤3 pages)

### Problem
Shopify merchants are increasingly discovered, evaluated, and recommended by AI shopping agents - ChatGPT's purchase flow, Google AI Mode, Shopify's own Agentic Plan, and a growing long tail of third-party agents running on open-weight models. When agents misread a merchant's catalog (because product copy is ambiguous, FAQs are missing, policies contradict, or tacit selling points were never written down), the merchant is either skipped or misrepresented. Today, merchants have no way to *see* how AI agents see them, and no closed-loop way to fix it.

### Target user
Shopify merchants in the $100K-$5M annual revenue range - typically 1-10 person teams, with a domain expert (the founder or merchandiser) but no in-house AI engineering. Their tacit knowledge is the brand's biggest undocumented asset. Their AI representation is the leak nobody is monitoring.

### Core user journey
Connect Shopify (5 min) → 20-minute Socratic interview captures tacit knowledge → multi-agent simulator runs 50-150 buyer-intent prompts across 4 real LLMs → ranked, calibrated gap list with revenue impact and reasoning trace → one-click fix generation in merchant voice → push to Shopify Admin API → re-test live → measured before/after delta.

### Key product decisions
1. **Multi-agent simulation, not single-agent.** Comparison is the insight. (DL #3)
2. **Calibrated "I don't know" everywhere.** Diagnostic tools that overclaim are useless. (DL #7)
3. **Tacit knowledge as ground truth.** No other AI-readiness tool has this. The Socratic interview captures the merchant's brain; that's the diagnostic substrate other tools structurally cannot access. (DL #2, §7)
4. **Closed loop fix → re-test.** Lists of problems aren't products; deltas are.
5. **Free-tier-first architecture.** Cost-efficient at scale; honest about provider mix. (DL #4)

### Scope cuts (we did NOT build)
- Cross-merchant benchmarking dashboards
- Persistent monitoring / drift alerting (one-shot audit only)
- Multi-store accounts
- Shopify App Store distribution wrapper
- Voice cloning for TTS persona
- Auto-fix without merchant approval

Why: 11 days, solo (or small team). Closing one loop end-to-end beats five half-loops. Production-readiness is for v2.

### Tradeoffs
- **Realism vs. demo time.** Real LLM calls take 60-90s for a sim run. We embrace the wait - the visible network activity IS the credibility signal.
- **Calibrated honesty vs. impressive numbers.** Showing "I don't know" deflates some demo moments but is the product's whole differentiator.
- **Solo bandwidth vs. quality.** Cut multi-store, alerting, SSO before docs or failure handling.

(Full doc fleshes each above into 2-3 paragraphs. Stays ≤3 pages.)

---

## 28. TECHNICAL DOC SKELETON

### System architecture
See §5.1 diagram. Five Cloud Run-ready services collapsed to one local FastAPI process for hackathon. Real Shopify Admin GraphQL, real Neo4j AuraDB, real Firebase, real direct Gemini API, real OpenRouter calls.

### AI vs deterministic boundary
See §5.4 table. Rule: ground-truth-or-determinism = code; natural-language-understanding = LLM. We do not ask LLMs to do math, and we do not ask Cypher to read prose.

### Five named failure modes

1. **LLM returns malformed JSON.** pydantic schema validation → retry once with stricter prompt → fallback to `parse_failed` node with low confidence. UI shows yellow "extraction needs review" banner.
2. **Shopify Admin API down.** Crawl pauses; existing graph remains queryable; UI shows "merchant data is N hours stale, fixes can't be applied until reconnect." Re-test panel disabled with explanatory tooltip.
3. **Agent simulator rate-limited (free tier).** Concurrency-limited queue retries with exponential backoff; if one provider stays down, simulation completes with the others and clearly labels the failed column "rate-limited - partial run." Calibration confidence on gap detection auto-downgrades.
4. **Neo4j Bolt connection timeout.** Operations are batched and retried with idempotency keys (every node has a deterministic ID derived from content hash, so re-write is safe). Circuit breaker after 3 failures escalates to UI banner.
5. **STT misheard transcript.** Transcript pane is editable post-interview; word time offsets allow fine-grained correction. If STT confidence per word < 0.5, word renders italic and re-extraction is flagged for that segment.

### Known limitations
- Single-merchant scope (no cross-merchant benchmarking).
- Buyer prompts are LLM-generated, not from real shopper logs (a prod system would use Shopify session search-query data).
- Revenue model is parameterized estimate, not measured uplift; ranges shown not point estimates.
- One-shot audit, not persistent monitoring.
- Free-tier model swarm; production would add paid GPT/Claude for fuller coverage.

### What we'd improve with more time
- Connect to merchant's real shopper search logs to seed buyer prompts.
- Cross-merchant cohort benchmarking ("you score 67/100 vs category median 73/100").
- Shopify App Store wrapper for one-click distribution.
- Persistent monitoring with drift alerts.
- Voice cloning for the merchant's brand voice in fix copy generation.
- Multilingual agent simulation across major non-English buyer languages.

---

## 29. BRAND IDENTITY - FULCRUM COFFEE CO.

### Positioning
Specialty single-origin coffee for the home-brewing enthusiast. Values: traceability, transparency, slow-roasted, brewing guidance over hype.

### Catalog (42 SKUs to build out, 2 May)
- 12 single-origins (Ethiopia, Kenya, Colombia, Guatemala, Brazil, Indonesia, Costa Rica, Rwanda, Honduras, Peru, Mexico, Yemen - 1 each)
- 4 blends (Morning, Espresso, Decaf, Cold Brew Specific)
- 6 brewing accessories (V60 dripper, Chemex, Aeropress, French Press, scale, gooseneck kettle)
- 6 subscription tiers (250g monthly / weekly × 3 frequencies)
- 8 gift items (sampler boxes, gift cards, branded mugs, beans + book combos)
- 6 limited editions (rotating)

### Intentional gaps to bake in (so demo finds real misrepresentation)
1. **Yirgacheffe description omits "chocolate-forward"** (we positioned it that way in our merchant brain, but the page says "fruity floral profile" - agents will pick up on description, not intent). → **Demo's headline contradiction gap.**
2. **Cold brew section nowhere mentions which beans are best for cold brew.** → `dark_zone` gap.
3. **Return policy is one paragraph, doesn't address opened bag returns.** → Decision Tree edge case agents will fail.
4. **Two policy contradictions baked in**: shipping page says "free over $40," footer says "free over $50." → `CONTRADICTS` edge.
5. **No FAQ entries on grind size guidance.** → `omission` gap.
6. **"Decaf" line has zero MerchantTruths because we'll skip phase 2 questions about it during the demo interview.** → reveals dark_zone gap that the merchant didn't realize they had.

These six gaps are *real* once baked in. The demo doesn't fake them; it discovers them. **Critical**: the merchant (you) does NOT pre-script which gap is the headline. Let the system surface what it surfaces. The bake-in is just to ensure there's enough surface for it to find.

### Brand voice
Patient, generous, slightly nerdy, anti-hype. "We don't tell you what to taste; we tell you why this bean tastes the way it does." This voice gets sampled from interview transcripts and used by Gemini Pro when generating fix copy - preserves brand tone across automated fixes.

---

## 30. STRETCH / UNDENIABLE MOVES (Day 9 if slack)

In priority order. **Do not pursue until Day 8 acceptance test passes.**

1. **Multilingual agent simulation** (§19.8) - re-run swarm in Hindi, Spanish, Mandarin. Reveals international AI representation collapse. Strongest single differentiator if completed.
2. **PDF Audit Report export** (§19.9) - branded one-click report. Drives retention.
3. **Cohort benchmark stub** - even 3 dev stores you build give "you: 67. Cohort median: 73." Visceral.
4. **Cloud Run public deploy** - judges can self-serve onboard their own dev store. Requires DNS + IAM but doable in 4 hours if smooth.
5. **A/B fix mode** - apply fix to a duplicated product variant (shadow), re-test, only commit if delta > threshold. Demonstrates safety-first product instinct.
6. **Scheduled re-audit cron** - set up a weekly auto-audit job. Just a tiny Cloud Scheduler entry; 30-min build; turns one-shot into product.

### Cut order if behind on Day 8
1. Cut: Adversarial Buyer Mode (§19.7).
2. Cut: Replay Theater (§19.6).
3. Cut: Decision Tree Vault (§19.5).
4. NEVER cut: documentation, core loop, calibration, reasoning trace, before/after delta.

---

## 31. OPEN QUESTIONS

Lock answers before 3 May:

1. ✅ **Pivot confirmed** - Echomind Commerce. (Locked 2026-05-01.)
2. ✅ **Brand identity** - Fulcrum Coffee Co. (Locked. Rename if you want.)
3. ⏳ **Solo or duo?** Cross-discipline duo is allowed, rules favor it. If you have an MBA / marketing-minded friend, recruiting them for product framing + interview role-play strengthens submission. Decide by 4 May.
4. ✅ **API budget: zero paid OpenAI/Anthropic.** Free tier only for hackathon. (Locked.)
5. ⏳ **Real merchant outreach** - deferred to last. Build everything else first; reach out to one real Shopify SMB merchant ONLY if Day 9 has slack and pre-built product is bulletproof.
6. ⏳ **Demo store name** - keep "Fulcrum Coffee Co." or rename? (Pick by 2 May.)

---

## 32. THE ELEVATOR PITCH (carry in your head)

> ECHOMIND COMMERCE is an AI Representation Optimizer for Shopify merchants. It interviews the merchant for 20 minutes (Socratic, AI-driven, captures tacit knowledge as a typed graph), simulates 50-150 buyer queries against four real AI shopping agents (Gemini, Llama, Qwen, DeepSeek), diffs the agents' actual representation against the merchant's intended representation, and produces a calibrated, revenue-ranked gap list with one-click fixes that push to Shopify and re-test the agents to prove the delta. It's the only AI-readiness tool where the diagnostic ground truth comes from the merchant's brain rather than from documents the merchant already failed to write - and the only one that knows what it doesn't know. Built on the Echomind technical thesis (typed graph + calibrated twin + reasoning trace + contradiction primitive + decision tree builder + frontier scoring + entity resolution + living update loop) but pointed at the exact problem Kasparro builds infrastructure for. Free-tier-first architecture. Real Shopify, real Neo4j, real LLMs, real merchant, real fixes, real measured deltas. End to end. Live.

---

*End of WINNING_PLAN.md. Source of truth from now on. ECHOMIND_BLUEPRINT.md is ancestral. RULES.md and BLUEPRINT_DIGEST.md are reference. Build starts 10 May. Ship by 18:00 IST 20 May 2026.*
