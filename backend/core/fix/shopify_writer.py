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

import json
import logging
from datetime import datetime, timezone

from api.schemas import FixSuggestion
from services.shopify_service import ShopifyError, shopify_service

logger = logging.getLogger("echomind.fix.shopify_writer")


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

    try:
        if fix.fix_type == "copy_rewrite":
            if not target_product_gid:
                raise ShopifyError(
                    "copy_rewrite requires target_product_gid (Shopify product gid)"
                )
            updated = await shopify_service.update_product_description(
                target_product_gid, fix.proposed_text
            )
            resource_id = updated.get("id") or target_product_gid

        elif fix.fix_type == "policy_clarify":
            if not target_page_gid:
                raise ShopifyError("policy_clarify requires target_page_gid")
            updated = await shopify_service.update_page_body(
                target_page_gid, fix.proposed_text
            )
            resource_id = updated.get("id") or target_page_gid

        elif fix.fix_type == "faq_add":
            if target_page_gid:
                # Append to existing FAQ page body.
                updated = await shopify_service.update_page_body(
                    target_page_gid, fix.proposed_text
                )
                resource_id = updated.get("id") or target_page_gid
            elif target_product_gid:
                await shopify_service.apply_metafield(
                    target_product_gid,
                    metafield_namespace,
                    "faq_addendum",
                    fix.proposed_text,
                    metafield_type="multi_line_text_field",
                )
                resource_id = target_product_gid
            else:
                raise ShopifyError(
                    "faq_add requires target_page_gid or target_product_gid"
                )

        elif fix.fix_type == "metafield_add":
            if not target_product_gid:
                raise ShopifyError("metafield_add requires target_product_gid")
            value = fix.proposed_text
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
                raise ShopifyError("structured_data requires target_product_gid")
            # Validate JSON before pushing (it will be served via theme include).
            try:
                json.loads(fix.proposed_text)
            except json.JSONDecodeError as e:
                raise ShopifyError(f"structured_data must be valid JSON: {e}") from e
            await shopify_service.apply_metafield(
                target_product_gid,
                metafield_namespace,
                "structured_data_json_ld",
                fix.proposed_text,
                metafield_type="json",
            )
            resource_id = target_product_gid
        else:
            raise ShopifyError(f"unknown fix_type: {fix.fix_type}")
    except Exception:  # noqa: BLE001 - surface to caller, log here
        from utils.logging_safety import safe_log
        logger.exception("fix.apply_failed fix_id=%s", safe_log(fix.id))
        raise

    return fix.model_copy(
        update={
            "applied": True,
            "applied_at": datetime.now(timezone.utc),
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


__all__ = ["apply_fix", "revert_fix"]
