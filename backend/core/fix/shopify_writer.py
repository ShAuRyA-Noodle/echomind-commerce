"""Echomind Commerce - fix → Shopify mutation writer.

Takes a `FixSuggestion`, dispatches the right Shopify mutation by `fix_type`,
records the change, and returns the updated resource. Built on
`services/shopify_service.py` which already wraps tenacity retries +
snapshot/revert (Decision Log #15).

Routing:
    * copy_rewrite     → ShopifyService.update_product_description
    * faq_add          → ShopifyService.update_page_body  (FAQ page) OR
                          apply_metafield (faq:items)
    * policy_clarify   → ShopifyService.update_page_body  (policy page)
    * metafield_add    → ShopifyService.apply_metafield
    * structured_data  → ShopifyService.apply_metafield (json type)

Each application:
    * snapshots the resource pre-mutation
    * runs the mutation through tenacity (3 retries on 429/5xx)
    * records the new resource id + observed delta = None (re-test fills it)
"""

from __future__ import annotations

import html
import json
import logging
import re
from datetime import UTC, datetime

from api.schemas import FixSuggestion
from services.shopify_service import ShopifyError, shopify_service

logger = logging.getLogger("echomind.fix.shopify_writer")

# Upper bound for any text pushed to the live store. The copy prompt asks for
# 80-200 words, so anything this long is a runaway generation or bad input.
MAX_FIX_TEXT_CHARS = 10_000
_GID_RE = {
    "Product": re.compile(r"^gid://shopify/Product/\d+$"),
    "Page": re.compile(r"^gid://shopify/Page/\d+$"),
}
_HTML_TAG_RE = re.compile(r"<\s*/?\s*[a-zA-Z!?]")
_SCRIPT_BREAKOUT_RE = re.compile(r"<\s*/\s*script|<!--", re.IGNORECASE)


class FixValidationError(ShopifyError):
    """Fix text or target failed validation, so nothing was written to the store."""


def _check_gid(gid: str, kind: str) -> str:
    if not _GID_RE[kind].match(gid):
        raise FixValidationError(f"target must be a Shopify {kind} gid like gid://shopify/{kind}/123")
    return gid


def _clean_text(fix: FixSuggestion) -> str:
    """Validate fix text (LLM output or merchant edit) before it reaches the store."""
    text = fix.proposed_text if isinstance(fix.proposed_text, str) else ""
    text = text.strip()
    if not text:
        raise FixValidationError("proposed_text is empty; refusing to write an empty fix")
    if len(text) > MAX_FIX_TEXT_CHARS:
        raise FixValidationError(
            f"proposed_text is longer than {MAX_FIX_TEXT_CHARS} characters"
        )
    return text


def _plain_text_to_html(text: str) -> str:
    """Escape plain-text copy so no markup or script can reach a storefront page."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return "".join(
        "<p>" + html.escape(p).replace("\n", "<br>") + "</p>" for p in paragraphs
    )


def _reject_markup(text: str) -> str:
    """Text metafields are printed raw by Liquid themes, so refuse HTML tags."""
    if _HTML_TAG_RE.search(text):
        raise FixValidationError("proposed_text must be plain text (HTML tags are not allowed)")
    return text


async def apply_fix(
    fix: FixSuggestion,
    *,
    target_product_gid: str | None = None,
    target_page_gid: str | None = None,
    metafield_namespace: str = "echomind",
    metafield_key: str = "ai_readiness_fix",
) -> FixSuggestion:
    """Apply a typed FixSuggestion against the live Shopify store.

    Returns the FixSuggestion with `applied=True`, `applied_at`, and
    `shopify_resource_id` populated. Re-test orchestrator measures the
    observed delta and fills `observed_delta` separately.
    """
    if fix.applied:
        return fix

    resource_id: str | None = None
    text = _clean_text(fix)
    if target_product_gid:
        _check_gid(target_product_gid, "Product")
    if target_page_gid:
        _check_gid(target_page_gid, "Page")

    try:
        if fix.fix_type == "copy_rewrite":
            if not target_product_gid:
                raise FixValidationError(
                    "copy_rewrite requires target_product_gid (Shopify product gid)"
                )
            updated = await shopify_service.update_product_description(
                target_product_gid, _plain_text_to_html(text)
            )
            resource_id = updated.get("id") or target_product_gid

        elif fix.fix_type == "policy_clarify":
            if not target_page_gid:
                raise FixValidationError("policy_clarify requires target_page_gid")
            updated = await shopify_service.update_page_body(
                target_page_gid, _plain_text_to_html(text)
            )
            resource_id = updated.get("id") or target_page_gid

        elif fix.fix_type == "faq_add":
            if target_page_gid:
                # Append to existing FAQ page body.
                updated = await shopify_service.update_page_body(
                    target_page_gid, _plain_text_to_html(text)
                )
                resource_id = updated.get("id") or target_page_gid
            elif target_product_gid:
                await shopify_service.apply_metafield(
                    target_product_gid,
                    metafield_namespace,
                    "faq_addendum",
                    _reject_markup(text),
                    metafield_type="multi_line_text_field",
                )
                resource_id = target_product_gid
            else:
                raise FixValidationError(
                    "faq_add requires target_page_gid or target_product_gid"
                )

        elif fix.fix_type == "metafield_add":
            if not target_product_gid:
                raise FixValidationError("metafield_add requires target_product_gid")
            value = _reject_markup(text)
            await shopify_service.apply_metafield(
                target_product_gid,
                metafield_namespace,
                metafield_key,
                value,
                metafield_type="single_line_text_field",
            )
            resource_id = target_product_gid

        elif fix.fix_type == "structured_data":
            if not target_product_gid:
                raise FixValidationError("structured_data requires target_product_gid")
            # Validate JSON before pushing (it will be served via theme include
            # inside a <script type="application/ld+json"> tag).
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as e:
                raise FixValidationError(f"structured_data must be valid JSON: {e}") from e
            if not isinstance(parsed, dict | list):
                raise FixValidationError("structured_data must be a JSON object or array")
            if _SCRIPT_BREAKOUT_RE.search(text):
                raise FixValidationError("structured_data must not contain </script or <!--")
            await shopify_service.apply_metafield(
                target_product_gid,
                metafield_namespace,
                "structured_data_json_ld",
                text,
                metafield_type="json",
            )
            resource_id = target_product_gid
        else:
            raise FixValidationError(f"unknown fix_type: {fix.fix_type}")
    except ShopifyError as exc:
        from utils.logging_safety import safe_log
        logger.warning("fix.apply_failed fix_id=%s reason=%s", safe_log(fix.id), safe_log(exc, 200))
        raise
    except Exception:
        from utils.logging_safety import safe_log
        logger.exception("fix.apply_failed fix_id=%s", safe_log(fix.id))
        raise

    return fix.model_copy(
        update={
            "applied": True,
            "applied_at": datetime.now(UTC),
            "shopify_resource_id": resource_id,
        }
    )


async def revert_fix(
    fix: FixSuggestion, target_product_gid: str | None = None
) -> dict[str, str]:
    """Revert a copy_rewrite fix using the snapshot taken pre-mutation."""
    if fix.fix_type != "copy_rewrite":
        return {"reverted": "false", "reason": "only copy_rewrite supports revert today"}
    gid = target_product_gid or fix.shopify_resource_id
    if not gid:
        return {"reverted": "false", "reason": "no target gid available"}
    await shopify_service.revert_product(gid)
    return {"reverted": "true", "product_id": gid}


__all__ = ["FixValidationError", "apply_fix", "revert_fix"]
