"""Ownership / multi-tenant scoping tests (`api/ownership.py`).

Pure, in-memory tests - no Neo4j connection. They lock in the two invariants
the scoping layer must never break:

    1. DEMO SAFETY (auth off / inactive scope): every helper is a complete
       no-op. The predicate is the literal ``true``, no ``owner_uid`` param is
       added, writes are not stamped, and every ownership check passes. This is
       what keeps the open public demo (``AUTH_REQUIRED=false``) unaffected.

    2. TENANT ISOLATION (auth on / active scope): the predicate binds
       ``owner_uid`` (while still matching legacy unowned nodes), writes are
       stamped, and cross-tenant resources are rejected with 403 / unknown ones
       with 404.

If a future change weakens either invariant, this file fails by design.
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from api.ownership import OWNER_PROP, ScopeContext, _claims_to_scope


# ---------------------------------------------------------------------------
# Inactive scope == open demo. Everything is a no-op.
# ---------------------------------------------------------------------------


def test_inactive_predicate_is_literal_true() -> None:
    scope = ScopeContext(owner_uid=None, active=False)
    assert scope.predicate("n") == "true"
    assert scope.predicate("g") == "true"


def test_inactive_params_add_no_owner() -> None:
    scope = ScopeContext(owner_uid=None, active=False)
    assert scope.params() == {}
    assert scope.params({"limit": 10}) == {"limit": 10}
    assert "owner_uid" not in scope.params({"id": "x"})


def test_inactive_stamp_adds_nothing() -> None:
    scope = ScopeContext(owner_uid=None, active=False)
    assert scope.stamp({"title": "Yirgacheffe"}) == {"title": "Yirgacheffe"}
    assert OWNER_PROP not in scope.stamp({"title": "x"})


def test_inactive_ownership_checks_always_pass() -> None:
    scope = ScopeContext(owner_uid=None, active=False)
    assert scope.owns(None) is True
    assert scope.owns({OWNER_PROP: "someone-else"}) is True
    # require_owns must not raise even on a missing / foreign node.
    scope.require_owns(None, kind="gap")
    scope.require_owns({OWNER_PROP: "someone-else"}, kind="fix")


# ---------------------------------------------------------------------------
# Active scope == multi-tenant isolation.
# ---------------------------------------------------------------------------


def test_active_predicate_binds_owner_and_allows_legacy() -> None:
    scope = ScopeContext(owner_uid="uid-123", active=True)
    pred = scope.predicate("n")
    assert "n.owner_uid = $owner_uid" in pred
    assert "n.owner_uid IS NULL" in pred  # legacy nodes still visible


def test_active_params_inject_owner_uid() -> None:
    scope = ScopeContext(owner_uid="uid-123", active=True)
    assert scope.params() == {"owner_uid": "uid-123"}
    merged = scope.params({"limit": 5})
    assert merged == {"limit": 5, "owner_uid": "uid-123"}


def test_active_params_does_not_mutate_caller_dict() -> None:
    scope = ScopeContext(owner_uid="uid-123", active=True)
    base = {"limit": 5}
    scope.params(base)
    assert base == {"limit": 5}  # caller dict untouched


def test_active_stamp_sets_owner() -> None:
    scope = ScopeContext(owner_uid="uid-123", active=True)
    stamped = scope.stamp({"title": "x"})
    assert stamped[OWNER_PROP] == "uid-123"


def test_active_owns_matrix() -> None:
    scope = ScopeContext(owner_uid="uid-123", active=True)
    assert scope.owns({OWNER_PROP: "uid-123"}) is True   # own node
    assert scope.owns({OWNER_PROP: None}) is True         # legacy unowned
    assert scope.owns({}) is True                          # no owner prop == legacy
    assert scope.owns({OWNER_PROP: "uid-999"}) is False   # cross-tenant
    assert scope.owns(None) is False                       # absent


def test_active_require_owns_404_on_missing() -> None:
    scope = ScopeContext(owner_uid="uid-123", active=True)
    with pytest.raises(HTTPException) as exc:
        scope.require_owns(None, kind="gap")
    assert exc.value.status_code == 404


def test_active_require_owns_403_on_cross_tenant() -> None:
    scope = ScopeContext(owner_uid="uid-123", active=True)
    with pytest.raises(HTTPException) as exc:
        scope.require_owns({OWNER_PROP: "uid-999"}, kind="fix")
    assert exc.value.status_code == 403


def test_active_require_owns_passes_for_owner_and_legacy() -> None:
    scope = ScopeContext(owner_uid="uid-123", active=True)
    scope.require_owns({OWNER_PROP: "uid-123"}, kind="fix")  # no raise
    scope.require_owns({OWNER_PROP: None}, kind="fix")        # legacy, no raise


# ---------------------------------------------------------------------------
# claims -> scope resolution (the auth toggle boundary)
# ---------------------------------------------------------------------------


def test_auth_disabled_sentinel_yields_inactive_scope() -> None:
    # This is exactly what require_user returns when AUTH_REQUIRED=false.
    scope = _claims_to_scope({"uid": "anonymous-local", "_auth_disabled": True})
    assert scope.active is False
    assert scope.predicate("n") == "true"


def test_real_claims_yield_active_owner_scope() -> None:
    scope = _claims_to_scope({"uid": "firebase-uid-abc"})
    assert scope.active is True
    assert scope.owner_uid == "firebase-uid-abc"


def test_claims_without_uid_fall_back_to_inactive() -> None:
    # Authenticated but malformed claims must not scope to "" (which would hide
    # everything); they degrade to inactive instead.
    scope = _claims_to_scope({})
    assert scope.active is False
