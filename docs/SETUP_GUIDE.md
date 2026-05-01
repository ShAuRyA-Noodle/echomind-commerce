# Echomind Commerce - Setup Guide

End-to-end replication walkthrough for the Echomind Commerce dev environment on macOS. Resumes from the point where you have already completed:

- Shopify Partner account + dev store at `fulcrum-coffee-co.myshopify.com`
- Neo4j AuraDB Free instance provisioned
- Firebase project `echomind699` with Web App registered, Auth enabled (Google sign-in), Firestore provisioned
- Gemini API key
- OpenRouter key (deferred, paste when ready)

The remaining steps below get you to a fully wired `.env` and a green smoke test.

---

## A. Shopify Custom App + Admin API token

The Admin API token is the long-lived credential the backend uses to read/write products, themes, content, orders, customers, metaobjects, locales, and inventory in your dev store. We use the long-lived token route (not OAuth) because this is a hackathon - no app distribution, no rotating tokens.

### A.1 Open the dev-store custom-apps page

Visit:

```
https://admin.shopify.com/store/fulcrum-coffee-co/settings/apps/development
```

### A.2 Enable custom-app development (first time only)

If you see a banner / button labeled **"Allow custom app development"**, click it, then **Allow custom app development** again on the confirm modal. Shopify will warn you that custom apps can access store data - that's expected.

### A.3 Create the app

1. Click **Create an app** (top-right).
2. App name: `Echomind Commerce Dev`
3. App developer / API contact email: your email (`workwithshaurya10@gmail.com`).
4. Click **Create app**.

### A.4 Configure Admin API access scopes

1. In the new app, go to the **Configuration** tab.
2. Under **Admin API access scopes**, click **Edit**.
3. Tick exactly the following scopes (use the search box per scope to find them quickly):

   - `read_products`
   - `write_products`
   - `read_content`
   - `write_content`
   - `read_themes`
   - `write_themes`
   - `read_orders`
   - `read_customers`
   - `read_metaobjects`
   - `write_metaobjects`
   - `read_locales`
   - `read_inventory`
   - `write_inventory`

4. Leave **Storefront API access scopes** empty for now - we configure those in step **B**.
5. Click **Save**.

### A.5 Install the app and copy the Admin token

1. Go to the **API credentials** tab.
2. Click **Install app** (top-right) → **Install** on the confirm modal.
3. Under **Admin API access token**, click **Reveal token once**. The token starts with `shpat_...`.
4. Copy it immediately - Shopify only shows it once.
5. Paste into `echomind-commerce/.env`:

   ```env
   SHOPIFY_STORE_DOMAIN=fulcrum-coffee-co.myshopify.com
   SHOPIFY_ADMIN_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### A.6 What to ignore

The same API credentials page shows an **API key**, **API secret key**, and **Webhook signing secret**. You can ignore all three for the hackathon. They are only required if you go the OAuth distribution route or sign incoming webhooks. We use the long-lived Admin token for simplicity.

---

## B. Storefront API token (buyer-side simulation)

The Storefront API token is a separate, public-safe token used by the buyer-side simulator to query the storefront the same way a real shopper's browser would.

### B.1 Configure Storefront scopes

1. Same custom app → **Configuration** tab.
2. Scroll to **Storefront API access scopes** → **Edit**.
3. Enable:

   - `unauthenticated_read_product_listings`
   - `unauthenticated_read_product_inventory`
   - `unauthenticated_read_product_pickup_locations`
   - `unauthenticated_read_metaobjects`
   - `unauthenticated_read_content`

4. Click **Save**.

### B.2 Re-install / install Storefront and copy token

1. Go to the **API credentials** tab.
2. If a button says **Install app** again (because you changed scopes), click it. Otherwise scroll to **Storefront API access tokens** → **Install app** / **Reveal token**.
3. Copy the **Storefront API access token**.
4. Paste into `.env`:

   ```env
   SHOPIFY_STOREFRONT_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

## C. Firebase Storage error troubleshooting

If clicking **Get started** on Firebase Console → **Storage** throws an error, run through the causes below in order. The first one resolves >90% of cases.

### C.1 (Most likely) Cloud Storage API is not enabled

As of late 2024, new Firebase projects no longer auto-enable the Cloud Storage API. You must enable it directly in the Google Cloud Console first.

1. Visit:

   ```
   https://console.cloud.google.com/apis/library/storage.googleapis.com?project=echomind699
   ```

2. Click **Enable**.
3. Wait ~30 seconds for propagation.
4. Return to Firebase Console → Storage → click **Get started** again.

### C.2 Upgraded Storage Terms not accepted

Firebase Storage rolled out new terms for Spark plan in some regions. The Console sometimes silently fails the first time.

