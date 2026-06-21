"""Echomind Commerce - per-owner (multi-tenant) scoping for graph reads/writes.

Background
----------
Every graph/audit/fix read currently runs against the whole Neo4j database and
the ``{store_id}`` path segment is decorative - it is echoed in the response but
never bound into Cypher. The same is true of ``/fix/apply``: it applies whatever
``FixSuggestion`` the caller hands it, with no ownership check. In a single-store
demo that is fine; the instant the deployment becomes multi-tenant it is an
IDOR-class authorization gap.

This module adds the missing server-side scoping infrastructure as
*defense-in-depth*. It is deliberately built so that:

    * With ``AUTH_REQUIRED=false`` (the public demo) it is a complete no-op.
      ``require_user`` returns the ``_auth_disabled`` sentinel, ``ScopeContext``
      reports ``active = False``, every Cypher predicate degrades to ``true`` and
      writes stamp nothing. The graph behaves exactly as before - the open demo
      is unaffected.

    * With auth enabled (a verified Firebase token), ``ScopeContext`` carries the
      authenticated ``owner_uid``. Read predicates bind ``owner_uid`` into the
      Cypher (legacy nodes with no owner stamp are *also* matched so existing
      single-tenant data keeps rendering), upserts stamp ``owner_uid`` onto new
      nodes, and ownership checks reject cross-tenant mutations with HTTP 403.

The flip to enforced multi-tenant isolation is therefore a *configuration*
decision (set ``AUTH_REQUIRED=true`` and wire the Firebase-token frontend), not
a code change. See SECURITY.md / README.md for the production checklist.

Usage
-----
HTTP route::

    from api.ownership import ScopeContext, scope_ctx

    @router.get("/{store_id}")
    async def get_graph(store_id: str, scope: ScopeContext = Depends(scope_ctx)):
        cypher = f"MATCH (n) WHERE {scope.predicate('n')} RETURN n"
        rows = await neo4j_client.run(cypher, scope.params())

Read predicate convention
-------------------------
``scope.predicate("n")`` returns a Cypher boolean fragment. When scoping is
inactive it is the literal ``true`` (matches everything). When active it is
``(n.owner_uid = $owner_uid OR n.owner_uid IS NULL)`` so that:

    * nodes owned by the caller match, and
    * legacy nodes written before scoping existed (no ``owner_uid``) still match,
      avoiding a silent data blackout on first deploy.

A future hard-isolation mode can drop the ``IS NULL`` arm once a backfill stamps
every legacy node; that is called out in SECURITY.md.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import Depends, HTTPException, status

from api.auth_deps import require_user

logger = logging.getLogger("echomind.ownership")

# Property name stamped on owned nodes. Kept here as the single source of truth
# so reads, writes, and ownership checks never drift.
OWNER_PROP = "owner_uid"


class ScopeContext:
    """Resolved per-request ownership scope.

    ``active`` is True only when a real authenticated owner is present. When
    False every method degrades to a no-op so the open demo is unaffected.
    """

    __slots__ = ("owner_uid", "active")

    def __init__(self, owner_uid: str | None, active: bool) -> None:
        self.owner_uid = owner_uid
        self.active = active

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def predicate(self, var: str = "n") -> str:
        """Cypher boolean fragment scoping node ``var`` to this owner.

        Inactive  -> ``true`` (matches everything; demo behaviour unchanged).
        Active    -> ``(n.owner_uid = $owner_uid OR n.owner_uid IS NULL)``.

        The ``IS NULL`` arm keeps pre-scoping (legacy) nodes visible so enabling
        auth never blanks out an existing single-tenant graph. ``var`` must be a
        trusted, code-controlled identifier (never user input).
        """
        if not self.active:
            return "true"
        return f"({var}.{OWNER_PROP} = $owner_uid OR {var}.{OWNER_PROP} IS NULL)"

    def params(self, base: dict[str, Any] | None = None) -> dict[str, Any]:
        """Merge ``$owner_uid`` into a Cypher params dict when scoping is active.

        Always returns a dict safe to hand to ``neo4j_client.run``. When inactive
        the owner param is omitted (the predicate never references it).
        """
        params: dict[str, Any] = dict(base or {})
        if self.active:
            params["owner_uid"] = self.owner_uid
        return params

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def stamp(self, props: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return ``props`` with ``owner_uid`` added when scoping is active.

        Used by upserts so newly written nodes carry their owner and become
        scopable on subsequent reads. A no-op (returns a copy unchanged) in the
        demo, so the open graph never grows an ``owner_uid`` it would then have
        to read around.
        """
        out: dict[str, Any] = dict(props or {})
        if self.active and self.owner_uid:
            out[OWNER_PROP] = self.owner_uid
        return out

    # ------------------------------------------------------------------
    # Ownership checks (mutations)
    # ------------------------------------------------------------------

    def owns(self, node: dict[str, Any] | None) -> bool:
        """True if ``node`` may be acted on by this caller.

        Inactive -> always True (demo). Active -> True when the node is unowned
        (legacy) or owned by this caller; False on a cross-tenant node.
        """
        if not self.active:
            return True
        if node is None:
            return False
        owner = node.get(OWNER_PROP)
        return owner is None or owner == self.owner_uid

    def require_owns(self, node: dict[str, Any] | None, *, kind: str = "resource") -> None:
        """Raise 404 (missing) / 403 (cross-tenant) unless the caller owns ``node``.

        404 is used for an absent node so we do not leak the existence of another
        tenant's resource; 403 is used when the node exists but belongs to a
        different owner. No-op when scoping is inactive.
        """
        if not self.active:
            return
        if node is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{kind} not found",
            )
        if not self.owns(node):
            logger.warning("ownership.denied kind=%s owner=%s", kind, self.owner_uid)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized for this {kind}",
            )


def _claims_to_scope(claims: dict[str, Any]) -> ScopeContext:
    """Build a ScopeContext from decoded auth claims.

    The ``_auth_disabled`` sentinel (returned by ``require_user`` when
    ``AUTH_REQUIRED=false``) yields an inactive scope. A real verified token
    (with a ``uid``) yields an active, owner-bound scope.
    """
    if claims.get("_auth_disabled"):
        return ScopeContext(owner_uid=None, active=False)
    uid = claims.get("uid")
    if not uid:
        # Authenticated but no uid in claims - treat as inactive rather than
        # binding an empty owner, which would scope to "" and hide everything.
        logger.warning("ownership.no_uid_in_claims - scoping inactive for this request")
        return ScopeContext(owner_uid=None, active=False)
    return ScopeContext(owner_uid=str(uid), active=True)


def scope_ctx(claims: dict[str, Any] = Depends(require_user)) -> ScopeContext:
    """FastAPI dependency: resolve the per-request ScopeContext.

    Depends on ``require_user`` so it inherits the exact auth toggle semantics
    (401 on missing/invalid token when ``AUTH_REQUIRED=true``; sentinel when
    disabled). Inject with ``scope: ScopeContext = Depends(scope_ctx)``.
    """
    return _claims_to_scope(claims)


__all__ = ["OWNER_PROP", "ScopeContext", "scope_ctx"]
