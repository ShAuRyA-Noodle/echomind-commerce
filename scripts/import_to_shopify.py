#!/usr/bin/env python3
"""
Fulcrum Coffee Co - Shopify bulk import.

Reads:
  - fulcrum-catalog.json   (42 products)
  - fulcrum-policies.json  (7 policies / pages)
  - fulcrum-reviews.json   (60+ reviews, stored as a product metafield list)

Pushes everything to a Shopify dev store via the Admin GraphQL API
(2024-10). Idempotent: skips products whose handle already exists,
upserts pages by handle, and upserts the reviews metafield per product.

Required env vars:
  SHOPIFY_STORE_DOMAIN          e.g. fulcrum-coffee-co.myshopify.com
  SHOPIFY_ADMIN_ACCESS_TOKEN    private app / custom app admin token

Usage:
  python import_to_shopify.py [--dry-run] [--only products|policies|reviews]
                              [--catalog PATH] [--policies PATH] [--reviews PATH]

Notes:
  - Reviews are stored under metafield namespace "fulcrum_reviews" key "items"
    (type: json) on each product. This is intentional: most Shopify dev stores
    won't have a third-party reviews app installed, and metafields give us a
    single round-trip storage model the audit pipeline can read directly.
  - Pages of type "policy" are mapped to Shopify shop policies (shippingPolicy,
    refundPolicy, privacyPolicy, termsOfService); other entries are created as
    Online Store pages.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

API_VERSION = "2024-10"
SCRIPT_DIR = Path(__file__).resolve().parent

LOG = logging.getLogger("fulcrum.import")


# ---------------------------------------------------------------------------
# GraphQL client
# ---------------------------------------------------------------------------

class ShopifyClient:
    """Thin Admin GraphQL client with retry on 429 / transient errors."""

    def __init__(self, domain: str, token: str, dry_run: bool = False):
        if not domain:
            raise ValueError("SHOPIFY_STORE_DOMAIN is required")
        if not token and not dry_run:
            raise ValueError("SHOPIFY_ADMIN_ACCESS_TOKEN is required")
        self.endpoint = f"https://{domain}/admin/api/{API_VERSION}/graphql.json"
        self.dry_run = dry_run
        self._client = httpx.Client(
            timeout=30.0,
            headers={
                "X-Shopify-Access-Token": token or "DRY_RUN",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    def close(self) -> None:
        self._client.close()

    def query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.dry_run:
            LOG.debug("[dry-run] would call: %s", _first_line(query))
            return {"data": {}, "_dry_run": True}

        payload = {"query": query, "variables": variables or {}}
        backoff = 1.0
        for attempt in range(5):
            try:
                resp = self._client.post(self.endpoint, json=payload)
            except httpx.RequestError as exc:
                LOG.warning("network error (%s); retry %d", exc, attempt + 1)
                time.sleep(backoff)
                backoff *= 2
                continue

            if resp.status_code == 429:
                wait = float(resp.headers.get("Retry-After", backoff))
                LOG.info("rate limited; sleeping %.1fs", wait)
                time.sleep(wait)
                backoff *= 2
                continue
            if resp.status_code >= 500:
                LOG.warning("server %s; retry %d", resp.status_code, attempt + 1)
                time.sleep(backoff)
                backoff *= 2
                continue

            try:
                body = resp.json()
            except ValueError:
                raise RuntimeError(f"non-JSON response (HTTP {resp.status_code}): {resp.text[:200]}")

            if "errors" in body and body["errors"]:
                raise RuntimeError(f"GraphQL error: {body['errors']}")
            return body

        raise RuntimeError("Shopify request exhausted retries")


def _first_line(s: str) -> str:
    for line in s.splitlines():
        line = line.strip()
        if line:
            return line[:80]
    return ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return json.load(f)


def find_product_by_handle(client: ShopifyClient, handle: str) -> str | None:
    q = """
    query findProduct($handle: String!) {
      productByHandle(handle: $handle) { id }
    }
    """
    res = client.query(q, {"handle": handle})
    if client.dry_run:
        return None
    node = (res.get("data") or {}).get("productByHandle")
    return node["id"] if node else None


def find_page_by_handle(client: ShopifyClient, handle: str) -> str | None:
    """Best-effort lookup using the pages REST-style query in GQL.

    Online Store pages don't have a direct byHandle query in older API
    versions; we list pages with a query filter instead.
    """
    q = """
    query findPage($q: String!) {
      pages(first: 5, query: $q) {
        edges { node { id handle } }
      }
    }
    """
    res = client.query(q, {"q": f"handle:{handle}"})
    if client.dry_run:
        return None
    edges = ((res.get("data") or {}).get("pages") or {}).get("edges") or []
    for edge in edges:
        node = edge.get("node") or {}
        if node.get("handle") == handle:
            return node["id"]
    return None


# ---------------------------------------------------------------------------
# Product import
# ---------------------------------------------------------------------------

PRODUCT_CREATE = """
mutation productCreate($input: ProductInput!, $media: [CreateMediaInput!]) {
  productCreate(input: $input, media: $media) {
    product { id handle title }
    userErrors { field message }
  }
}
"""

PRODUCT_VARIANTS_BULK_CREATE = """
mutation variantsBulkCreate($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkCreate(productId: $productId, variants: $variants) {
    productVariants { id title sku }
    userErrors { field message }
  }
}
"""

METAFIELDS_SET = """
mutation metafieldsSet($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { key namespace }
    userErrors { field message }
  }
}
"""


def build_product_input(p: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Map our catalog JSON into productCreate input + media list."""
    pinput: dict[str, Any] = {
        "handle": p["handle"],
        "title": p["title"],
        "vendor": p.get("vendor", "Fulcrum Coffee Co"),
        "productType": p.get("product_type", ""),
        "tags": p.get("tags", []),
        "descriptionHtml": p.get("body_html", ""),
        "status": "ACTIVE",
    }

    metafields_input = []
    for mf in p.get("metafields", []):
        metafields_input.append({
            "namespace": mf["namespace"],
            "key": mf["key"],
            "type": mf.get("type", "single_line_text_field"),
            "value": str(mf["value"]),
        })
    if metafields_input:
        pinput["metafields"] = metafields_input

    media = []
    for img in p.get("images", []):
        media.append({
            "originalSource": img["src"],
            "alt": img.get("alt", ""),
            "mediaContentType": "IMAGE",
        })

    return pinput, media


