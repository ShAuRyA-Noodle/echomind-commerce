"""Hardening tests: fix text validation before Shopify writes, WebSocket origin
checks, and clear 503s when Neo4j is not configured.

No network: the Shopify service is replaced with a recorder, and the app runs
through FastAPI's TestClient with NEO4J_URI empty (as in CI).
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from api.schemas import FixSuggestion
from core.fix import shopify_writer
from core.fix.shopify_writer import FixValidationError, apply_fix

PRODUCT = "gid://shopify/Product/123"
PAGE = "gid://shopify/Page/45"


class _Recorder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...]]] = []

    async def update_product_description(self, gid: str, body: str) -> dict[str, Any]:
        self.calls.append(("product", (gid, body)))
        return {"id": gid}

    async def update_page_body(self, gid: str, body: str) -> dict[str, Any]:
        self.calls.append(("page", (gid, body)))
        return {"id": gid}

    async def apply_metafield(self, gid: str, ns: str, key: str, value: str, **kw: Any) -> dict:
        self.calls.append(("metafield", (gid, key, value)))
        return {}


@pytest.fixture()
def recorder(monkeypatch: pytest.MonkeyPatch) -> _Recorder:
    rec = _Recorder()
    monkeypatch.setattr(shopify_writer, "shopify_service", rec)
    return rec


def _fix(fix_type: str, text: str) -> FixSuggestion:
    return FixSuggestion(id="f1", gap_id="g1", fix_type=fix_type, proposed_text=text)  # type: ignore[arg-type]


async def test_copy_is_escaped_before_reaching_store(recorder: _Recorder) -> None:
    out = await apply_fix(
        _fix("copy_rewrite", "Roasted Monday.\n\n<script>alert(1)</script> & more"),
        target_product_gid=PRODUCT,
    )
    assert out.applied
    _, (gid, body) = recorder.calls[0]
    assert gid == PRODUCT
    assert "<script>" not in body
    assert body == "<p>Roasted Monday.</p><p>&lt;script&gt;alert(1)&lt;/script&gt; &amp; more</p>"


@pytest.mark.parametrize("text", ["", "   ", "x" * (shopify_writer.MAX_FIX_TEXT_CHARS + 1)])
async def test_empty_or_huge_text_never_written(recorder: _Recorder, text: str) -> None:
    with pytest.raises(FixValidationError):
        await apply_fix(_fix("copy_rewrite", text), target_product_gid=PRODUCT)
    assert recorder.calls == []


async def test_bad_target_gid_rejected(recorder: _Recorder) -> None:
    with pytest.raises(FixValidationError):
        await apply_fix(_fix("copy_rewrite", "ok"), target_product_gid="not-a-shopify-gid")
    with pytest.raises(FixValidationError):
        await apply_fix(_fix("policy_clarify", "ok"), target_page_gid=PRODUCT)
    assert recorder.calls == []


async def test_text_metafield_rejects_markup(recorder: _Recorder) -> None:
    with pytest.raises(FixValidationError):
        await apply_fix(_fix("metafield_add", "<img src=x onerror=alert(1)>"), target_product_gid=PRODUCT)
    await apply_fix(_fix("metafield_add", "Ships in 2 days, 3 < 5"), target_product_gid=PRODUCT)
    assert recorder.calls == [("metafield", (PRODUCT, "ai_readiness_fix", "Ships in 2 days, 3 < 5"))]


@pytest.mark.parametrize(
    "text",
    ['"just a string"', "not json", '{"name": "</script><script>alert(1)</script>"}'],
)
async def test_structured_data_validated(recorder: _Recorder, text: str) -> None:
    with pytest.raises(FixValidationError):
        await apply_fix(_fix("structured_data", text), target_product_gid=PRODUCT)
    assert recorder.calls == []


async def test_structured_data_ok(recorder: _Recorder) -> None:
    await apply_fix(_fix("structured_data", '{"@type": "Product", "name": "Decaf"}'), target_product_gid=PRODUCT)
    assert recorder.calls[0][0] == "metafield"


# ---------------------------------------------------------------------------
# App-level: missing config gives clear errors, WS origin allow-list
# ---------------------------------------------------------------------------


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    import api.auth_middleware as auth_mw
    import main
    from api import auth_deps
    from graph.neo4j_client import neo4j_client

    monkeypatch.setattr(auth_deps, "_AUTH_REQUIRED", False)
    monkeypatch.setattr(auth_mw, "_AUTH_REQUIRED", False)
    monkeypatch.setattr(neo4j_client, "uri", "")
    return TestClient(main.app)


def test_health_reports_neo4j_not_configured(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["neo4j"]["status"] == "not_configured"


def test_graph_route_gives_503_not_stack_trace(client: TestClient) -> None:
    r = client.get("/api/audit/demo-store")
    assert r.status_code == 503
    assert "NEO4J_URI" in r.json()["detail"]


def test_fix_generate_without_gemini_key_is_503(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from config.settings import settings

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    r = client.post("/api/fix/generate/g1", json={})
    assert r.status_code == 503
    assert "GEMINI_API_KEY" in r.json()["detail"]


def test_fix_apply_invalid_text_is_422(client: TestClient) -> None:
    body = {
        "fix": {"id": "f1", "gap_id": "g1", "fix_type": "copy_rewrite", "proposed_text": "  "},
        "target_product_gid": PRODUCT,
    }
    r = client.post("/api/fix/apply", json=body)
    assert r.status_code == 422
    assert "empty" in r.json()["detail"]


def test_fix_apply_blocked_when_auth_off_outside_local(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from config.settings import settings

    monkeypatch.setattr(settings, "ENV", "production")
    body = {
        "fix": {"id": "f1", "gap_id": "g1", "fix_type": "copy_rewrite", "proposed_text": "hi"},
        "target_product_gid": PRODUCT,
    }
    r = client.post("/api/fix/apply", json=body)
    assert r.status_code == 403


def test_ws_rejects_foreign_origin(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect) as exc, client.websocket_connect(
        "/api/interview/ws/s1", headers={"origin": "null"}
    ) as ws:
        ws.receive_json()
    assert exc.value.code == 4403


def test_ws_allows_frontend_origin(client: TestClient) -> None:
    from config.settings import settings

    with client.websocket_connect(
        "/api/interview/ws/s1", headers={"origin": settings.cors_origins[0]}
    ) as ws:
        assert ws.receive_json()["type"] == "session_open"
        ws.send_json({"type": "control", "action": "ping"})
        assert ws.receive_json()["type"] == "pong"
