# Product Document

**Project:** Echomind Commerce
**Track:** Track 5 - AI Representation Optimizer
**Hackathon:** KASPARRO Agentic Commerce Hackathon 2026

---

## 1. The Problem

In 2026, three things converged in a single quarter: ChatGPT began completing purchases inside the chat surface. Google AI Mode started recommending products directly inside search. Shopify launched its Agentic Plan to wire every merchant's catalog into AI shopping channels by default.

The consequence is structural: **AI agents are now the discovery, comparison, and checkout layer for a growing share of Shopify GMV.** When an agent misreads a merchant's catalog, the merchant is either skipped entirely or surfaced with a misrepresentation. Neither outcome is visible to the merchant. There is no dashboard, no alert, no audit trail.

The deeper problem is that the most valuable part of a merchant's brand, the tacit knowledge of who buys what and why, when policies bend, which products fail for which use cases, has historically never been written down. Every AI-readiness tool that exists in 2026 will diagnose merchants against the documents the merchant has already failed to write. None will diagnose them against the merchant's actual brain.

**The gap is structural:** every AI-readiness tool today diagnoses merchants against the documents they already failed to write. Echomind Commerce is the first to diagnose them against the merchant's actual knowledge.

---

## 2. Who We Built It For

**Primary user:** Shopify merchants in the $100K to $5M annual revenue range. Typically 1 to 10 person teams, founder-led or merchandiser-led, with deep category expertise but zero in-house AI engineering. They are too small for a full agency engagement, too large to ignore the Agentic Plan rollout, and they already feel the revenue leak. They just cannot name it.

**Secondary user:** Kasparro itself, because every customer of theirs fits this profile precisely.

**For the hackathon submission:** The real-world user is the builder running the live demo against a real Shopify dev store (Fulcrum Coffee Co.), conducting a real voice interview, running a real four-model agent swarm, and applying a real Admin API fix. The architecture supports third-party merchants without changes.

---

## 3. What We Built

Echomind Commerce is an **AI Representation Optimizer** that closes a six-step loop:

```
Connect Shopify    ->  Interview merchant  ->  Simulate AI agents
       |                      |                       |
  Real OAuth           Voice-first,            4 real LLMs
  Admin GraphQL       frontier-scored         OpenRouter free tier
  catalog crawl      Socratic engine          concurrent fan-out
       |                      |                       |
       +-----> Typed knowledge graph (Neo4j) <--------+
                              |
                        Diagnose gaps
                   (5 gap types, calibrated)
                              |
                        Generate fix
                   (Gemini Pro, merchant voice)
                              |
                     Apply to Shopify
                  (real Admin GraphQL mutation)
                              |
                         Re-test live
                   (same prompts, same agents)
                   measured before/after delta
```

**Nothing in this loop is mocked.** Every step touches real infrastructure: real Shopify tokens, real LLM API calls, real Neo4j writes, real Shopify product mutations.

---

## 4. Key Product Decisions

### 4.1 Tacit knowledge as ground truth (not RAG over existing docs)
**Considered:** RAG over the merchant's existing product copy and FAQ.
**Chose:** Socratic interview that surfaces knowledge the merchant has never written down.
**Why:** Categories 4 (Intuitive Judgment), 5 (Edge Case Knowledge), and 6 (Meta-Knowledge) of our Tacit Knowledge Taxonomy are structurally inaccessible to RAG. The interview is the moat. Every other tool in this category will miss these three categories entirely.

### 4.2 Multi-agent simulation across four model families
**Considered:** Single-LLM simulation.
**Chose:** Four real model families: GPT-OSS 120B, Llama 3.3 70B, Qwen3 80B (MoE), GLM-4.5 Air, all via OpenRouter free tier.
**Why:** The unique product insight is comparison. You cannot tell a merchant "AI agents misrepresent you" using one agent. Four families also mirrors the real 2026 agentic shopping ecosystem, where the long tail of integrations runs on open-weight models for cost reasons.

### 4.3 Calibrated "I don't know" as first-class output
**Considered:** Always emit a number with a confidence percentage.
**Chose:** Five-bucket calibration (certain / confident / uncertain / low_confidence / dont_know), with `dont_know` surfaced visibly and never hidden.
**Why:** Diagnostic tools that overclaim are useless. The `dont_know` label is the product principle. It is shown during the demo, on purpose, even though it deflates one moment, because the credibility it buys is worth more than that moment.

### 4.4 Closed-loop fix, retest, measured delta
**Considered:** Produce a ranked PDF of issues and stop there.
**Chose:** Push real Shopify Admin GraphQL mutations, re-run the same buyer prompts against the same agents, report the measured before/after surface-rate delta.
**Why:** Lists of problems are not products. Deltas are products. If the delta underperforms the predicted range, that is also surfaced, not hidden.

