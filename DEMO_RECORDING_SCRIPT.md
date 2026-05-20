# Demo Recording Script

**Target:** 4-5 minutes, single take, all live, network tab visible throughout.
**Setup:** localhost:8000 backend, localhost:3000 frontend. Neo4j populated, Shopify catalog seeded.

---

## Pre-recording checklist (do this 30 minutes before hitting Record)

- [ ] `docker compose up` or manual backend + frontend running
- [ ] `curl localhost:8000/health` returns `"status": "ok"` for both neo4j and gemini
- [ ] `http://localhost:3000` loads without console errors
- [ ] Shopify catalog seeded: `python3 scripts/import_to_shopify.py`
- [ ] Neo4j has < 3K nodes (clear if needed: `MATCH (n) DETACH DELETE n`)
- [ ] Gemini quota < 50% of daily limit
- [ ] OpenRouter: ping test passes for all 4 models (`GET /api/debug/swarm`)
- [ ] Mic: test record/playback, background noise < -55dB
- [ ] Open browser DevTools (Network tab) BEFORE starting to record
- [ ] OBS or Quicktime: 1080p, 30fps, two-take budget

---

## BEAT 1: The Hook (0:00 - 0:20)

**Screen:** One fullscreen black slide, white text fades in.

**Narrate:**
> "By 2026, three things happened at once: ChatGPT began completing purchases inside the chat. Google AI Mode started recommending products inside search. Shopify launched its Agentic Plan. AI agents are now the discovery layer for a growing share of Shopify revenue, and right now, merchants have no way to see how those agents see their stores. Echomind Commerce is the diagnostic. Everything you are about to see is real."

---

## BEAT 2: Connect (0:20 - 0:50)

**Screen:** Open http://localhost:3000/onboard

**Do this, in order:**
1. Show the Network tab is open (point to it).
2. Click **Run ingest** button. Watch the real Admin GraphQL call fire in the network tab.
3. Wait for the counter: "42 products, 7 policies, 62 reviews."

**Narrate:**
> "Real Shopify Admin GraphQL. Real products, real policies, real reviews, crawled from a live dev store. The network tab is open. Forty-two SKUs ingested, all typed into Neo4j nodes."

---

## BEAT 3: The Interview (0:50 - 2:00)

**Screen:** Navigate to http://localhost:3000/interview/session-001

**Do this:**
1. Click **Start interview**. The system generates the first Socratic question.
2. Click **Start mic** (or use text fallback).
3. Answer this question naturally as a coffee merchant. Suggested answer:
   > "They ask me in DMs all the time if the Yirgacheffe is good for cold brew. And honestly it is not. It is chocolate-forward, which is not the right profile for cold extraction. But our FAQ says nothing about that."
4. Watch the mini-graph on the right: **three nodes pulse in.**
   - CustomerQuestion: "Is the Yirgacheffe good for cold brew?"
   - MerchantTruth: "Yirgacheffe is chocolate-forward, not suited for cold brew."
   - EXCEPTION_TO edge
5. Click **Next question** once to show the system advancing.

**Narrate:**
> "The interview engine asks questions a catalog never answers - and each answer types tacit knowledge into the graph in real time. Watch the right panel. Three new nodes just entered the graph from one answer. That MerchantTruth, tagged as edge_case_knowledge and deeply-tacit, is now the diagnostic ground truth. It is knowledge no document held before this conversation."

---

## BEAT 4: The Agent Swarm (2:00 - 3:00)

**Screen:** Navigate to http://localhost:3000/simulate/run-001

**Do this:**
1. Set n_prompts to 8, check demo mode.
2. Click **Run swarm**.
3. Watch the four columns light up: gpt_oss, llama, qwen, glm.
4. Show the network tab firing live OpenRouter API calls.
5. Wait for "run complete" - approximately 30-40 seconds.

**Narrate:**
> "Four real LLMs. GPT-OSS 120B, Llama 3.3 70B, Qwen3 80B, GLM-4.5 Air. Thirty-two real API calls to OpenRouter, live. Every buyer prompt generated from the merchant's own knowledge. Watch the network tab. These are not cached responses. Each column is a different model family showing how it represents this store."

---

## BEAT 5: The Diagnosis (3:00 - 4:00)

**Screen:** Navigate to http://localhost:3000/audit/fulcrum-coffee-co

**Do this:**
1. Show the AI Readiness Score.
2. Point to the top gap card: the Yirgacheffe contradiction.
3. Click it to go to the diff page.
4. Watch the ReasoningTrace animation play (4 steps, each citing source nodes).
5. Click one source-node chip - it jumps to the graph view.
6. Come back to the audit page.
7. Scroll to show a gap with **"Don't know"** calibration label. Point to it explicitly.

**Narrate:**
> "Every gap links back to a real source: either a verbatim agent response or a MerchantTruth from the interview. Click any source node and you jump to it in the graph. Nothing is asserted without a citation. And here... the product principle. This gap has a dont_know calibration label. Not enough buyer prompts in the decaf category to estimate revenue impact. The system refuses to fake a number it does not have. That is the difference between a diagnostic and a hallucination machine."

---

## BEAT 6: Fix and Re-test (4:00 - 4:50)

**Screen:** Stay on the diff page for the Yirgacheffe contradiction.

**Do this:**
1. Show the proposed fix copy in the textarea (Gemini Pro generated it, conditioned on merchant voice).
2. Optionally edit it slightly to show it is editable.
3. Discuss what Apply would do: "This would push a real Shopify Admin GraphQL mutation to the live product page."
   - If catalog is seeded AND you want to show live mutation: click Apply, open the Shopify admin page in another tab, show the product page changed.
   - If not: narrate the flow without clicking.
4. Describe the re-test: "The same buyer prompts re-run against the same four agents. We measure the actual before/after surface rate delta."

**Narrate:**
> "The fix is generated in the merchant's voice, sampled from the interview transcript. One click pushes a real Shopify Admin API mutation. The product page changes in the live store. Then the same buyer prompts that previously surfaced this gap re-run against the same four agents, and we report the measured delta, not the predicted one. If the prediction misses, that too is surfaced, not hidden."

---

## BEAT 7: Close (4:50 - 5:00)

**Screen:** Cut to the graph view showing 200+ nodes, force-directed.

**Narrate:**
> "Echomind Commerce. Interview the merchant. Simulate four real AI agents. Diagnose the gaps with calibrated confidence. Fix. Re-test. Measure the delta. Everything real. Nothing synthetic. Nothing cached. Track 5."

---

## Risk callouts

| Situation | What to do |
|---|---|
| Shopify Admin API 502 | Narrate honestly: "Shopify rate-limited, this is real-world infrastructure" |
| OpenRouter rate-limit mid-run | Narrate: "One slot got rate-limited, calibration auto-downgraded, this is product behavior" |
| Web Speech API misheard | Correct in the transcript pane, hit Re-extract, continue |
| Phase did not advance as expected | Fine. Frontier scorer chose differently. Demo does not depend on a specific phase. |
| Backend 500 error | Show the /api/debug/health endpoint response. Explain. Do not hide it. |
| Demo crashes entirely | Use backup recording from Day 10 (19 May). |

---

## After recording

- [ ] Watch end-to-end on a separate device. Confirm: Network tab visible at key beats, `dont_know` calibration on screen for at least 3 seconds, graph nodes visibly pulsing during interview.
- [ ] Upload to YouTube as unlisted.
- [ ] Add URL to README and submission form.
- [ ] Save raw file to two locations.
- [ ] Run the revert script on the dev store: `python3 scripts/import_to_shopify.py --reset` (if product descriptions were modified).
