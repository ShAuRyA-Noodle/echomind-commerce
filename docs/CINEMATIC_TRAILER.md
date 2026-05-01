# Cinematic Trailer Storyboard - Echomind Commerce

> 90-second cinematic backup video. Plays if the live demo fails on judging
> day. Also doubles as a Day 11 social/launch asset (Twitter, LinkedIn, the
> WhatsApp submission group).
>
> Source narrative: [DEMO_SCRIPT.md](DEMO_SCRIPT.md). This is the
> stripped, motion-heavy, no-dialogue cut.

---

## Spec

| Property | Value |
|---|---|
| Duration | 90 seconds (84-94 acceptable) |
| Resolution | 1920x1080, 30 fps |
| Format | MP4, h.264, AAC stereo audio |
| Aspect | 16:9 master, 1:1 + 9:16 social cuts post-launch |
| Audio | One ambient music track + occasional SFX. No voiceover. |
| Captions | Hard-coded white-on-black subtitles, ~22 px, center-bottom |
| File size target | <40 MB |
| Tools | OBS Studio for screen capture, DaVinci Resolve for cuts, royalty-free track from Pixabay or YouTube Audio Library |

---

## Three-act structure (30s + 35s + 25s)

### Act 1 - The Problem (0:00 to 0:30)

Punchy, cold open. No people, no faces. All screens.

| Time | Shot | Caption |
|---|---|---|
| 0:00-0:03 | Black screen, white text fades in: "AI agents now mediate every shopping decision." | none |
| 0:03-0:08 | Three logos animate in: ChatGPT, Google AI Mode, Shopify Agentic Plan. | "ChatGPT closes purchases. Google AI Mode recommends. Shopify ships agentic." |
| 0:08-0:14 | Quick cut: a typed buyer prompt appears in a faux ChatGPT interface, agent recommends a competitor's product. | "When agents misread your store..." |
| 0:14-0:22 | Whip-pan to a Shopify dashboard. Revenue chart dips. The merchant blinks. Static screenshot, no animation. | "...you lose revenue you never saw leak." |
| 0:22-0:30 | Hard cut to black. Echomind logo materializes. | "Echomind Commerce. Diagnose the leak." |

**Music**: Ambient build, low end, ominous. Pixabay search: "cinematic tension build."

### Act 2 - The Loop (0:30 to 1:05)

The product, in motion. No scrolling-narrator boredom. Each beat is one
action, max two seconds. Match cuts to the music's bass hits.

| Time | Shot | Caption |
|---|---|---|
| 0:30-0:33 | Real Shopify Partners OAuth screen. Click. Redirect. | "Connect Shopify, real OAuth." |
| 0:33-0:38 | The /onboard page, ingest counter ticking 0 to 42. | "42 SKUs, 7 policies, 62 reviews. Live ingest." |
| 0:38-0:46 | Speed-up cut of the /interview view. Graph nodes pulse in on the right panel. | "20-min Socratic interview. Tacit knowledge becomes a graph." |
| 0:46-0:54 | /simulate view. Four columns light up in sequence as agent_done events fire. | "Four real LLMs. Live OpenRouter calls." |
| 0:54-1:00 | /audit dashboard. Top gap card pulses in: "CONTRADICTION - severity 0.83 - $1,840 at risk." | "Diagnosed gaps. Calibrated confidence." |
| 1:00-1:05 | /diff page. Reasoning trace animates step-by-step. Source-node chips light up. Then a green "calibration: confident" badge slides up. | "Every claim links back to a source node." |

**Music**: Beat-driven percussion, builds to a peak at 1:05. Pixabay search:
"corporate motivation cinematic" or "tech logo reveal."

### Act 3 - The Loop Closes (1:05 to 1:30)

Resolution. The closed loop is the climax.

| Time | Shot | Caption |
|---|---|---|
| 1:05-1:10 | "Generate fix" button click. Gemini Pro types proposed copy on screen, character-by-character (use the macOS Quick Time text reveal effect). | "Fix proposed. Merchant voice preserved." |
| 1:10-1:14 | "Apply" click. Loading spinner. Cut to the live Shopify product page in a side-by-side: before / after. | "Real Shopify Admin GraphQL mutation." |
| 1:14-1:21 | /audit re-test panel: surface rate animation 12% to 71%. The number counts up. | "Same buyer prompts. Same agents. 12% -> 71%." |
| 1:21-1:25 | Screen splits into 4 quadrants showing: typed graph, four-agent simulation, gap deep-dive, before/after delta. | "Connect. Interview. Simulate. Diagnose. Fix. Re-test." |
| 1:25-1:30 | Echomind logo. Tagline. URL. | "echomind. orange-kid. github.com/ShAuRyA-Noodle/Orange-Kid" |

**Music**: Climactic resolution. Last beat lands on the URL frame.

---

## Production checklist

| Item | Status |
|---|---|
| OBS scenes pre-built (one per page: /onboard, /interview, /simulate, /audit, /diff) | Day 10 |
| Recording at 1920x1080, 30 fps, max bitrate, high-quality audio | Day 10 |
| Speed ramps applied in DaVinci Resolve (0.4x for graph-grow, 2.0x for ingest counter) | Day 10 |
| Captions hard-coded (not soft subtitles) so social platforms render them | Day 10 |
| Background music chosen and downloaded (Pixabay or YouTube Audio Library, royalty-free) | Day 10 |
| Logo + URL frames pre-rendered as PNG, comped in DaVinci | Day 10 |
| Backup audio mix without music (in case of platform copyright flag) | Day 10 |
| Master upload to YouTube unlisted, link in README and submission form | Day 11 |
| 1:1 cut for Twitter, 9:16 cut for Instagram Reels (post-submission, not pre) | Day 12+ |

---

## Voiceless on purpose

The trailer has no voiceover. Reasons:

1. **Trust signal**: a polished, captioned video looks more produced than
   a narrated walkthrough.
2. **Multilingual reach**: the WhatsApp submission group probably mixes
   English/Hindi/Tamil readers - captions translate; voice does not.
3. **Re-recording resilience**: voice take retakes blow our day-10 budget;
   captions are typeable in 5 minutes.

The full DEMO_SCRIPT.md narration version is the primary submission. The
trailer is the backup + the social asset.

---

## Hard rules

- **No em dashes in captions.** CI on the repo enforces this; the trailer
  follows the same rule.
- **No fake data.** Every screen capture comes from a real run against the
  live Shopify dev store + real OpenRouter swarm + real Neo4j graph.
- **No scripted "aha" moments.** The Yirgacheffe contradiction is captured
  during a real interview turn; if a different gap surfaces highest, that
  one stars in the trailer instead.

---

## Day 11 launch sequence

1. Submit primary demo video link (full DEMO_SCRIPT.md walkthrough).
2. Append cinematic trailer as a secondary unlisted YouTube link in the
   README, labeled "in case of provider outage on viewing day."
3. Tweet the trailer with the GitHub URL. One star before submission >
   zero stars.
4. Post to the WhatsApp submission group with the live URL + the
   trailer link. Quiet, no marketing pitch, just two links and "Track 5
   submission - Echomind Commerce."

---

*Source: this storyboard derives from [DEMO_SCRIPT.md](DEMO_SCRIPT.md) and
[WINNING_PLAN.md](../../WINNING_PLAN.md) section 21. Last reviewed:
2026-05-01. Trailer recording on Day 10 of the build window (2026-05-19).*
