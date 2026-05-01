# Changelog - Echomind Commerce

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows [SemVer](https://semver.org/spec/v2.0.0.html). The build window for the Kasparro Agentic Commerce Hackathon is 10-20 May 2026; entries dated before that are pre-build scaffolding.

---

## [Unreleased]

### Planned for Day 1 (2026-05-10)
- Atomic doc commits: PRODUCT_DOC, TECHNICAL_DOC, DECISION_LOG entries 1-15
- Backend / frontend boot via `docker compose up`
- `/health` endpoint pings live Neo4j AuraDB + live Gemini API

### Planned for Day 2 (2026-05-11)
- Real Shopify OAuth flow via Partner Custom App
- Admin GraphQL crawler → Firestore + Neo4j (`Product`, `Policy`, `TrustSignal` nodes)
- `/onboard` page with live ingest counter

### Planned for Day 3 (2026-05-12)
- Socratic engine: 5 commerce phases, frontier scorer, redundancy checker
- Gemini Flash typed extraction (`MerchantTruth`, `Decision`, `Pattern`, `CustomerQuestion`, `Policy`)
- Phase manager with statistical advancement triggers
- Text-mode interview loop end-to-end

### Planned for Day 4 (2026-05-13)
- Google STT V2 streaming integration
- WebSocket route for live audio
- 3-column `/interview/[id]` view with live mini-graph (`react-force-graph-2d`)

### Planned for Day 5 (2026-05-14)
- Agent swarm: OpenAI-compatible OpenRouter client (Llama / Qwen / DeepSeek) + Gemini Flash direct
- Buyer-intent prompt generator (50-150 per audit)
- 4-column `/simulate/[runId]` with streaming tokens
- `BuyerPrompt` and `AgentRepresentation` nodes persist live to Neo4j

### Planned for Day 6 (2026-05-15)
- Cypher gap-detection queries for the 5 gap types
- Gemini Pro judge with rubric → `Gap` nodes
- Calibrator (5-bucket WINNING_PLAN §9.3 formula)
- Revenue impact model (parameterized, range-not-point)

### Planned for Day 7 (2026-05-16)
- `/audit/[storeId]` dashboard
- `/diff/[gapId]` deep-dive view
- AI Readiness Radar + Coverage Heatmap
- Reasoning trace accordion (per-step source-node links)

### Planned for Day 8 (2026-05-17)
- `core/fix/copy_generator.py` (merchant-voice samples conditioning)
- `core/fix/shopify_writer.py` (real Admin GraphQL mutations)
- Re-test orchestrator with before/after delta computation
- Acceptance test: 3 different gaps complete the full closed loop with measured deltas

### Planned for Day 9 (2026-05-18)
- Failure-mode rehearsal: kill Shopify token → reconnect prompt; block OpenRouter → partial-sample run; malformed Gemini JSON → fallback extraction with calibration downgrade
- Living Update Loop wired in `/audit`
- Decision Tree Vault `/policies/[type]` (stretch)
- Replay Theater `/replay/[auditId]` (stretch)

### Planned for Day 10 (2026-05-19)
- Final pass on PRODUCT_DOC, TECHNICAL_DOC, DECISION_LOG (≥20 entries), Contribution Note
- Demo video recording (single take, all live, no edits hide failures)
- Backup demo recording
- README setup instructions verified on a fresh machine

### Planned for Day 11 (2026-05-20, submission day)
- Dry-run full setup on a fresh machine using only the README
- Tighten Firestore security rules to per-merchant + auth-required (Decision Log #23)
- Final tag `v1.0-submission`
- Submit by **18:00 IST** to https://forms.gle/sYaqxeyBAajNPV9t7

---

## [0.0.1] - 2026-05-01 (pre-build scaffolding, current state)

### Added
- Repo skeleton (`backend/`, `frontend/`, `docs/`, `scripts/`).
- `.env` schema with all 30+ environment variables typed in `pyproject.toml` + `pydantic-settings`.
- Backend FastAPI app with lifespan handlers, CORS, all 8 routers mounted, real `/health` that pings Neo4j and Gemini.
- Frontend Next.js 14 with all 9 routes rendering placeholder shells, real Firebase init from `NEXT_PUBLIC_*` env, dark-mode default.
- `services/llm_service.py` - real working Gemini Flash / Pro / embedding wrapper + OpenRouter sync/async client, all wrapped with `tenacity` retries.
- `graph/neo4j_client.py` - async-first Neo4j wrapper with `verify_connectivity()` and `ping()` returning server version.
- `graph/schema.py` - idempotent Cypher constraints + indexes + 768-dim cosine vector indexes for the 4 embedding-bearing node types.
- `api/schemas.py` - pydantic 2 models for all 11 nodes + 12 edges + reasoning-trace primitives.
- `config/prompts.py` - 12 production-grade prompt templates: Socratic question gen, extraction, buyer prompts, agent simulator system prompt, gap judge, calibrator, fix copy gen, decision-tree builder, contradiction resolver, twin reasoning (verbatim port from Echomind §6.4), adversarial buyer, redundancy check.
- Catalog seed data: `scripts/fulcrum-catalog.json` (42 SKUs), `scripts/fulcrum-policies.json` (7 policies), `scripts/fulcrum-reviews.json` (62 reviews) - with 6 intentional gaps baked in for the demo to discover.
- `scripts/import_to_shopify.py` - idempotent Admin GraphQL importer with dry-run flag.
- Docker Compose + Dockerfiles + Makefile (12 targets) + `.pre-commit-config.yaml` + `.dockerignore`.
- Documentation: PRODUCT_DOC.md, TECHNICAL_DOC.md, DECISION_LOG.md (26 entries), SETUP_GUIDE.md, JUDGE_REPLICATION.md, DEMO_SCRIPT.md, COMPETITIVE_ANALYSIS.md, SECURITY.md.
- LICENSE (MIT).

### Fixed (post-scaffolding alignment audit, 2026-05-01)
- **Critical**: `api/schemas.py::CalibrationLabel` was using a wrong taxonomy (`highly_calibrated / well_calibrated / …`) that mismatched WINNING_PLAN §9.3 + every other surface. Replaced with the canonical 5-bucket `certain / confident / uncertain / low_confidence / dont_know`. Without this fix, every gap output from Gemini Pro would have failed pydantic validation.
- **Critical**: `MerchantTruth` was missing the 6-value `tacit_category` field (Tacit Knowledge Taxonomy from WINNING_PLAN §7), and the existing `category` field was being asked to do double duty in `prompts.py::EXTRACTION_PROMPT_FLASH`. Both fields now exist as orthogonal classifications and `prompts.py` outputs both.
- **Critical**: `MerchantTruth` was missing `verbatim_quote` field used by extraction prompt for the audit trail. Added.
- **Critical**: Frontend `components/gap-card.tsx::GapType` used yet a third taxonomy (`missing_node / agent_misread / policy_ambiguity / trust_signal_gap`). Aligned to the canonical 5 (`omission / contradiction / ambiguity / hallucination / dark_zone`) and added type-help tooltips.
- **Frontend**: `lib/colors.ts::NodeType` was missing `BuyerPrompt` (10 of 11 node types). Added with a distinct violet color.
- **Docs**: `DECISION_LOG.md` #7 used informal `tentative / low_conf` labels; aligned to the canonical 5-bucket names.
- **Docs**: `TECHNICAL_DOC.md` referenced `gemini-2.0-flash` but the configured `.env` and the user's API key resolve to `gemini-2.5-flash`. Updated to reflect the parameterized 2.0/2.5 cutover policy named in Decision Log #19.
- **Docs**: `README.md` had a redundant `## Setup` section after the Quick Start was added, and the docs index labeled artifacts as "*coming Day 1*" when they were already present. Polished both.

### Added (post-audit polish, 2026-05-01)
- `SECURITY.md` - explicit privacy / IP / liability / data-lifecycle posture.
- `docs/COMPETITIVE_ANALYSIS.md` - head-to-head vs. Delphi.ai, Personal AI, Glean, NotebookLM, Shopify Magic, RAG-on-docs entrants. Pre-empts the obvious judge questions.
- `docs/DEMO_SCRIPT.md` - verbatim 5-minute single-take demo flow with pre-roll checklist and post-roll verification.
- `CHANGELOG.md` - this file.
- `LICENSE` - MIT.

---

## Versioning policy

- `0.0.x` - pre-build scaffolding, before the build window opens.
- `0.1.x` - daily build-window snapshots (Day 1 = 0.1.0, Day 2 = 0.1.1, etc.).
- `1.0.0` - submission tag (`v1.0-submission`), 2026-05-20 ≤ 18:00 IST.
- `1.1.x+` - post-submission cleanup (only if invited to interview).

Each Day-N build entry includes (a) what shipped, (b) which Decision Log entries were added that day, (c) which acceptance test passed.
