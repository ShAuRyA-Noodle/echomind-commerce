# Echomind Commerce - Judge Replication Guide

Goal: a hackathon judge clones the repo and reaches a working `localhost:3000` in under 30 minutes on a fresh machine.

---

## Prerequisites

- macOS or Linux (Windows via WSL2 should work but is untested)
- Docker Desktop (running)
- Python 3.11
- Node 20 (only needed if running the frontend outside Docker)
- Git

Confirm:

```bash
docker --version
python3 --version    # 3.11.x
node --version       # v20.x
```

---

## Steps

### 1. Clone the repo

```bash
git clone <repo-url> echomind-commerce
cd echomind-commerce
```

### 2. Provision credentials

Echomind needs API keys for Shopify (Admin + Storefront), Firebase (`echomind699` project + Admin SDK JSON), Neo4j AuraDB, Gemini, OpenRouter, and Google Cloud Speech-to-Text.

```bash
cp .env.example .env
```

Open `.env` and fill every variable. **The exhaustive how-to-get-each-key walkthrough lives in `docs/SETUP_GUIDE.md`** - it covers the Shopify Custom App, Admin / Storefront tokens, Firebase Admin SDK service-account JSON, STT API enablement, and Neo4j AuraDB.

Drop the Firebase Admin SDK JSON at:

```
./firebase-admin-credentials.json
```

(Already gitignored. Path matches `GOOGLE_APPLICATION_CREDENTIALS` in `.env.example`.)

### 3. Bring up the stack

```bash
docker compose up --build
```

First build is ~5-8 minutes (Python deps + Node build). Subsequent runs are seconds.

Services started:

- `web` - Next.js frontend on `:3000`
- `api` - FastAPI backend on `:8000`
- `worker` - background ingestion / RAG indexer
- (Neo4j and Firebase are managed services; no local containers needed.)

### 4. Open the app

Visit:

```
http://localhost:3000
```

---

## Day 1 acceptance

You should see:

1. The **landing page** render at `/`.
2. Clicking **Get started** → **Google sign-in** popup → returns to the app authenticated.
3. The **onboarding wizard** appears (step 1 of N).

That's the Day 1 acceptance bar. Acceptance criteria for later days (RAG ingest, recommendation engine, voice interview, etc.) are tracked in `docs/WINNING_PLAN.md` per Day-by-Day section.

---

## Smoke tests

From the repo root, with the stack up:

```bash
make health
```

Expected:

```
api: OK
firebase: OK
neo4j: OK
gemini: OK
shopify-admin: OK
shopify-storefront: OK
```

Any `FAIL` line maps 1:1 to a missing or wrong env var - re-check the matching section of `SETUP_GUIDE.md`.

```bash
make neo4j-init
```

Expected: creates constraints and indexes on the AuraDB instance, prints `neo4j-init: done`. Idempotent - safe to re-run.

---

## Troubleshooting one-liners

- `docker compose up` exits immediately → check `.env` exists and has no trailing `=` lines without values.
- `firebase: FAIL` in `make health` → confirm `firebase-admin-credentials.json` exists and `GOOGLE_APPLICATION_CREDENTIALS` points to it.
- `shopify-admin: FAIL` → token must start with `shpat_`. Re-copy from the Shopify custom-app **API credentials** tab.
- `neo4j: FAIL` → password copy/paste error is the most common cause; re-paste from the AuraDB credentials file.
- Firebase Storage blocked during setup → see `SETUP_GUIDE.md` §C. Storage is a stretch-goal dependency; the rest of the demo runs without it.

---

## What to demo

1. Onboard a seller (Google sign-in → wizard → connect Shopify dev store `fulcrum-coffee-co`).
2. Trigger product ingest → watch the Neo4j browser populate.
3. Open the buyer-side simulator → ask a product question → see the RAG-grounded answer with citations.
4. Inspect the recommendation panel.

Full demo script lives in `docs/DEMO_SCRIPT.md` (added Day 12).
