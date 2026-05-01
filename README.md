<div align="center">

# Echomind Commerce

### AI Representation Optimizer for Shopify

**Track 5 submission, KASPARRO Agentic Commerce Hackathon 2026**

Interview the merchant. Simulate four real AI shopping agents. Diagnose the gaps. Apply fixes. Re-test live.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/next.js-14-black.svg)](https://nextjs.org/)
[![Neo4j](https://img.shields.io/badge/neo4j-AuraDB-008CC1.svg)](https://neo4j.com/cloud/aura/)
[![Gemini](https://img.shields.io/badge/gemini-2.5-4285F4.svg)](https://aistudio.google.com/)
[![OpenRouter](https://img.shields.io/badge/openrouter-free%20tier-6750A4.svg)](https://openrouter.ai/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-pytest-0A9396.svg)](backend/tests)

[Product Doc](docs/PRODUCT_DOC.md) · [Technical Doc](docs/TECHNICAL_DOC.md) · [Decision Log](docs/DECISION_LOG.md) · [Demo Script](docs/DEMO_SCRIPT.md) · [Competitive Analysis](docs/COMPETITIVE_ANALYSIS.md)

</div>

---

## What is Echomind Commerce?

In 2026, three things converged inside a single quarter: ChatGPT began closing purchases inside the chat surface, Google AI Mode started recommending products inside search, and Shopify launched its Agentic Plan to wire every merchant's catalog into AI shopping channels by default.

The consequence: AI agents are now the **discovery, comparison, and checkout layer** for an increasing share of Shopify GMV. When those agents misread a merchant's catalog, the merchant is either skipped or misrepresented. Today, merchants have **no way to see how AI agents see them**, and no closed-loop way to fix it.

Every other AI-readiness tool in 2026 will diagnose merchants against the documents the merchant **already failed to write**. Echomind Commerce diagnoses them against the merchant's **actual brain**.

## The closed loop

```
Connect Shopify       (real OAuth + Admin GraphQL crawl)
        v
Socratic Interview    (20 min, voice-first, types tacit knowledge into a graph)
        v
Agent Swarm           (50-150 buyer prompts x 4 real LLMs running in parallel)
        v
Gap Diagnosis         (typed knowledge graph diff + Gemini Pro judge + 5-bucket calibration)
        v
Fix Generation        (Gemini Pro copy in merchant voice, predicted delta range)
        v
Apply to Shopify      (real Admin GraphQL mutation; snapshot/revert safety)
        v
Re-test               (same buyer prompts, same agents; measured before/after delta)
```

**Nothing in this loop is mocked.** Real Shopify mutations. Real LLM calls. Real Neo4j writes. Real before/after measurements.

## Why this wins Track 5

| Differentiator | Echomind Commerce | Typical Track 5 entry |
|---|---|---|
| Diagnostic ground truth | Merchant brain captured by Socratic AI | RAG over docs the merchant already wrote |
| Agent comparison | 4 real LLMs in parallel (GPT-OSS, Llama 3.3, Qwen3, GLM-4.5) | Single LLM, or none |
| Calibration | 5-bucket including visible "I don't know" output | Confident-looking numbers, no uncertainty |
| Fix loop | Apply to live Shopify, re-test, measure observed delta | Recommendation list, no closure |
| Public mode | Tier S #1 endpoint, anyone pastes a Shopify URL | Per-merchant only |
| Originality | Tacit Knowledge Capture Score, six categories | Generic readiness score |

## The four-model agent swarm

We test the merchant's store against a representative slice of the real 2026 AI shopping ecosystem. All free-tier; verified live.

| Slot | Provider | Model | Represents |
|---|---|---|---|
| `gpt_oss` | OpenAI | `openai/gpt-oss-120b:free` | OpenAI / ChatGPT class |
| `llama` | Meta | `meta-llama/llama-3.3-70b-instruct:free` | Meta AI + open-weight agent stacks |
| `qwen` | Alibaba | `qwen/qwen3-next-80b-a3b-instruct:free` | Qwen / Alibaba ecosystem |
| `glm` | Zhipu | `z-ai/glm-4.5-air:free` | Chinese frontier |
| `adversarial` (stretch) | Nous | `nousresearch/hermes-3-llama-3.1-405b:free` | 405B for hostile prompts |

All swarm calls go through OpenRouter (one OpenAI-compatible API). Direct Gemini API powers extraction, the gap judge, and twin reasoning.

## Quick start

```bash
git clone https://github.com/ShAuRyA-Noodle/Orange-Kid.git echomind-commerce
cd echomind-commerce

cp .env.example .env
# fill in keys (see SETUP_GUIDE.md for sources)

docker compose up
# backend on :8000, frontend on :3000

open http://localhost:3000
```

## Architecture

```
Next.js 14 frontend  ----HTTP/WS---->  FastAPI backend (Python 3.11)
                                            |
                          --------------------------------------------
                          |             |              |             |
                     Shopify        Google STT       OpenRouter    Gemini
                     Admin/Storefr  V2 streaming     (4-model      Flash + Pro
                     GraphQL                          swarm)        + embed-004
                          |             |              |             |
                          --------------------------------------------
                                            |
                                  ----------------------
                                  |                    |
                              Neo4j AuraDB         Firebase
                              (typed graph        (Auth + Firestore
                               + vector index)     + Storage)
```

11 typed node types, 12 edge types, 5 gap types, 5 fix types, 5 calibration buckets, 5 Socratic phases, 6 tacit-knowledge categories. All locked by enum tests.

## Repository layout

```
echomind-commerce/
  backend/
    api/             FastAPI routes + pydantic schemas
    config/          settings.py + prompts.py (12 prompts, single source of truth)
    core/
      socratic/      5-phase interview engine + frontier scorer + extractor
      agents/        OpenRouter swarm + concurrent runner + buyer prompt gen
      diagnose/      Cypher diff + Gemini Pro judge + calibrator + revenue model
      fix/           Copy generator + Shopify writer + retest orchestrator
      twin/          Diagnostic twin (subgraph retrieval + reasoning chain)
      contradiction/ Detector + resolver
    graph/           Neo4j client + typed CRUD + named Cypher queries + schema
    services/        Shopify, STT V2, LLM (Gemini + OpenRouter), Firebase
    tests/           Schema round-trip + calibration formula
  frontend/
    app/             9 routes (onboard / interview / simulate / audit / diff / graph / policies / replay / public)
    components/      ReasoningTrace animation, TacitKnowledgePanel, GapCard, CalibrationBadge
    lib/             firebase, api-client (zod), ws-client (typed reconnect+dedupe), colors
  scripts/           Fulcrum Coffee 42-SKU seed catalog + Shopify importer
  docs/              Product, Technical, Decision Log, Setup, Demo, Competitive Analysis
```

## The numbers

| Metric | Value |
|---|---|
| Node types | 11 (Product, Policy, TrustSignal, MerchantTruth, Decision, Pattern, CustomerQuestion, BuyerPrompt, AgentRepresentation, Gap, FixSuggestion) |
| Edge types | 12 |
| Centralized LLM prompts | 12 |
| Calibration buckets | 5 (certain / confident / uncertain / low_confidence / dont_know) |
| Tacit knowledge categories | 6 |
| Gap types detected | 5 |
| Fix types generated | 5 |
| Swarm models | 4 (free-tier) |
| API endpoints | 10 routers |
| Cost per audit (hackathon) | $0 (all free tier) |
| Cost per audit (production) | $5-8 |

## Key documents

- **[Product Doc](docs/PRODUCT_DOC.md)** - problem, target user, key decisions, scope cuts, tradeoffs, success criteria.
- **[Technical Doc](docs/TECHNICAL_DOC.md)** - architecture, AI vs deterministic boundary, full data model, five named failure modes, calibration formula, cost model.
- **[Decision Log](docs/DECISION_LOG.md)** - 26+ append-only decisions with reasoning, tradeoffs, and implications.
- **[Demo Script](docs/DEMO_SCRIPT.md)** - verbatim 5-minute single-take flow with pre-roll checklist.
- **[Competitive Analysis](docs/COMPETITIVE_ANALYSIS.md)** - head-to-head vs. Delphi.ai, Personal AI, Glean, NotebookLM, Shopify Magic.
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Shopify Custom App + Firebase Admin SDK + Cloud APIs.
- **[Judge Replication](docs/JUDGE_REPLICATION.md)** - 4-step path from clone to running localhost.
- **[Security & Privacy](SECURITY.md)** - data flows, IP ownership, liability boundaries.
- **[Changelog](CHANGELOG.md)** - what shipped, when, why.

## Calibration formula (verbatim from WINNING_PLAN section 9.3)

```
adjusted = 0.4 * raw_confidence
         + 0.3 * evidence_factor
         + 0.3 * coverage_factor

label = >= 0.80 certain | >= 0.60 confident | >= 0.35 uncertain
      | >= 0.15 low_confidence | else dont_know

CRITICAL distinction:
    "I don't know"  = subgraph has no relevant nodes (coverage < 0.15)
    "I'm uncertain" = relevant nodes exist but are sparse / contradictory
```

The 5-bucket label is auditable. We do not claim numerical calibration accuracy.

## Free-tier first

All five integrated services run on free tier. Zero marginal cost per audit during development. Production unit economics: $5-8 per audit at scale.

| Service | Free tier | Used for |
|---|---|---|
| Gemini direct API | 1.5M tokens/day Flash, 50 RPM Pro | Extraction, question gen, gap judge, twin reasoning |
| OpenRouter `:free` | Per-model rate limits | 4-model agent swarm |
| Google STT V2 | 60 minutes/month | Live interview transcription |
| Neo4j AuraDB | 50K nodes / 175K edges | Typed knowledge graph + vector index |
| Firebase Spark | Generous | Auth + Firestore + Storage |
| Shopify Dev Store | Unlimited | Real merchant infrastructure |

## License

MIT - see [LICENSE](LICENSE).

## Acknowledgements

Built for the [KASPARRO Agentic Commerce Hackathon 2026](https://kasparro.com). Original Echomind technical thesis (Socratic interview + typed knowledge graph + calibrated twin) was redirected at AI shopping agents in this submission. The blueprint, decision log, and pivot rationale are documented in `WINNING_PLAN.md` at the parent directory of the project workspace and in [docs/DECISION_LOG.md](docs/DECISION_LOG.md).