def import_product(client: ShopifyClient, product: dict[str, Any]) -> str | None:
    handle = product["handle"]
    existing = find_product_by_handle(client, handle)
    if existing:
        LOG.info("product %s already exists (%s) - skip", handle, existing)
        return existing

    pinput, media = build_product_input(product)
    res = client.query(PRODUCT_CREATE, {"input": pinput, "media": media or None})
    if client.dry_run:
        LOG.info("[dry-run] would create product %s", handle)
        return None

    payload = ((res.get("data") or {}).get("productCreate") or {})
    errs = payload.get("userErrors") or []
    if errs:
        LOG.error("productCreate errors for %s: %s", handle, errs)
        return None
    pid = (payload.get("product") or {}).get("id")
    LOG.info("created product %s -> %s", handle, pid)

    # Variants
    variants_input = []
    for v in product.get("variants", []):
        variants_input.append({
            "optionValues": [{"name": v["title"], "optionName": "Size"}],
            "price": v["price"],
            "inventoryItem": {"sku": v.get("sku", ""), "tracked": True},
            "inventoryQuantities": [],  # locations need to be looked up; skipped to keep script portable
        })
    if variants_input and pid:
        vres = client.query(PRODUCT_VARIANTS_BULK_CREATE, {
            "productId": pid,
            "variants": variants_input,
        })
        verrs = (((vres.get("data") or {}).get("productVariantsBulkCreate") or {}).get("userErrors") or [])
        if verrs:
            LOG.warning("variant errors for %s: %s", handle, verrs)
        else:
            LOG.info("  added %d variants", len(variants_input))

    return pid


# ---------------------------------------------------------------------------
# Policies + pages
# ---------------------------------------------------------------------------

SHOP_POLICY_UPDATE = """
mutation shopPolicyUpdate($shopPolicy: ShopPolicyInput!) {
  shopPolicyUpdate(shopPolicy: $shopPolicy) {
    shopPolicy { id type body }
    userErrors { field message }
  }
}
"""

PAGE_CREATE = """
mutation pageCreate($page: PageCreateInput!) {
  pageCreate(page: $page) {
    page { id handle title }
    userErrors { field message }
  }
}
"""

PAGE_UPDATE = """
mutation pageUpdate($id: ID!, $page: PageUpdateInput!) {
  pageUpdate(id: $id, page: $page) {
    page { id handle title }
    userErrors { field message }
  }
}
"""

POLICY_TYPE_MAP = {
    "shipping-policy": "SHIPPING_POLICY",
    "refund-policy": "REFUND_POLICY",
    "privacy-policy": "PRIVACY_POLICY",
    "terms-of-service": "TERMS_OF_SERVICE",
}


