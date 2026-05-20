# Contribution Note

**Project:** Echomind Commerce
**Team:** Solo submission - Shaurya Punj
**Duration:** 14 days (planning + pre-build May 1-9, build window May 10-20, 2026)

---

## Team composition

Single contributor. All product thinking, engineering, and documentation work done by one person.

---

## Time split

| Phase | Days | % | What happened |
|---|---|---|---|
| Strategic planning + hackathon analysis | 1-2 | 14% | Read all rules, analyzed 5 tracks, made pivot decision (expert twin -> merchant AI readiness), drafted WINNING_PLAN.md |
| Product thinking + documentation | 1-3 | 21% | PRODUCT_DOCUMENT, TECHNICAL_DOCUMENT, DECISION_LOG (26 entries), COMPETITIVE_ANALYSIS, DEMO_SCRIPT, SECURITY, SETUP_GUIDE, JUDGE_REPLICATION, CINEMATIC_TRAILER |
| Infrastructure + credentials | 3-4 | 7% | Shopify Partner account, dev store, custom app, Firebase project + Auth + Firestore + Storage, Neo4j AuraDB Free, Gemini API key, OpenRouter key |
| Backend architecture + core engine | 4-7 | 21% | FastAPI app, pydantic schemas (11 nodes, 12 edges), 12 centralized LLM prompts, Neo4j client, Shopify client, LLM service (Gemini + OpenRouter), Socratic engine (5 phases, frontier scorer, extractor, question gen), agent swarm (OpenRouter 4-model, concurrent runner), diagnose pipeline (Cypher diff, Gemini Pro judge, calibrator, revenue model, ranker), fix loop (copy gen, Shopify writer, retest orchestrator) |
| Frontend + UI | 7-10 | 21% | Next.js 14, 9 routes, Firebase init, WebSocket hooks (useInterviewSocket, useSimulateSocket), ForceGraph2D wrapper, cinematic ReasoningTrace animation, TacitKnowledgePanel, GapCard, CalibrationBadge, live interview page (3 columns, Web Speech API mic), live simulate page (4-column streaming), audit dashboard (live Neo4j reads), diff page (reasoning trace + revenue sliders), graph viz (filtered, searchable, click-to-detail) |
| Integration + alignment audit | 10-12 | 14% | Wired all 14 REST endpoints + 2 WS handlers to real core modules, fixed CalibrationLabel taxonomy mismatch, MerchantTruth schema alignment, GapType taxonomy alignment, fixed 2 test calibration assertions, CI green (3 jobs), em-dash sweep (1172 replacements), README rewrite |
| Catalog + demo prep | 12-14 | 7% | 42-SKU Fulcrum Coffee catalog with 6 baked-in gaps, 7 policies with shipping contradiction, 62 reviews, Shopify importer script, catalog seeded to live dev store |

---

## What "product thinking" meant in practice

This was not a documentation-only exercise. Every product decision came from first-principles reasoning about the hackathon judging criteria, the competitive landscape, and what would make a merchant actually want to use this tool. Specific examples:

- **The pivot** from expert-twin to merchant AI readiness was a full architectural decision made on Day 1 after realizing the original Echomind blueprint scored ~0/15 on Business Relevance for this hackathon.
- **The calibrated "I don't know"** was a product call, not an engineering one. It would have been easier to always emit a number. The decision not to was deliberate and is the product's core differentiator.
- **The four-model swarm using only free-tier OpenRouter models** was both a product decision (represents the real 2026 agentic ecosystem better than premium APIs) and an engineering constraint (no budget). The narrative reframe turned the constraint into a strength.
- **The tacit knowledge interview** (instead of RAG over existing docs) is the structural moat. This was identified on Day 1 and drove every subsequent architecture choice.

---

## What "development" meant in practice

125 atomic commits over 14 days, each with a meaningful commit message explaining why not just what. The git history is the clearest record of the build progression:
- Docs-first Day 1: PRODUCT_DOC, TECHNICAL_DOC, DECISION_LOG committed before any feature code.
- Feature commits organized by layer: schemas -> prompts -> services -> graph -> socratic -> agents -> diagnose -> fix -> API endpoints -> frontend.
- Bug fix commits (CalibrationLabel alignment, test calibration assertions) with explicit explanation of the math error corrected.

---

## Tools and infrastructure used

| Tool | Purpose |
|---|---|
| Python 3.11 + FastAPI | Backend |
| Next.js 14 + TypeScript | Frontend |
| Neo4j AuraDB Free | Knowledge graph |
| Gemini 2.5 Flash + Pro (direct API) | LLM engine |
| OpenRouter free tier | 4-model agent swarm |
| Firebase (Auth + Firestore + Storage) | Session persistence |
| Shopify Partner Dev Store | Real merchant infrastructure |
| GitHub Actions | CI (pytest, tsc, eslint, em-dash detector) |
| Docker Compose | Local stack orchestration |

---

## Decision log

26 documented architectural decisions at `docs/DECISION_LOG.md`, each with: Decision / Considered / Chose / Reason / Tradeoff / Implication. Committed one entry per commit on Day 1 to create a provable thinking history.

---

*Shaurya Punj*
*Echomind Commerce, May 2026*
