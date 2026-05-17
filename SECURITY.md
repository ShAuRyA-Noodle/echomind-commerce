# Security & Privacy - Echomind Commerce

> Companion to [docs/PRODUCT_DOC.md](docs/PRODUCT_DOC.md) and [docs/TECHNICAL_DOC.md](docs/TECHNICAL_DOC.md). This document is the privacy / IP / liability story we'd hand a merchant on day one. It also pre-empts the obvious judge questions.

---

## 1. What data flows through Echomind Commerce

| Data class | Source | Stored where | Purpose |
|---|---|---|---|
| Shopify catalog (products, policies, reviews) | Shopify Admin GraphQL - read with the merchant's app token | Neo4j (graph nodes) + Firestore (raw blobs) | Diagnostic substrate; agent simulation context |
| Merchant interview audio | Browser microphone, streamed live | Firebase Cloud Storage (only if recording is enabled - opt-in) | Optional transcript replay; deletable any time |
| Merchant interview transcript | Google STT V2 streaming | Firestore | Source of MerchantTruth nodes; audit trail |
| Tacit knowledge nodes (MerchantTruth, Decision, Pattern, etc.) | Gemini Flash extraction over the transcript | Neo4j | The diagnostic ground truth |
| Buyer-intent prompts | Gemini Flash generation | Neo4j + Firestore | Agent simulator inputs |
| Agent representation outputs | Live calls to Gemini direct + OpenRouter (Llama, Qwen, DeepSeek) | Neo4j + Firestore | The diagnostic comparison set |
| Gap classifications & calibration metadata | Gemini Pro judge | Neo4j | The diagnostic outputs |
| Fix copy generations | Gemini Pro | Firestore (until merchant approves & applies) | Proposed fixes - never auto-applied |
| Fix application records | Shopify Admin GraphQL mutations | Shopify (the live store) + Firestore changelog | Auditable history of changes pushed to the store |

**No personal customer data is ingested.** Reviews are public storefront content. The interview captures the *merchant's* tacit knowledge, not customer PII.

## 2. Authentication & access control

- **Authentication.** Firebase Auth with Google Sign-In is the only identity model. Sessions are short-lived (1 hour) and refreshed via Firebase's standard refresh-token flow.
- **Backend trust boundary.** Every authenticated request from the frontend carries a Firebase ID token; the FastAPI middleware verifies the token via the Firebase Admin SDK before any route handler runs.
- **Shopify token storage.** The merchant's Admin API access token is stored in Firestore under a per-merchant document, encrypted at rest by Google's default Firestore encryption. It is never exposed to the frontend and is read only when an audit-pipeline service needs it server-side.
- **No multi-tenant data sharing.** The MVP is single-merchant per session; the data model carries explicit merchant scoping on every node.
- **Firestore security rules.** Test mode during development; **tightened to per-merchant + auth-required rules before submission** (Decision Log #23). The submission checklist gates this.

## 3. Data lifecycle & merchant control

The merchant owns and controls every artifact:

- **Right to view.** The full graph, every transcript chunk, every agent response, and every fix proposal are visible in the UI and exportable as a PDF audit report.
- **Right to edit.** The Living Update Loop ([WINNING_PLAN.md §12](../WINNING_PLAN.md#12-living-update-loop)) lets the merchant correct any extracted MerchantTruth, dismiss any gap, and rate any fix. Corrections trigger re-extraction.
- **Right to delete.** Any audit can be deleted; deletion cascades through Neo4j (all merchant-scoped nodes), Firestore (transcripts, runs, change log), and Cloud Storage (audio, exports). Deletion is irreversible and visible in the changelog as a tombstone entry until the changelog itself is purged.
- **Right to export.** Every audit is exportable as a single JSON document containing the full graph, every transcript turn, every agent run, and every fix decision.

## 4. IP ownership

- **The merchant owns their graph.** The MerchantTruth nodes, the Decision trees, the gap diagnoses - all of it is the merchant's data. Echomind Commerce is the processor, not the controller.
- **The merchant owns the proposed fix copy.** Generated copy is conditioned on the merchant's own voice samples; it is theirs to apply, edit, or discard.
- **Echomind Commerce retains rights to anonymized, aggregated metrics** for product improvement (e.g., "across N audits, Llama-class agents misrepresent return policies 23% of the time"). No merchant-identifiable content leaves the per-merchant scope.
- **Open-source code is MIT-licensed** ([LICENSE](LICENSE)). The codebase itself is freely redistributable; the merchant's data is not.

## 5. Liability boundaries

- **Echomind Commerce never auto-applies fixes.** Every Shopify mutation requires explicit merchant approval. There is no "auto-pilot" mode. This is a deliberate product decision (PRODUCT_DOC §5).
- **The diagnostic does not claim numerical calibration accuracy.** We claim auditable 5-bucket *labels* (`certain` / `confident` / `uncertain` / `low_confidence` / `dont_know`), not calibrated probabilities. Merchants are told this in plain language under every gap card.
- **Agent simulator outputs are fair-test simulations, not legal characterizations of any provider.** OpenRouter rate limits and provider-side prompt drift are reflected in the calibration label, never hidden.

## 6. Free-tier-first cost surface

The architecture runs on free tiers (Gemini direct, OpenRouter `:free`, Neo4j AuraDB Free, Firebase Spark, Shopify Dev Store). This is a **deliberate** product choice (Decision Log #4): a tool a merchant cannot afford to run is no tool at all. Production unit economics ($5-8/audit) are documented in TECHNICAL_DOC §9.

## 7. Vulnerability disclosure

If you discover a security issue:

1. **Do not** post it publicly.
2. Email **shauryapunj404@gmail.com** with subject `[ORANGE-KID SECURITY] <brief description>`, or open a private security advisory via GitHub's *Security › Report a vulnerability* on this repo.
3. Provide reproduction steps + impact assessment + suggested mitigation.

You will receive an acknowledgement within 48 hours. Critical issues are aimed for a patch within 7 days.

## 8. What's explicitly out of scope for the hackathon submission

- **Multi-region storage / data-residency.** Buckets are `us-east1` (Decision Log #24) - `asia-south1` would force a paid tier.
- **HIPAA / SOC 2 / GDPR posture.** Not a regulated commerce category in the hackathon; documented in WINNING_PLAN as a v2 concern.
- **Rate-limiting per merchant.** The MVP is single-merchant; production would need per-tenant rate limits.
- **Encryption above Google's default at-rest.** No envelope encryption or BYOK; this is hackathon scope, not production.
- **Penetration testing report.** None done; explicitly out of scope.

## 9. The single biggest privacy-design choice

**The merchant's tacit knowledge is captured by Socratic interview, not by mining customer data.** Every other AI-readiness tool in 2026 will read shopper-side analytics, customer support tickets, or session logs to infer merchant intent. We don't. We ask the merchant. The privacy footprint is dramatically smaller as a result, and the merchant retains primary authorship of every truth in their own diagnostic.

---

*Last reviewed: 2026-05-01. This document evolves with the product; entries from build days will be appended in [CHANGELOG.md](CHANGELOG.md).*