### 4.5 Free-tier-first architecture
**Considered:** Paying for premium OpenAI/Anthropic API access for the swarm.
**Chose:** Zero marginal cost per audit using Gemini free tier + OpenRouter free-tier models.
**Why:** Three reasons: budget constraint, representativeness (most agentic shopping infrastructure runs on open-weight models), and product principle (a tool a merchant cannot afford to run is no tool at all). The unit economics story ($0 during hackathon, $5-8 at production scale) is itself a product differentiator.

### 4.6 Documentation-first, Day 1
**Considered:** Build first, document at the end.
**Chose:** Product Doc, Technical Doc, and Decision Log committed before any feature code.
**Why:** The rules state explicitly that submissions without both documents will not be evaluated regardless of code quality. Clearing the hard gate first costs nothing; it forces every architectural decision to be defended before it ossifies.

---

## 5. Scope Cuts

Every cut below is deliberate, not accidental. The principle: one bulletproof closed loop beats five half-loops.

| Cut | Why |
|---|---|
| Cross-merchant benchmarking | Requires a population of audited stores we do not yet have. Documented as v2. |
| Persistent monitoring / drift alerting | Adds notification surface area that distracts from proving the core diagnostic loop. |
| Multi-store accounts / SSO | Enterprise plumbing. The rubric does not reward it. |
| Shopify App Store distribution | Multi-week App Store review. Not a hackathon item. |
| Voice cloning for fix copy | In-context conditioning on transcript samples achieves ~80% of the outcome at 0% of the cost. |
| Auto-fix without merchant approval | Hard product decision, not a scope cut for time. Every fix shows a diff and requires explicit Apply. Auto-mutation against a live storefront without human-in-the-loop is the wrong product instinct. |
| Real third-party merchant recruitment | Deferred stretch. Architecture supports it unchanged. |

---

## 6. Tradeoffs

**Realism vs demo time.** Real LLM calls take 60-90 seconds for a sim run. We do not cut this. The visible network activity is the credibility signal.

**Calibrated honesty vs impressive-looking numbers.** The product visibly says "I don't know" when it should. This deflates one demo moment but establishes the entire product principle.

**Free-tier model swarm vs premium swarm coverage.** Llama, Qwen, GLM are not GPT-4. We label every column honestly and reframe: AI shopping agents in 2026 run on a diverse model ecosystem, and the long tail is open-weight. This frame is truer than testing only ChatGPT.

**Solo bandwidth vs ambition.** Cut order is locked: cut Replay Theater before Decision Tree Vault, cut both before the core loop, and never cut documentation or calibration. Discipline over ambition.

---

## 7. Success Criteria

This submission succeeds if:

1. Documentation gate cleared. Both Product Doc and Technical Doc present, sharp, scope cuts named, decisions defended. Decision Log has 26+ entries with atomic commits behind them.
2. Demo runs end-to-end live with no edits hiding failures. Real Shopify OAuth, real STT, real agent swarm, real Admin API mutation, real before/after delta.
3. A judge can navigate from a top gap to its source MerchantTruth and source AgentRepresentation in four clicks or fewer.
4. At least one gap surfaces with `dont_know` calibration during the demo and is not hidden.
5. The before/after delta on at least one fix is measured (not predicted) and matches its predicted range, with the calibration label visible.
6. Code, commits, and docs together would let a Kasparro engineer pick this up tomorrow.

---

## 8. Why This Beats Every Alternative

| Tool | What it does | What it misses |
|---|---|---|
| Shopify Magic / Sidekick | Generates copy on demand | No diagnostic, no agent simulation, no interview |
| Delphi.ai | Clones an expert for Q&A | Different product entirely; no commerce surface |
| Glean / Notion AI / RAG tools | RAG over existing documents | Cannot surface tacit knowledge never written down |
| Static AI-readiness scanners | Lint over existing copy | No ground truth from merchant, no multi-agent, no closed loop |
| Any single-LLM simulator | Shows one agent's view | Cannot detect ambiguity or compare across model families |

**Echomind Commerce is the only tool that combines:** tacit-knowledge interview, multi-agent simulation, calibrated diagnostic, and closed-loop fix-and-retest. No shipping product combines all four. No shipping product is even trying.

---

*Companion: `TECHNICAL_DOCUMENT.md` (architecture, failure handling, data model, calibration formula, cost model).*
*Full decision history: `docs/DECISION_LOG.md` (26+ entries).*
*Demo: `docs/DEMO_SCRIPT.md` and `docs/CINEMATIC_TRAILER.md`.*
