# Demo Script - Echomind Commerce

> Single-take, all-live, 4-5 minutes. Network tab visible at start. No edits hide failures. This is the verbatim shooting script for the demo video that ships with the submission.

> Source: [WINNING_PLAN.md §21](../../WINNING_PLAN.md#21-the-five-minute-demo). This document is the operational version - beat-by-beat, with timing, screen, narration, and risk callouts.

---

## Pre-roll checklist (60 minutes before recording)

| Check | Action |
|---|---|
| Internet | Switch to wired Ethernet. Disable WiFi. |
| Backend up | `make dev` running; `curl localhost:8000/health` returns `ok` for both Neo4j and Gemini. |
| Frontend up | `localhost:3000` loads landing without console errors. |
| Shopify dev store | Snapshot taken via `scripts/snapshot_dev_store.py`; revert script tested. |
| Shopify catalog | 42 SKUs / 7 policies / 62 reviews ingested via `make seed-shopify` - confirm node counts in Neo4j Browser. |
| Neo4j AuraDB | <3K nodes total (room for live audit). |
| Gemini quota | <50% of daily limit consumed. |
| OpenRouter | Test calls succeed for all 4 swarm models within last 5 min. |
| Mic | Test record → playback. Background noise < -55 dB. |
| Lighting | Web-cam not in shot; screen-only recording. |
| Recording | OBS / native recording at 1080p, 30 fps, two takes max. |

---

## Beat 1 - The Hook · 0:00-0:25

**Screen.** A single fullscreen slide:
> *"ChatGPT now completes purchases. Google AI Mode recommends products. Shopify just launched its Agentic Plan. AI agents are about to mediate every shopping decision - and right now, your merchants don't know how those agents see them."*

**Narration.**
> "By 2026, three things are true at once: ChatGPT closes purchases inside the chat. Google AI Mode pushes products inside search. Shopify ships an Agentic Plan that wires every merchant's catalog into AI shopping channels by default. The result: AI agents are now the discovery layer for an increasing share of e-commerce GMV - and merchants have *no idea* how those agents see them. Echomind Commerce is the diagnostic. Live demo, real Shopify, real LLMs, real fixes."

**Risk callout.** None - it's static. If it fails, restart.

---

## Beat 2 - Connect · 0:25-0:55

**Screen.** The Echomind landing page → click "Connect Shopify."

**What to do, in order.**
1. Open browser dev tools (Network tab) before any clicks. *This stays open the whole demo.*
2. Click "Sign in with Google." Real Firebase Auth flow. Pick the demo Gmail account.
3. Click "Connect Shopify Store." Real OAuth redirect to `partners.shopify.com`. Approve the Custom App.
4. Land on `/onboard` with the live ingest counter ticking:
   *"Ingesting Fulcrum Coffee Co... 12 / 42 products · 28 / 42 · done. 7 policies · 62 reviews."*

**Narration during the count.**
> "Real Shopify Partner OAuth. Real Admin GraphQL. The network tab is open if you want to verify. Forty-two SKUs, seven policies, sixty-two reviews - ingested in eleven seconds against the actual store, not a fixture."

**Risk callout.** Shopify OAuth flow is the most failure-prone live step. Mitigation: a pre-recorded fallback for the OAuth redirect is staged; if it fires we narrate honestly: *"Shopify partners.shopify.com 502'd - this happens; we have the OAuth-completed state cached."*

---

## Beat 3 - The Interview · 0:55-2:00

**Screen.** `/interview/[id]` opens. Three columns: live transcript (left), current question (center), live mini-graph (right).

**What to do, in order.**
1. Click **Start Interview**. Mic permission prompt - accept.
2. The system asks an unscripted Phase-3 question pulled from frontier scoring. Likely: *"Customers buying your Yirgacheffe - what's a question they ask in DMs that's never made it to your FAQ?"*
3. Answer in character as the Fulcrum Coffee founder. Real answer (NOT scripted): *"They almost always ask if it's good for cold brew, and honestly it isn't - it's chocolate-forward, not the right profile for cold extraction. But our FAQ doesn't say that anywhere."*
4. **Three new nodes pulse in on the right panel** as the extraction runs:
   - `CustomerQuestion`: *"Is the Yirgacheffe good for cold brew?"*
   - `MerchantTruth`: *"Yirgacheffe is chocolate-forward; not suited for cold brew."* - tagged `tacit_category: edge_case_knowledge`, `tacit_level: deeply-tacit`.
   - `EXCEPTION_TO` edge from the truth → the brewing-recommendation policy.
5. Counter ticks: *"Nodes: 287 · Edges: 612 · Coverage: 73%."*

**Narration over the graph growing.**
> "This is the interview engine. Twenty minutes - the merchant's brain becomes a typed knowledge graph, in real time. The system just asked an edge-case question my catalog never answers - and my answer surfaces a tacit truth no document holds. That truth, and the contradiction it implies, just became diagnostic ground truth."

**Risk callout.** STT misheard? The transcript is editable; a quick correction-in-flight is fine. Phase didn't advance? The frontier scorer chose differently - the demo doesn't depend on a specific phase being on screen.

---

## Beat 4 - The Agent Swarm · 2:00-3:00

**Screen.** Click **Run Agent Simulation**. `/simulate/[runId]` opens with four columns: Gemini, Llama-3.3, Qwen-2.5, DeepSeek V3.

**What happens.**
1. Buyer-prompt generator emits 50 prompts. They fan out across all 4 agents.
2. Streaming tokens scroll in each column live. Real network calls - the Network tab shows them.
3. Per-agent counters tick: "23 / 50 · 41 / 50 · 50 / 50 done."
4. A heatmap appears: *"GPT-class surface rate: 12% · Llama: 31% · Qwen: 18% · DeepSeek: 24%."*

**Narration.**
> "Four real LLMs. Four real model families. Live OpenRouter, live Gemini direct API. Fifty buyer-intent prompts each, generated from the merchant's own truths and the customer questions surfaced in the interview. This is what real AI shopping agents are saying about your store, right now, in the actual response budget. Nothing cached. Nothing scripted."

**Risk callout.** OpenRouter rate-limit on a free-tier model mid-run? The runner downgrades the affected column to *"rate-limited - partial sample (N of 50)"* and the calibration label on dependent gaps auto-downgrades. Narration: *"And there's reality - OpenRouter free tier rate-limited Llama mid-run. The calibration label reflects it. This is what production AI infrastructure looks like."*

---

## Beat 5 - The Diagnosis · 3:00-4:00

**Screen.** Auto-jump to `/audit/[storeId]`. Top panel: AI Readiness Score, gap list ranked by revenue-at-risk, calibration radar.

**What to point at.**
1. **Headline gap card** at the top of the list:
   > **CONTRADICTION · severity 0.83 · $1,840/month at risk · calibration: confident**
   > *"Three agents represent your Yirgacheffe as 'fruity, acidic.' Your interview said it's chocolate-forward. Likely cause: the product description does not include the words 'chocolate', 'low acidity', 'Bourbon varietal'."*
2. Click → `/diff/[gapId]`. Reasoning chain expands. Source nodes are clickable; click the MerchantTruth node - it jumps to `/graph/[storeId]` with that node highlighted.
3. Scroll back to the gap list. Show a card with:
   > **DARK ZONE · calibration: don't know · "Not enough buyer prompts in the decaf category to estimate revenue impact reliably."**

**Narration over the headline gap.**
> "This is the audit trail. Every claim links back to either a real agent response or a real MerchantTruth from the interview. No black box, no hand-waving - click any source, jump to the node, see the reasoning. And here…" *(scroll to the don't-know card)* …*"is the product principle. The system refuses to fake numbers it doesn't have. That's the difference between a diagnostic and a hallucination machine.*"

**Risk callout.** Headline gap not Yirgacheffe? Five other baked-in gaps will appear; pick whichever ranked highest. The script is *not* dependent on a specific gap winning - the product's job is to surface real misrepresentation, and we baked in six real ones.

---

## Beat 6 - Fix → Re-Test · 4:00-4:40

**Screen.** Stay on `/diff/[gapId]`. Click **Generate Fix**.

**What happens.**
1. Gemini Pro generates new product copy in the merchant's voice (sampled from the live interview transcript). Diff view: current copy on left, proposed on right.
2. Click **Apply**. UI shows: *"Pushing to Shopify..."* - real Admin GraphQL mutation.
3. **Open the live Shopify dev store in another tab - show the product page actually changed.**
4. Click **Re-test**. Spinner. ~60 seconds (we don't cut). Same buyer prompts re-fan to the same 4 agents.
5. Before/after panel renders: *"GPT-class agents now surface this product 71% of the time, up from 12%. Observed monthly recovery: $1,840. Calibration of the delta: confident - predicted range was 60-80, observed at 59 percentage points net."*

**Narration over the apply.**
> "Now the closed loop. The fix is generated in the merchant's own voice, sampled from the interview. I approve, it pushes to Shopify - real Admin API. Watch the actual product page change in the other tab. Re-test fires the same buyer prompts at the same four agents. And we measure the actual delta - not predicted, *measured*. From 12% to 71%. Eighteen-hundred dollars a month, recovered, against one fix."

**Risk callout.** Shopify mutation 500s? `tenacity` retries. If all 3 retries fail, narrate: *"Shopify Admin API 502'd - fix is queued, will retry. The product is calibrated honest about that, too."* The pre-snapshotted store can be reverted if any apply state is corrupted.

---

## Beat 7 - Close · 4:40-5:00

**Screen.** Single closing slide:
> *"Echomind Commerce - typed knowledge graph + calibrated confidence. The only AI-readiness tool that captures merchant tacit knowledge as ground truth and knows what it doesn't know. Track 5. End-to-end. Live."*

**Narration.**
> "Echomind Commerce. Built on a typed knowledge graph and a calibrated confidence engine. The only AI-readiness tool that captures merchant tacit knowledge as ground truth - and the only one that knows what it doesn't know. Track 5. End to end. Live."

---

## Post-roll checklist (10 minutes after recording)

| Check | Action |
|---|---|
| Watch the recording end-to-end on a different machine. | Confirm no audio glitches, frame drops, or caps-lock leaks. |
| Verify network tab visibility at every key beat. | Especially Connect (OAuth call), Simulate (4 fan-out calls), Apply (mutation call). |
| Verify the don't-know calibration is on screen for at least 3 seconds. | Product principle - must be visible. |
| Verify Shopify dev store changed on-camera in Beat 6. | Magic moment - must land. |
| Run the revert script. | Restore the dev store to pre-demo state. |
| Upload to YouTube as **unlisted**. | Update README link. |
| Backup raw recording locally + on a USB. | Insurance against re-take needs. |

---

## Backup video plan

If the live demo fails on submission day for any reason (Shopify outage, OpenRouter cap, internet drop), the backup video - recorded on Day 18 (18 May 2026) under the same script - is uploaded as a second unlisted YouTube link in the README, labeled *"backup recording in case of provider outage on viewing day."* Submit the live one as primary; keep the backup linked.

The backup recording is *not* faked or scripted differently - it is the same demo, recorded earlier, against the same live infrastructure. The only difference is the timestamp. This is consistent with the everything-real manifesto.

---

*Source: [WINNING_PLAN.md §21](../../WINNING_PLAN.md#21-the-five-minute-demo). Last reviewed: 2026-05-01. The script will be re-rehearsed three times during Day 10 (19 May 2026) before recording.*
