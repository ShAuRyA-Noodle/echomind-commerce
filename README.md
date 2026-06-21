<div align="center">

# Echomind Commerce

### See your Shopify store through every AI agent's eyes. Fix what they misread.

Echomind Commerce interviews a merchant for tacit knowledge no document holds, simulates how four real AI shopping agents represent the store, diagnoses gaps with calibrated confidence, applies fixes via the Shopify Admin API, and re-tests live to prove the delta.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Neo4j](https://img.shields.io/badge/neo4j-AuraDB-008CC1.svg)](https://neo4j.com/cloud/aura/)
[![Gemini](https://img.shields.io/badge/gemini-2.5-4285F4.svg)](https://aistudio.google.com/)
[![OpenRouter](https://img.shields.io/badge/openrouter-free%20tier-6750A4.svg)](https://openrouter.ai/)
[![CI](https://github.com/ShAuRyA-Noodle/echomind-commerce/actions/workflows/ci.yml/badge.svg)](https://github.com/ShAuRyA-Noodle/echomind-commerce/actions)

[Quick start](#quick-start) · [Walkthrough](#walkthrough) · [Architecture](#architecture) · [API](#api-surface) · [Configuration](#configuration) · [Local development](#local-development)

</div>

---

## Why this exists

In 2026, AI shopping agents (ChatGPT's purchase flow, Google AI Mode, the long tail of agentic checkout integrations on Shopify's Agentic Plan) have become the discovery and recommendation layer for a growing share of e-commerce traffic. When those agents misread a merchant's catalog, the merchant is either skipped entirely or recommended in a way the merchant never intended. Today, no merchant tool surfaces that gap.

Every AI-readiness scanner you can buy in 2026 inspects the documents the merchant has already written. Echomind Commerce takes a different starting point: the merchant's tacit knowledge. The product copy that should exist but doesn't. The policy edge cases handled by hand. The buyer signals the merchant reads in DMs but never put on the storefront.

You capture that knowledge through a Socratic interview, type it into a knowledge graph, and use it as ground truth to diagnose how four real LLMs represent the store right now.

## What you get

After an audit, you walk away with:

- **A typed knowledge graph** of your store: 11 node types covering products, policies, trust signals, the merchant's own truths, recurring patterns, customer questions, agent responses, gaps, and proposed fixes.
- **Live agent representations** captured verbatim from four real LLMs (GPT-OSS 120B, Llama 3.3 70B, Qwen3 80B, GLM-4.5 Air) running through OpenRouter on free-tier inference.
- **A calibrated gap report** with five gap classes (omission, contradiction, ambiguity, hallucination, dark zone), each labeled `certain`, `confident`, `uncertain`, `low_confidence`, or `dont_know`. The product refuses to fake numbers it cannot defend.
- **Auto-generated fix copy** in your brand voice (sampled from your own interview transcripts), with a predicted impact range.
- **Real Shopify mutations** that apply your approved fixes to the live store, with a snapshot/revert safety net.
- **A measured before/after delta** from re-running the same buyer prompts through the same agents after the fix.

## Quick start

Prereqs: Docker Desktop, an existing Shopify Partner Dev Store, and free-tier API keys for Gemini and OpenRouter (both available without a credit card).

```bash
git clone https://github.com/ShAuRyA-Noodle/echomind-commerce.git
cd echomind-commerce

cp .env.example .env
# fill in keys (see docs/SETUP_GUIDE.md for where to get each one)

docker compose up
# backend on http://localhost:8000
# frontend on http://localhost:3000
```

If you do not have an existing Shopify dev store, follow [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) section A. The whole setup, including obtaining every key from scratch, takes about 15 minutes.

## Walkthrough

This is what a single audit looks like end to end.

### 1. Connect your Shopify store

Open `http://localhost:3000/onboard`, click **Run ingest**. The backend hits Shopify Admin GraphQL with the access token from `.env`, paginates through every product, every page (FAQ, Shipping, Returns, etc.), and any product reviews stored as metafields. Each Shopify resource is mapped to a typed Neo4j node. Re-running is idempotent (deterministic content-hash IDs).

You should see a counter tick: `42 products, 7 policies, 62 reviews, duration 11s` (numbers depend on your store).

### 2. Run a Socratic interview

Open `http://localhost:3000/interview/<any-session-id>`. Click **Start interview**. The system asks you the first question through a real WebSocket. You answer either by:

- Clicking **Start mic** to use your browser's Web Speech API (Chrome only). The transcript streams in live.
- Typing into the text fallback box (Cmd or Ctrl + Enter to send).

Each merchant utterance triggers a Gemini Flash extraction pass that pulls typed knowledge from the chunk: a `MerchantTruth` (with `tacit_category` and `tacit_level` tags), a `Decision` if you described a choice point, a `Pattern` if you described a recurring behavior, a `CustomerQuestion` if you mentioned one, or a `Policy` if you stated one explicitly. New nodes pulse in on the right-side mini graph in real time.

The engine asks one question per turn, picked by a **frontier scorer** that weights five signals (depth need, connectivity gap, recency, centrality, phase fit). It cycles through five phases:

| # | Phase | Surfaces |
|---|---|---|
| 1 | Brand Mapping | positioning, voice, target buyer |
| 2 | Product Truths | hidden differentiators, fit, failure modes |
| 3 | Customer Reality | questions never made it to FAQ, real objections |
| 4 | Policy Edge Cases | exception rules, when policies bend |
| 5 | Trust Signals | why customers choose you over Amazon |

A complete interview runs about 20 minutes and lands roughly 60 to 120 `MerchantTruth` nodes plus connected entities.

### 3. Run the agent swarm

Open `http://localhost:3000/simulate/<any-run-id>`. Click **Run swarm**. The backend:

1. Generates 50 to 150 buyer-intent prompts from your `MerchantTruth` and `CustomerQuestion` nodes (Gemini Flash, distributed 40/25/20/15 across discover, compare, objection, post-purchase).
2. Fans every prompt out to all four swarm slots in parallel through OpenRouter.
3. Streams `agent_start` and `agent_done` events over a WebSocket so each column lights up live.

Every response is captured verbatim as an `AgentRepresentation` node, with surfaced product titles parsed out, a per-call latency, and a parse-failed flag if the model returned malformed JSON.

In demo mode, a 10 prompt × 4 model run (40 calls) finishes in roughly 30 seconds.

### 4. Diagnose the gaps

POST `/api/diagnose/run` (or hit the **Run diagnose** button on the audit dashboard). The backend runs five Cypher candidate queries against the graph (one per gap type), feeds each candidate to a Gemini Pro **judge** for classification, runs the calibration formula on the result, runs the parameterized revenue model, and ranks every gap by priority. The output is a typed `Gap` node per finding with:

- `type`: omission, contradiction, ambiguity, hallucination, or dark zone
- `severity`: 0 to 1
- `revenue_impact_usd_monthly`: estimated, with low/mid/high range available
- `calibration_label`: one of the five buckets
- `reasoning_chain`: every step cites specific source node IDs

Open `http://localhost:3000/audit/<store-id>` to see the dashboard. Gaps are split into four UI buckets: **Headline** (certain or confident), **Verify first** (uncertain), **Advanced view** (low_confidence), **Needs more data** (dont_know, never presented as actionable).

### 5. Drill into a gap

Click any gap card. `http://localhost:3000/diff/<gap-id>` opens with a five-section layout:

- **Agent says** (verbatim outputs from the swarm models that revealed the gap)
- **Merchant truth** (the relevant `MerchantTruth` node + the current product copy for comparison)
- **Reasoning chain** (a step-by-step animation that reveals each claim with cited source nodes; clicking a node ID jumps to the graph view)
- **Revenue impact** (every parameter exposed as an editable slider, low/mid/high range refreshes live)
- **Fix suggestion** (proposed copy in your voice, predicted delta range, **Apply** button)

### 6. Apply and re-test

Hit **Apply**. The backend runs a real Shopify Admin GraphQL `productUpdate` mutation. The catalog snapshot is taken automatically before the mutation in case revert is needed. The frontend then fires a scoped re-test that re-runs the buyer prompts that previously surfaced this gap, and reports the measured before/after surface-rate delta. Calibration of the prediction itself is shown alongside (in case the predicted range differs materially from the observed delta).

### 7. Explore the graph

`http://localhost:3000/graph/<store-id>` renders the full force-directed graph. Filter by node type, search by label, click any node to see its 1-hop neighbors. Confidence drives node opacity, type drives color, edge weight drives line thickness. The same colors are used by the mini graph in the interview view.

## Architecture

```
   YOU (the merchant)
     |
     |  Google Sign-In (Firebase Auth)
     v
  Next.js 14 frontend  -----------HTTP / WS-----------+
                                                       |
            +-------------------- FastAPI backend -----+
            |          (Python 3.11, websockets, async)
            |
            +--> Shopify Admin + Storefront GraphQL  (real merchant data)
            |
            +--> Google STT V2 (server) | Web Speech API (browser)
            |
            +--> Direct Gemini API           ----- extraction, judge, twin
            |
            +--> OpenRouter free tier        ----- 4-model agent swarm
            |
            +--> Neo4j AuraDB Free           ----- typed graph + vector index
            |
            +--> Firebase (Auth, Firestore, Storage)
```

Eleven typed node types and twelve edge types, all enforced by pydantic at the API boundary and zod at the frontend boundary. Five calibration buckets. Five gap types. Six tacit-knowledge categories. Every value is a Literal type, every enum is locked by a CI test that fails on drift.

## API surface

All endpoints live under `/api`. WebSockets carry live state; REST handles one-shot operations.

| Endpoint | Purpose |
|---|---|
| `POST /api/onboard/ingest/run` | Crawl Shopify, write Product / Policy / TrustSignal nodes |
| `GET  /api/onboard/ingest/status` | Live counts pulled from Neo4j |
| `POST /api/interview/start` | Issue a session ID |
| `WS   /api/interview/ws/{session_id}` | Live Socratic loop (text_input → extract → graph_update) |
| `POST /api/interview/{id}/extract` | Text-mode extraction over a transcript chunk |
| `POST /api/interview/{id}/next` | Frontier-scored next question |
| `POST /api/simulate/run` | Run swarm synchronously, return summary |
| `WS   /api/simulate/ws/{run_id}` | Live agent_start / agent_done event stream |
| `POST /api/diagnose/run` | Cypher candidate detection + Gemini Pro judge + ranker |
| `POST /api/fix/generate/{gap_id}` | Generate fix copy in merchant voice |
| `POST /api/fix/apply` | Push to Shopify Admin GraphQL (real mutation) |
| `GET  /api/audit/{store_id}` | Dashboard summary (readiness, calibration mix, totals) |
| `GET  /api/audit/{store_id}/gaps` | Ranked gap list with affected products |
| `GET  /api/graph/{store_id}` | Paginated nodes + edges for the viz |
| `GET  /api/graph/{store_id}/search?q=` | Text search across labels |
| `GET  /api/graph/{store_id}/node/{node_id}` | Node + 1-hop neighbors |
| `POST /api/audit/public/run` | Run a reduced audit on any public Shopify store with only its Storefront token |
| `GET  /api/debug/health` | Live Neo4j + Gemini + OpenRouter + Shopify probe |
| `GET  /api/debug/swarm` | Per-slot agent connectivity check |
| `GET  /api/debug/graph` | Per-type node + edge counts |
| `GET  /api/debug/env` | Sanitized view of which integrations are wired |

OpenAPI is auto-generated; once the backend is running, browse the live spec at `http://localhost:8000/docs`.

> **Auth & multi-tenant scoping.** The public demo runs with `AUTH_REQUIRED=false`, so these routes are open and the `{store_id}` segment is informational. The graph/audit/diagnose/fix reads and `/fix/apply` carry a server-side owner-scoping layer (`backend/api/ownership.py`) that activates automatically when a Firebase token is present: reads bind the owner's `uid` into Cypher, writes stamp `owner_uid`, and `/fix/apply` rejects cross-tenant mutations. **For a shared multi-tenant deployment, set `AUTH_REQUIRED=true` and gate the frontend behind sign-in** (the REST client already attaches the ID token when Firebase is configured). See [SECURITY.md §2.1](SECURITY.md#21-production-multi-tenant-checklist-required-before-a-shared-deployment) for the full production checklist.

## Configuration

Every setting is a typed environment variable. Defaults work for local dev. See [`.env.example`](.env.example) for the complete schema and source URLs.

| Variable | Used for | Where to get it |
|---|---|---|
| `GEMINI_API_KEY` | Extraction, gap judge, twin reasoning, embeddings | https://aistudio.google.com/apikey (free) |
| `OPENROUTER_API_KEY` | Four-model agent swarm | https://openrouter.ai/keys (free tier covers all four) |
| `NEO4J_URI` / `NEO4J_USERNAME` / `NEO4J_PASSWORD` / `NEO4J_DATABASE` | Typed knowledge graph + vector index | https://console.neo4j.io (AuraDB Free) |
| `SHOPIFY_STORE_DOMAIN` / `SHOPIFY_ADMIN_ACCESS_TOKEN` / `SHOPIFY_STOREFRONT_ACCESS_TOKEN` | Catalog crawl + mutations + simulation | https://partners.shopify.com → dev store → Apps → Custom Apps |
| `FIREBASE_*` (web client) | Frontend auth, Firestore, Storage | https://console.firebase.google.com → Project Settings → Web app |
| `GOOGLE_APPLICATION_CREDENTIALS` | Firebase Admin SDK + STT V2 (server-side) | Firebase Console → Service Accounts → Generate new private key |
| `OPENROUTER_AGENT_GPTOSS` / `_LLAMA` / `_QWEN` / `_GLM` | Swarm slot models (defaults to free tier) | OpenRouter model registry |

`.env` is gitignored; never commit it. `.env.example` is the canonical schema and is committed.

## Local development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

### Health check

```bash
make health
# Hits GET /health, returns Neo4j ping + a tiny Gemini test call.
```

### Common Make targets

```
make dev            docker compose up
make build          docker compose build
make logs           tail compose logs
make health         curl /health
make neo4j-init     apply Cypher constraints + vector indexes
make seed-shopify   bulk-import the 42-SKU sample catalog
make test           pytest
make lint           ruff + eslint
make help           full target list
```

## Testing

```bash
cd backend
pytest -q
```

Test categories:

- **Schema round-trip**: every pydantic node and edge accepts its sample payload, dumps to JSON, re-parses, equals the original.
- **Enum drift detector**: each Literal enum (calibration buckets, gap types, fix types, tacit categories, Socratic phases) is asserted against its canonical set. Any silent drift fails CI.
- **Calibration bucket boundaries**: every cutoff (0.80, 0.60, 0.35, 0.15) is locked with both inside-and-outside assertions. Three demo scenarios are encoded as integration tests (Yirgacheffe contradiction, decaf dark zone, partial provider failure).

GitHub Actions also runs an em-dash detector across all source files and verifies that every required document still exists.

## Deployment

The hackathon submission runs in `docker compose up` mode locally. For production:

- **Backend**: deploy `backend/` to Cloud Run (Cloud Build picks up `Dockerfile`). One service handles REST + WebSockets; concurrency 20, max instances 10, timeout 300s is enough for the agent swarm fan-out.
- **Frontend**: deploy `frontend/` to Vercel. Set the `NEXT_PUBLIC_*` env vars in the Vercel dashboard.
- **Neo4j**: AuraDB Free fits one merchant audit comfortably (about 1.5K nodes, 4.5K edges per audit; 50K / 175K free-tier cap).
- **Firestore + Storage**: Spark plan (free) covers the typical workload.
- **Tighten Firestore rules** to per-merchant + auth-required before going live (test mode is the dev default).

Per-audit cost at production volume runs about $5 to $8, dominated by paid swarm models if you choose to add OpenAI / Anthropic alongside the free tier.

## Project layout

```
echomind-commerce/
├── backend/
│   ├── api/              FastAPI routes + pydantic schemas
│   ├── config/           settings.py + prompts.py (12 LLM templates)
│   ├── core/
│   │   ├── socratic/     5-phase interview engine + frontier scorer + extractor
│   │   ├── agents/       OpenRouter swarm + concurrent runner + buyer prompt gen
│   │   ├── diagnose/     Cypher diff + Gemini Pro judge + calibrator + revenue model
│   │   ├── fix/          Copy generator + Shopify writer + retest orchestrator
│   │   ├── twin/         Diagnostic twin (subgraph retrieval + reasoning chain)
│   │   └── contradiction/ Detector + resolver
│   ├── graph/            Neo4j client + typed CRUD + named Cypher + schema bootstrap
│   ├── services/         Shopify, Google STT V2, Gemini + OpenRouter LLM, Firebase
│   └── tests/            Schema round-trip + calibration formula + boundary tests
├── frontend/
│   ├── app/              9 routes (onboard, interview, simulate, audit, diff, graph, policies, replay)
│   ├── components/       ReasoningTrace animation, TacitKnowledgePanel, GapCard, ForceGraph
│   └── lib/
│       ├── hooks/        useInterviewSocket, useSimulateSocket
│       ├── ws-client.ts  Typed reconnect + dedupe
│       ├── api-client.ts Typed fetch + zod runtime validation
│       └── colors.ts     Single source of truth for node + calibration palette
├── scripts/              Sample 42-SKU catalog + Shopify Admin GraphQL importer
├── docs/                 Setup, demo script, competitive analysis, cinematic trailer storyboard
└── .github/              Issue + PR templates, CI workflow
```

## Tech stack

| Layer | Choices |
|---|---|
| Backend | Python 3.11, FastAPI 0.115, uvicorn, websockets 13, pydantic 2.9, pydantic-settings, tenacity, httpx, neo4j 5.25, google-generativeai, google-cloud-speech, openai (for OpenRouter), firebase-admin |
| Frontend | Next.js 14.2, React 18.3, TypeScript 5.5 (strict), Tailwind 3.4, shadcn/ui, react-force-graph-2d, @tanstack/react-query, recharts, firebase, zod |
| Data | Neo4j AuraDB (typed property graph + 768-dim cosine vector index), Firestore (sessions, transcripts, change log), Cloud Storage (audio, exports) |
| LLMs | Gemini 2.5 Flash + Pro direct (extraction, judge, twin), text-embedding-004 (entity resolution), OpenRouter free-tier swarm (GPT-OSS 120B, Llama 3.3 70B, Qwen3 80B MoE, GLM-4.5 Air) |
| Speech | Browser Web Speech API by default; Google STT V2 streaming wired as an optional server-side path |
| Infra | Docker Compose for local boot; Cloud Run + Vercel for production |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Three rules with teeth:

1. No em dashes anywhere in the codebase. CI enforces it.
2. Atomic commits in conventional format. Every behavior change updates [docs/DECISION_LOG.md](docs/DECISION_LOG.md) with one new entry.
3. Calibration discipline: every numeric output exposes a calibration label, and we never claim numerical accuracy we have not measured.

## Documentation

- [docs/PRODUCT_DOC.md](docs/PRODUCT_DOC.md) - problem, target user, key decisions, scope cuts
- [docs/TECHNICAL_DOC.md](docs/TECHNICAL_DOC.md) - architecture, AI vs deterministic boundary, failure modes, calibration formula
- [docs/DECISION_LOG.md](docs/DECISION_LOG.md) - 26+ append-only architectural and product decisions
- [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - step-by-step Shopify Custom App, Firebase, Cloud APIs
- [docs/JUDGE_REPLICATION.md](docs/JUDGE_REPLICATION.md) - 4-step path from clone to running localhost
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) - verbatim demo walkthrough
- [docs/CINEMATIC_TRAILER.md](docs/CINEMATIC_TRAILER.md) - 90-second backup video storyboard
- [docs/COMPETITIVE_ANALYSIS.md](docs/COMPETITIVE_ANALYSIS.md) - how this differs from Delphi.ai, Personal AI, Glean, NotebookLM, Shopify Magic
- [SECURITY.md](SECURITY.md) - data flows, IP ownership, vulnerability disclosure
- [CHANGELOG.md](CHANGELOG.md) - notable changes by version

## License

MIT - see [LICENSE](LICENSE).
