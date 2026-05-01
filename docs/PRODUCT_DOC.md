# Echomind Commerce - Product Document

> Track 5 · AI Representation Optimizer · Kasparro Agentic Commerce Hackathon
> Status: thinking document, not pitch. Decisions defended, scope cuts named.

---

## 1. Problem

In 2026, three things converged inside a single quarter: ChatGPT began completing purchases inside the chat surface, Google AI Mode started recommending products directly inside search, and Shopify launched its Agentic Plan to wire any merchant's catalog into AI shopping channels by default. This is the framing Kasparro itself opens the hackathon brief with - it is not our framing, it is the industry's.

The consequence: AI agents are now the discovery, comparison, and checkout layer for an increasing share of Shopify GMV. Those agents do not read the merchant's mind. They read what is written on the product page, in the FAQ, in the policy text, in the structured metadata. When that text is **incomplete, ambiguous, or contradictory**, the agent does one of two things - it skips the merchant entirely, or it surfaces a misrepresentation (a flavor profile that doesn't match, a use case the bean doesn't fit, a return policy that doesn't exist). Either outcome is a silent revenue leak the merchant never sees, because nobody is showing them how the agents see them.

The deeper problem is that the *most valuable* part of a merchant's brand - the tacit knowledge of who buys what and why, when policies bend, which products fail for which use cases - has historically never been written down. RAG-over-docs tools cannot extract knowledge that does not exist as a document. A static AI-readiness checklist cannot ask the questions the merchant has never been asked.

So the gap is structural: every AI-readiness tool shipping in 2026 will diagnose merchants against the documents the merchant already failed to write. None will diagnose them against the merchant's actual brain.

## 2. Target User

Shopify merchants in the **$100K-$5M annual revenue band**: 1-10 person teams, founder-led or merchandiser-led, with deep category expertise but zero in-house AI engineering. They are too small for a full agency engagement, too large to ignore the Agentic Plan rollout, and they already feel the leak - they just can't name it. Their domain expert is the bottleneck for everything (product copy, policy edge cases, FAQ content) and is permanently overcommitted, which is precisely why their tacit knowledge is undocumented.

Secondary user: the merchant's marketing or ops collaborator who consumes the audit and prosecutes the fixes. Tertiary user: Kasparro itself, because every customer of theirs is exactly this profile.

For the hackathon submission the real-world user is the builder - a real merchant Shopify dev store ("Fulcrum Coffee Co."), real catalog, real interview, real fixes pushed to a real store. The architecture supports a third-party merchant without changes; recruiting one is deferred stretch.

## 3. Core User Journey

