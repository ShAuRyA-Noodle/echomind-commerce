"""Echomind Commerce - Shopify Admin + Storefront client (production).

Real httpx clients; no mocks. Used everywhere Shopify is touched.

Capabilities
------------
* `fetch_shop_metadata()`           - name, currency, plan, primary domain
* `crawl_products(page_size)`       - async generator over paginated catalog
* `fetch_pages()`                   - Shopify "page" content (FAQ, About, …)
* `fetch_shop_policies()`           - privacy / refund / shipping / TOS / sub
* `update_product_description()`    - REAL Admin GraphQL mutation
* `update_page_body()`              - page body fixes
* `apply_metafield()`               - structured-data / FAQ metafield fixes
* `snapshot_product()` / `revert_product()` - Decision Log #15 safety net
* `audit_public_store()` (classmethod) - Tier S #1: paste any Shopify URL +
   storefront token → reduced public audit, no Admin auth required.

Resilience
----------
* `tenacity` retry on 429 / 5xx / connection-class exceptions
* 30s timeout per request
* `dry_run=True` short-circuits all mutations to logged no-ops
* userErrors from GraphQL surfaced as `ShopifyError`
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, AsyncIterator

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import settings
from utils.logging_safety import safe_log

logger = logging.getLogger("echomind.shopify")


_TRANSIENT_EXC: tuple[type[BaseException], ...] = (
    httpx.ReadTimeout,
    httpx.WriteTimeout,
    httpx.ConnectTimeout,
    httpx.RemoteProtocolError,
    httpx.NetworkError,
)


class ShopifyError(Exception):
    """Hard Shopify failure (4xx other than 429, malformed payload, userErrors)."""


# ---------------------------------------------------------------------------
# Reusable GraphQL fragments
# ---------------------------------------------------------------------------


SHOP_QUERY = """
query ShopMetadata {
  shop {
    id
    name
    currencyCode
    primaryDomain { url host }
    contactEmail
    plan { displayName }
  }
}
"""

PRODUCTS_QUERY = """
query Products($first: Int!, $after: String) {
  products(first: $first, after: $after) {
    edges {
      cursor
      node {
        id
        handle
        title
        description
        descriptionHtml
        vendor
        productType
        tags
        createdAt
        updatedAt
        featuredImage { url altText }
        images(first: 5) { edges { node { url altText } } }
        options { name values }
        variants(first: 10) {
          edges { node { id title price sku availableForSale } }
        }
        metafields(first: 30) {
          edges { node { namespace key value type } }
        }
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""

PAGES_QUERY = """
query Pages($first: Int!, $after: String) {
  pages(first: $first, after: $after) {
    edges {
      cursor
      node {
        id handle title body bodyHtml createdAt updatedAt
      }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""

SHOP_POLICIES_QUERY = """
query ShopPolicies {
  shop {
    privacyPolicy { id title body url }
    refundPolicy  { id title body url }
    shippingPolicy { id title body url }
    termsOfService { id title body url }
    subscriptionPolicy { id title body url }
  }
}
"""

PRODUCT_UPDATE_MUTATION = """
mutation ProductUpdate($input: ProductInput!) {
  productUpdate(input: $input) {
    product { id title descriptionHtml updatedAt }
    userErrors { field message }
  }
}
"""

PAGE_UPDATE_MUTATION = """
mutation PageUpdate($id: ID!, $page: PageUpdateInput!) {
  pageUpdate(id: $id, page: $page) {
    page { id title body updatedAt }
    userErrors { field message }
  }
}
"""

METAFIELD_SET_MUTATION = """
mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { id namespace key value type }
    userErrors { field message code }
  }
}
"""

PUBLIC_PRODUCTS_QUERY = """
query PublicProducts($first: Int!) {
  products(first: $first) {
    edges {
      node {
        id handle title description vendor productType tags
        featuredImage { url altText }
        priceRange { minVariantPrice { amount currencyCode } }
      }
    }
  }
}
"""

PRODUCT_SNAPSHOT_QUERY = """
query Snap($id: ID!) {
  product(id: $id) { id title descriptionHtml }
}
"""


class ShopifyService:
    """Real Shopify Admin + Storefront client. No mocks anywhere."""

    def __init__(
        self,
        store_domain: str | None = None,
        admin_token: str | None = None,
        storefront_token: str | None = None,
        api_version: str | None = None,
        dry_run: bool = False,
        timeout: float = 30.0,
    ) -> None:
        self.store_domain = store_domain or settings.SHOPIFY_STORE_DOMAIN
        self.admin_token = admin_token or settings.SHOPIFY_ADMIN_ACCESS_TOKEN
        self.storefront_token = storefront_token or settings.SHOPIFY_STOREFRONT_ACCESS_TOKEN
        self.api_version = api_version or settings.SHOPIFY_API_VERSION
        self.dry_run = dry_run
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._snapshots: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # URLs + headers
    # ------------------------------------------------------------------

    @property
    def admin_url(self) -> str:
        return f"https://{self.store_domain}/admin/api/{self.api_version}/graphql.json"

    @property
    def storefront_url(self) -> str:
        return f"https://{self.store_domain}/api/{self.api_version}/graphql.json"

    def _admin_headers(self) -> dict[str, str]:
        if not self.admin_token:
            raise ShopifyError("SHOPIFY_ADMIN_ACCESS_TOKEN not configured")
        return {
            "X-Shopify-Access-Token": self.admin_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _storefront_headers(self) -> dict[str, str]:
        if not self.storefront_token:
            raise ShopifyError("SHOPIFY_STOREFRONT_ACCESS_TOKEN not configured")
        return {
            "X-Shopify-Storefront-Access-Token": self.storefront_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ------------------------------------------------------------------
    # Async client lifecycle
    # ------------------------------------------------------------------

    async def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout, connect=10.0),
                headers={"User-Agent": "Echomind-Commerce/0.1"},
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # GraphQL transports - async + sync
    # ------------------------------------------------------------------

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(_TRANSIENT_EXC),
    )
    async def admin_graphql(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        c = await self.client()
        r = await c.post(
            self.admin_url,
            headers=self._admin_headers(),
            json={"query": query, "variables": variables or {}},
        )
        return self._handle_response(r)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(_TRANSIENT_EXC),
    )
    async def storefront_graphql(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        c = await self.client()
        r = await c.post(
            self.storefront_url,
            headers=self._storefront_headers(),
            json={"query": query, "variables": variables or {}},
        )
        return self._handle_response(r)

    def _handle_response(self, r: httpx.Response) -> dict[str, Any]:
        if r.status_code == 429:
            retry_after = float(r.headers.get("Retry-After", "2"))
            logger.warning("shopify.rate_limited retry_after=%s", retry_after)
            time.sleep(min(retry_after, 8.0))
            raise httpx.RemoteProtocolError("Rate limited")
        if 500 <= r.status_code < 600:
            raise httpx.RemoteProtocolError(f"Shopify {r.status_code}: {r.text[:200]}")
        if r.status_code >= 400:
            raise ShopifyError(f"Shopify {r.status_code}: {r.text[:300]}")
        try:
            data = r.json()
        except json.JSONDecodeError as e:
            raise ShopifyError(f"Shopify returned non-JSON: {r.text[:200]}") from e
        if "errors" in data and data["errors"]:
            logger.warning("shopify.graphql.errors=%s", data["errors"])
        return data

    # ------------------------------------------------------------------
    # READS - used by catalog ingest
    # ------------------------------------------------------------------

    async def fetch_shop_metadata(self) -> dict[str, Any]:
        result = await self.admin_graphql(SHOP_QUERY)
        return result.get("data", {}).get("shop", {})

    async def crawl_products(self, page_size: int = 50) -> AsyncIterator[dict[str, Any]]:
        """Async generator yielding products one at a time across pagination."""
        cursor: str | None = None
        while True:
            result = await self.admin_graphql(
                PRODUCTS_QUERY, {"first": page_size, "after": cursor}
            )
            edges = result.get("data", {}).get("products", {}).get("edges", [])
            for edge in edges:
                yield edge.get("node", {})
            page_info = result.get("data", {}).get("products", {}).get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info.get("endCursor")

    async def fetch_pages(self, page_size: int = 50) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            result = await self.admin_graphql(
                PAGES_QUERY, {"first": page_size, "after": cursor}
            )
            edges = result.get("data", {}).get("pages", {}).get("edges", [])
            for edge in edges:
                out.append(edge.get("node", {}))
            page_info = result.get("data", {}).get("pages", {}).get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break
            cursor = page_info.get("endCursor")
        return out

    async def fetch_shop_policies(self) -> dict[str, Any]:
        result = await self.admin_graphql(SHOP_POLICIES_QUERY)
        return result.get("data", {}).get("shop", {})

    # ------------------------------------------------------------------
    # MUTATIONS - fix application
    # ------------------------------------------------------------------

    async def snapshot_product(self, product_gid: str) -> dict[str, Any]:
        """Capture pre-mutation state. Feeds revert_product() if needed."""
        result = await self.admin_graphql(PRODUCT_SNAPSHOT_QUERY, {"id": product_gid})
        snap = result.get("data", {}).get("product", {})
        if snap:
            self._snapshots[product_gid] = snap
        return snap

    async def update_product_description(
        self, product_gid: str, new_description_html: str
    ) -> dict[str, Any]:
        """REAL Admin GraphQL mutation - applies a fix to a live product page."""
        if self.dry_run:
            logger.info("shopify.dry_run.product_update gid=%s", safe_log(product_gid))
            return {"dry_run": True, "product_id": product_gid}
        await self.snapshot_product(product_gid)
        result = await self.admin_graphql(
            PRODUCT_UPDATE_MUTATION,
            {"input": {"id": product_gid, "descriptionHtml": new_description_html}},
        )
        update = result.get("data", {}).get("productUpdate", {})
        errors = update.get("userErrors") or []
        if errors:
            raise ShopifyError(f"productUpdate errors: {errors}")
        return update.get("product", {})

    async def update_page_body(self, page_gid: str, new_body: str) -> dict[str, Any]:
        if self.dry_run:
            logger.info("shopify.dry_run.page_update gid=%s", safe_log(page_gid))
            return {"dry_run": True, "page_id": page_gid}
        result = await self.admin_graphql(
            PAGE_UPDATE_MUTATION, {"id": page_gid, "page": {"body": new_body}}
        )
        update = result.get("data", {}).get("pageUpdate", {})
        errors = update.get("userErrors") or []
        if errors:
            raise ShopifyError(f"pageUpdate errors: {errors}")
        return update.get("page", {})

    async def apply_metafield(
        self,
        owner_gid: str,
        namespace: str,
        key: str,
        value: str,
        metafield_type: str = "single_line_text_field",
    ) -> dict[str, Any]:
        if self.dry_run:
            logger.info("shopify.dry_run.metafield ns=%s key=%s", namespace, key)
            return {"dry_run": True}
        result = await self.admin_graphql(
            METAFIELD_SET_MUTATION,
            {
                "metafields": [
                    {
                        "ownerId": owner_gid,
                        "namespace": namespace,
                        "key": key,
                        "value": value,
                        "type": metafield_type,
                    }
                ]
            },
        )
        out = result.get("data", {}).get("metafieldsSet", {})
        errors = out.get("userErrors") or []
        if errors:
            raise ShopifyError(f"metafieldsSet errors: {errors}")
        return out

    async def revert_product(self, product_gid: str) -> dict[str, Any]:
        snap = self._snapshots.get(product_gid)
        if not snap:
            raise ShopifyError(f"no snapshot stored for {product_gid}")
        return await self.update_product_description(
            product_gid, snap.get("descriptionHtml") or ""
        )

    # Backwards-compat alias kept for older imports.
    async def upsert_metafield(
        self,
        owner_gid: str,
        namespace: str,
        key: str,
        value: str,
        type_: str = "single_line_text_field",
    ) -> dict[str, Any]:
        return await self.apply_metafield(owner_gid, namespace, key, value, type_)

    async def fetch_catalog(self, *, limit: int = 250) -> list[dict[str, Any]]:
        """Eager pull of the full catalog - convenience for one-shot ingest."""
        out: list[dict[str, Any]] = []
        async for p in self.crawl_products(page_size=min(limit, 50)):
            out.append(p)
            if len(out) >= limit:
                break
        return out

    async def fetch_policies(self) -> list[dict[str, Any]]:
        shop = await self.fetch_shop_policies()
        out: list[dict[str, Any]] = []
        for key in (
            "privacyPolicy",
            "refundPolicy",
            "shippingPolicy",
            "termsOfService",
            "subscriptionPolicy",
        ):
            v = shop.get(key)
            if v:
                v["_kind"] = key
                out.append(v)
        return out

    async def fetch_reviews(self) -> list[dict[str, Any]]:
        """Fetch reviews stored as `fulcrum_reviews.items` JSON metafield per product."""
        out: list[dict[str, Any]] = []
        async for product in self.crawl_products(page_size=50):
            for edge in product.get("metafields", {}).get("edges", []) or []:
                node = edge.get("node", {})
                if (
                    node.get("namespace") == "fulcrum_reviews"
                    and node.get("key") == "items"
                ):
                    try:
                        items = json.loads(node.get("value", "[]"))
                    except json.JSONDecodeError:
                        items = []
                    for it in items:
                        it["_product_id"] = product.get("id")
                        out.append(it)
        return out

    # ------------------------------------------------------------------
    # PUBLIC AUDIT - Tier S #1
    # ------------------------------------------------------------------

    @classmethod
    async def audit_public_store(
        cls,
        store_domain: str,
        storefront_token: str,
        api_version: str = "2025-01",
        product_limit: int = 20,
    ) -> dict[str, Any]:
        """Run a reduced audit against ANY public Shopify store with only its
        Storefront token. Used by `/api/audit/public` - judges/merchants paste
        their store + storefront token, get a 60s reduced audit. No Admin auth.
        """
        svc = cls(
            store_domain=store_domain,
            storefront_token=storefront_token,
            api_version=api_version,
        )
        try:
            result = await svc.storefront_graphql(
                PUBLIC_PRODUCTS_QUERY, {"first": product_limit}
            )
            edges = result.get("data", {}).get("products", {}).get("edges", [])
            products = [e["node"] for e in edges]
            return {
                "store_domain": store_domain,
                "product_count": len(products),
                "products": products,
            }
        finally:
            await svc.close()


shopify_service = ShopifyService()