def import_policies(client: ShopifyClient, policies: list[dict[str, Any]]) -> int:
    count = 0
    for pol in policies:
        handle = pol["handle"]
        body = pol["body_html"]
        title = pol["title"]
        ptype = POLICY_TYPE_MAP.get(handle)

        if ptype:
            # Shopify shop policy
            res = client.query(SHOP_POLICY_UPDATE, {
                "shopPolicy": {"type": ptype, "body": body},
            })
            if client.dry_run:
                LOG.info("[dry-run] would update shop policy %s", ptype)
                count += 1
                continue
            errs = (((res.get("data") or {}).get("shopPolicyUpdate") or {}).get("userErrors") or [])
            if errs:
                LOG.error("shopPolicyUpdate %s errors: %s", ptype, errs)
            else:
                LOG.info("updated shop policy %s", ptype)
                count += 1
        else:
            # Online Store page (FAQ, contact, about)
            existing = find_page_by_handle(client, handle)
            if existing:
                res = client.query(PAGE_UPDATE, {
                    "id": existing,
                    "page": {"title": title, "body": body, "handle": handle},
                })
                if client.dry_run:
                    LOG.info("[dry-run] would update page %s", handle)
                    count += 1
                    continue
                errs = (((res.get("data") or {}).get("pageUpdate") or {}).get("userErrors") or [])
                if errs:
                    LOG.error("pageUpdate %s errors: %s", handle, errs)
                else:
                    LOG.info("updated page %s", handle)
                    count += 1
            else:
                res = client.query(PAGE_CREATE, {
                    "page": {"title": title, "body": body, "handle": handle, "isPublished": True},
                })
                if client.dry_run:
                    LOG.info("[dry-run] would create page %s", handle)
                    count += 1
                    continue
                errs = (((res.get("data") or {}).get("pageCreate") or {}).get("userErrors") or [])
                if errs:
                    LOG.error("pageCreate %s errors: %s", handle, errs)
                else:
                    LOG.info("created page %s", handle)
                    count += 1
    return count


# ---------------------------------------------------------------------------
# Reviews - stored as product metafield (json list)
# ---------------------------------------------------------------------------

def import_reviews(client: ShopifyClient, reviews: list[dict[str, Any]]) -> int:
    by_product: dict[str, list[dict[str, Any]]] = {}
    for r in reviews:
        by_product.setdefault(r["product_handle"], []).append(r)

    written = 0
    for handle, items in by_product.items():
        pid = find_product_by_handle(client, handle)
        if not pid and not client.dry_run:
            LOG.warning("no product for review handle %s; skipping %d reviews",
                        handle, len(items))
            continue

        metafields_input = [{
            "ownerId": pid or "gid://shopify/Product/0",
            "namespace": "fulcrum_reviews",
            "key": "items",
            "type": "json",
            "value": json.dumps(items),
        }]
        res = client.query(METAFIELDS_SET, {"metafields": metafields_input})
        if client.dry_run:
            LOG.info("[dry-run] would write %d reviews to %s", len(items), handle)
            written += len(items)
            continue
        errs = (((res.get("data") or {}).get("metafieldsSet") or {}).get("userErrors") or [])
        if errs:
            LOG.error("review metafield errors for %s: %s", handle, errs)
        else:
            LOG.info("wrote %d reviews to %s", len(items), handle)
            written += len(items)
    return written


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="don't hit Shopify; log intended actions")
    parser.add_argument("--only", choices=["products", "policies", "reviews"],
                        help="restrict to one phase")
    parser.add_argument("--catalog", default=str(SCRIPT_DIR / "fulcrum-catalog.json"))
    parser.add_argument("--policies", default=str(SCRIPT_DIR / "fulcrum-policies.json"))
    parser.add_argument("--reviews", default=str(SCRIPT_DIR / "fulcrum-reviews.json"))
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    domain = os.environ.get("SHOPIFY_STORE_DOMAIN", "")
    token = os.environ.get("SHOPIFY_ADMIN_ACCESS_TOKEN", "")

    if not args.dry_run and (not domain or not token):
        LOG.error("set SHOPIFY_STORE_DOMAIN and SHOPIFY_ADMIN_ACCESS_TOKEN, or pass --dry-run")
        return 2

    if args.dry_run and not domain:
        domain = "fulcrum-dry-run.myshopify.example"

    catalog = load_json(Path(args.catalog))
    policies = load_json(Path(args.policies))
    reviews = load_json(Path(args.reviews))

    client = ShopifyClient(domain, token, dry_run=args.dry_run)
    products_done = 0
    policies_done = 0
    reviews_done = 0

    try:
        if args.only in (None, "products"):
            LOG.info("=== importing %d products ===", len(catalog["products"]))
            for product in catalog["products"]:
                pid = import_product(client, product)
                if pid is not None or args.dry_run:
                    products_done += 1

        if args.only in (None, "policies"):
            LOG.info("=== importing %d policies ===", len(policies["policies"]))
            policies_done = import_policies(client, policies["policies"])

        if args.only in (None, "reviews"):
            LOG.info("=== importing %d reviews ===", len(reviews["reviews"]))
            reviews_done = import_reviews(client, reviews["reviews"])
    finally:
        client.close()

    LOG.info("done. products=%d policies=%d reviews=%d (dry_run=%s)",
             products_done, policies_done, reviews_done, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