1. **Connect.** Sign in with Google. Connect Shopify via real OAuth. Live counter ticks: products, policies, reviews ingested via real Admin GraphQL. (~5 min.)
2. **Interview.** A 20-minute AI-driven Socratic interview. Voice-first (Google STT V2 streaming). Five phases - brand mapping, product truths, customer reality, policy edge cases, trust signals. Frontier scoring picks the next-most-valuable question in real time. The typed knowledge graph grows live in the right pane; the merchant watches their own brain become a graph.
3. **Simulate.** Click run. Four real AI shopping agents (Gemini, Llama-3.3, Qwen-2.5, DeepSeek V3) receive 50-150 buyer-intent prompts in parallel. Streaming tokens visible per column. Outputs persist as `AgentRepresentation` nodes in the same graph as the interview.
4. **Diagnose.** A typed Gap Graph is computed by deterministic Cypher (candidate detection) + Gemini Pro (classification) + a calibrator (Echomind's 5-bucket confidence formula) + a parameterized revenue model. Each gap exposes a clickable reasoning trace back to source nodes. Gaps the system genuinely can't estimate are surfaced as "I don't know - needs more data," not faked.
5. **Fix.** One-click fix generation in the merchant's voice (sampled from the interview transcript). Diff view, edit, apply. Real Shopify Admin GraphQL mutation writes to the live store.
6. **Re-test.** Same buyer prompts that previously surfaced the gap re-run against the same four agents. Before/after delta is measured, not predicted. Calibration of the delta itself is shown.

The whole loop is replayable from a Firestore + Neo4j snapshot timeline. Nothing is staged.

## 4. Key Product Decisions

Each decision below has a defensible rejection - what we considered and chose against, and why.

**4.1 Multi-agent simulation across four model families (Gemini, Llama, Qwen, DeepSeek), not single-agent.**
Considered: a single GPT-class simulator. Rejected because the load-bearing insight is *comparison* - a merchant cannot be told "AI agents misread you" using one agent. They will, correctly, ask "which one?" Four families also matches the real 2026 agent ecosystem: ChatGPT and Google AI Mode are visible, but the long tail of Shopify Agentic Plan integrations and embedded retailer assistants runs predominantly on open-weight models for cost reasons. Testing across model families is *more* defensible than testing only ChatGPT.

**4.2 Tacit knowledge as ground truth, captured by a Socratic interview.**
Considered: RAG over the merchant's existing docs (faster to build, already a category). Rejected because every other AI-readiness tool in 2026 will be doing exactly that, and they will all fail on the same axis - they cannot extract knowledge the merchant never wrote down. Categories 4 (Intuitive Judgment), 5 (Edge Case Knowledge), and 6 (Meta-Knowledge) of our Tacit Knowledge Taxonomy are structurally inaccessible to RAG. The interview is the moat.

**4.3 Calibrated "I don't know" surfaced as first-class product output.**
Considered: always emitting a number with a confidence percentage attached. Rejected because diagnostic tools that overclaim are useless to the merchant (they're either ignored or trusted falsely, both bad). We adopt Echomind's 5-bucket calibration (`certain` / `confident` / `uncertain` / `low_confidence` / `dont_know`) and explicitly distinguish "I don't know" (no relevant nodes in subgraph) from "I'm uncertain" (nodes exist but sparse / contradictory). The "I don't know" label is shown in the demo, on purpose, even though it deflates one moment - because the credibility it buys is worth more than that moment.

**4.4 Closed-loop fix → real Shopify mutation → re-test, not a list of recommendations.**
Considered: produce a ranked PDF of issues and stop there (lower risk, faster build). Rejected because lists of problems are not products; deltas are. The merchant's question is not "what's wrong?" but "did fixing it help?" We push real Admin GraphQL mutations to the live dev store, then re-run the same buyer prompts against the same agents, and report the **measured** before/after surface-rate delta. If the delta underperforms the predicted range, that is also surfaced - not hidden.

**4.5 Free-tier-first architecture (Gemini direct + OpenRouter free tier + Neo4j AuraDB Free + Firebase Spark + Shopify Dev Store).**
Considered: paying for OpenAI/Anthropic to make the swarm "more impressive." Rejected for three reasons: (a) hackathon constraint of zero paid OpenAI/Anthropic credits; (b) it makes the cost-to-merchant story compelling - a tool a merchant cannot afford to run is no tool at all, and Kasparro builds commerce *infrastructure*, where unit economics are existential; (c) it forces us to design real failure handling for free-tier rate limits, which is itself a graded artifact in the rubric.

**4.6 Documentation-first Day 1, code Day 2+.**
Considered: build the obvious things on Day 1 and write docs at the end. Rejected because the rules state explicitly that submissions without both Product Doc and Technical Doc will not be evaluated regardless of code quality. Writing the docs first costs us nothing; it clears the hard gate before code exists, and forces us to defend every architectural decision before it ossifies. The Decision Log is committed one entry per commit on Day 1 - proof of thinking history.

**4.7 Local Docker Compose, not Cloud Run, for the hackathon.**
Considered: deploying to Cloud Run for a public URL. Rejected because the demo runs on a laptop, judges replicate via README, and a cloud deployment introduces DNS / IAM / cost surface area that contributes nothing to any rubric dimension. Cloud Run is documented as a v2 stretch in the Technical Doc. We don't take risks that don't pay rubric points.

## 5. Scope Cuts (what we did NOT build, and why)

**Cross-merchant benchmarking.** "You score 67/100 vs. category median 73/100" is compelling but requires a population of audited stores we don't yet have. Documented as v2.

**Persistent monitoring / drift alerting.** This is a one-shot audit, not a daemon. A scheduled re-audit cron is a 30-minute build but adds a retention surface (notifications, channels, thresholds) that distracts from closing the diagnostic loop end-to-end.

**Multi-store accounts / SSO / team roles.** A single merchant per session. The rubric does not reward enterprise plumbing; the demo would not show it.

**Shopify App Store distribution wrapper.** Submitting to the App Store is a multi-week review process unrelated to the diagnostic itself.

**Voice cloning for fix-copy generation.** We sample brand voice from the interview transcript and condition the LLM on it (good enough). True voice cloning is post-MVP.

**Auto-fix without merchant approval.** Hard product decision, not a scope cut for time. Every fix shows a diff and requires explicit "Apply." Auto-mutation against a live storefront without human-in-the-loop is the wrong product instinct, full stop.

**Multilingual agent simulation, PDF audit export, Replay Theater.** All elevation features (§19 in the plan). They are listed in priority order and pulled in only after the core loop passes the Day 8 acceptance test. Better one closed loop than five half-loops.

**Real third-party merchant recruitment.** Deferred stretch. The architecture supports it without changes; one merchant adds calendar coordination risk that Day 9 cannot absorb if anything else slips.

**The principle behind every cut:** 11 days, small team, one production-quality closed loop is worth more than five half-loops of breadth. Anything that does not directly serve the Connect → Interview → Simulate → Diagnose → Fix → Re-test path is cut until that path is bulletproof.

## 6. Tradeoffs

**Realism vs. demo time.** Real LLM calls take 60-90 seconds for a sim run. We do not cut. The visible network activity *is* the credibility signal - judges can see the streaming tokens, the OpenRouter latency, the Shopify mutation in the network tab. A faster fake demo would score worse, not better, against this rubric.

**Calibrated honesty vs. impressive-looking numbers.** The product visibly says "I don't know" when it should. This deflates one demo moment but buys the entire product principle. Our wager: judges who have seen 50 demos with fake confidence will reward the one demo that admits uncertainty.

**Free-tier model swarm vs. premium swarm coverage.** Llama, Qwen, DeepSeek are not GPT-5. We label every column honestly and reframe: AI shopping agents in 2026 run on a diverse model ecosystem, and the long tail is open-weight. This frame is *truer* than testing only ChatGPT, and it flatters the commerce-infrastructure thesis Kasparro is building against.

**Solo/small-team bandwidth vs. ambition.** The cut order is locked: cut Adversarial Buyer Mode, then Replay Theater, then Decision Tree Vault, before cutting any of {documentation, core loop, calibration, reasoning trace, before/after delta}. Discipline > ambition.

**Synthetic Fulcrum Coffee catalog vs. real merchant.** Rules permit synthetic Shopify product data. Our manifesto bans synthetic *infrastructure* - Shopify, Neo4j, LLMs, Firebase, the OAuth flow are all real. The products are fictional; nothing else is.

**"10,000 micro-questions" framing.** The blueprint occasionally talks about "10,000 questions" the system asks. Honest accounting: the actual count is **~5,000-8,000 LLM-mediated micro-queries per audit** (verbal Q&A 30-50, internal extraction prompts ~120, buyer-intent prompts 50-150, per-agent gap classification ~200, decision-tree decomposition ~80, contradiction probe ~40 - multiplied across documents and chunks). We name the real number in the Technical Doc rather than carry the larger one for marketing.

## 7. Success Criteria

This submission succeeds if, on judging, the following are true:

1. **Documentation gate is cleared.** Both Product Doc and Technical Doc present, sharp, scope cuts named, decisions defended. Decision Log ≥20 entries with atomic commits behind them.
2. **Demo runs end-to-end live with no edits hiding failures.** Real Shopify OAuth, real STT, real agent swarm, real Admin API mutation, real before/after delta. Network tab open at start.
3. **A judge can navigate from a top gap to its source MerchantTruth and source AgentRepresentation in ≤4 clicks.** The reasoning trace is the trust mechanism; if a judge cannot reach source nodes, the calibration claim is vapor.
4. **At least one gap surfaces with `dont_know` calibration during the demo and is not hidden.** This is the originality bet - calibrated honesty as product principle.
5. **The before/after delta on at least one fix is measured (not predicted) and matches its predicted range, with the calibration label visible.**
6. **Code, commits, and docs together would let a Kasparro engineer pick this up tomorrow.** The internship is the real prize per the rules; the artifact has to read as something a colleague produced.

If those six are true, the submission is a credible Track 5 finalist. Anything beyond is upside.

---

*Companion: `TECHNICAL_DOC.md` (architecture, AI/deterministic boundary, failure modes, data model, calibration formula, cost model, limitations).*