1. Hard-reload the Firebase Storage page (`Cmd+Shift+R`).
2. If a **Get started** modal with new ToS appears, accept it.
3. Retry.

### C.3 Org policies blocking bucket creation

Rare on personal Google accounts (you're using `workwithshaurya10@gmail.com`, so this almost certainly does not apply). Skip unless the error message explicitly mentions an org policy.

### C.4 Default bucket already exists in GCS but is unlinked

Sometimes a half-completed earlier attempt leaves an orphan GCS bucket that Firebase refuses to recreate.

1. Visit:

   ```
   https://console.cloud.google.com/storage/browser?project=echomind699
   ```

2. If a bucket named `echomind699.firebasestorage.app` (or `echomind699.appspot.com`) already exists, leave it.
3. Return to Firebase Console → Storage → **Get started**. It should now detect and link the existing bucket.

### C.5 Last resort - skip Storage

Audio recording / playback is a stretch goal, not core. If none of the above unblock you:

1. Leave the Firebase Storage step incomplete.
2. Leave any `STORAGE_BUCKET=` line in `.env` as-is (or comment it out).
3. We revisit Storage on Day 9 per `WINNING_PLAN.md`. Onboarding, RAG, and the recommendation engine all work without it.

---

## D. Firebase Admin SDK service account JSON

The backend uses Firebase Admin SDK to verify Auth tokens, write Firestore, and (later) issue signed Storage URLs. This same JSON also powers Google Cloud Speech-to-Text (step **E**) since both sit under the `echomind699` project.

1. Firebase Console → click the **gear icon** next to "Project Overview" → **Project settings**.
2. Click the **Service accounts** tab.
3. Confirm the **Firebase Admin SDK** service account is selected.
4. Click **Generate new private key** → confirm on the modal. A JSON file downloads.
5. Move/rename it to:

   ```
   /Users/shauryapunj/Desktop/Echomind/echomind-commerce/firebase-admin-credentials.json
   ```

   This path is already in `.gitignore`. Do **not** commit it.

6. `.env` already contains:

   ```env
   GOOGLE_APPLICATION_CREDENTIALS=./firebase-admin-credentials.json
   ```

   No further config needed - Google client libraries auto-pick this up.

---

## E. Google Cloud Speech-to-Text V2 API enablement

Required for the live voice interview during seller onboarding.

1. Visit:

   ```
   https://console.cloud.google.com/apis/library/speech.googleapis.com?project=echomind699
   ```

2. Click **Enable**.
3. No new credentials needed - the Firebase Admin SDK service account JSON from step **D** is reused. Same project, same service account, same JSON.

---

## F. OpenRouter quick test

Once you paste your OpenRouter key into `.env`:

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Source the env and hit the models endpoint:

```bash
set -a && source echomind-commerce/.env && set +a
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  | python -m json.tool | head -30
```

You should see a JSON list of model entries (`id`, `name`, `pricing`, ...). If you get `401`, the key is wrong. If you get an empty body, check the network.

---

## G. Neo4j AuraDB connection test

Pull your AuraDB URI and password from the credentials file Neo4j made you download when you created the instance. The URI looks like `neo4j+s://<id>.databases.neo4j.io`, and the username is the same as the instance ID.

`.env`:

```env
NEO4J_URI=neo4j+s://69ebb282.databases.neo4j.io
NEO4J_USER=69ebb282
NEO4J_PASSWORD=<paste from AuraDB download>
```

Quick sanity test:

```bash
pip install neo4j
python - <<'PY'
from neo4j import GraphDatabase
import os
driver = GraphDatabase.driver(
    "neo4j+s://69ebb282.databases.neo4j.io",
    auth=("69ebb282", "<PASSWORD>"),
)
driver.verify_connectivity()
print("Neo4j OK")
PY
```

Expected output: `Neo4j OK`. If you get an auth error, re-copy the password - Aura passwords contain easily-confused characters. If you get a DNS / TLS error, your network blocks `neo4j+s://`; try a hotspot.

---

## H. Final `.env` checklist

Before moving on, your `.env` should have non-empty values for:

- [ ] `SHOPIFY_STORE_DOMAIN`
- [ ] `SHOPIFY_ADMIN_ACCESS_TOKEN` (starts with `shpat_`)
- [ ] `SHOPIFY_STOREFRONT_ACCESS_TOKEN`
- [ ] `FIREBASE_PROJECT_ID=echomind699`
- [ ] `GOOGLE_APPLICATION_CREDENTIALS=./firebase-admin-credentials.json`
- [ ] `GEMINI_API_KEY`
- [ ] `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- [ ] `OPENROUTER_API_KEY` (can be deferred)
- [ ] Firebase Storage env (optional - Day 9)

When all green, proceed to `JUDGE_REPLICATION.md` to verify the smoke tests pass.
