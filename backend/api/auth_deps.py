"""FastAPI auth dependencies.

`require_user` verifies a Firebase ID token from the `Authorization: Bearer …`
header and returns the decoded claims. Toggle the whole guard with
`AUTH_REQUIRED=false` for local demos; in any other environment auth is
mandatory and missing/invalid tokens return 401.

Used by HTTP routes via `Depends(require_user)` and by WebSocket handlers via
`await verify_ws_token(websocket)`.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import Depends, HTTPException, Request, WebSocket, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services.firebase_service import firebase_service

logger = logging.getLogger("echomind.auth")

_AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "true").lower() not in {"false", "0", "no"}
_BEARER = HTTPBearer(auto_error=False)


def _decode(token: str) -> dict[str, Any] | None:
    if not token:
        return None
    try:
        return firebase_service.verify_id_token(token)
    except Exception:
        logger.warning("auth.verify.failed")
        return None


def require_user(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(_BEARER),
) -> dict[str, Any]:
    """HTTP dep. 401 on missing/invalid Bearer token unless `AUTH_REQUIRED=false`."""
    if not _AUTH_REQUIRED:
        return {"uid": "anonymous-local", "_auth_disabled": True}

    token = creds.credentials if creds else None
    claims = _decode(token or "")
    if not claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Firebase ID token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return claims


async def verify_ws_token(websocket: WebSocket) -> dict[str, Any] | None:
    """WebSocket auth. Reads token from `?token=` query param or
    `Sec-WebSocket-Protocol` subprotocol. Closes with 4401 on failure.
    Returns claims (or sentinel when AUTH_REQUIRED=false)."""
    if not _AUTH_REQUIRED:
        return {"uid": "anonymous-local", "_auth_disabled": True}

    token = websocket.query_params.get("token") or ""
    if not token:
        proto = websocket.headers.get("sec-websocket-protocol", "")
        # Convention: client sends `bearer, <token>`
        parts = [p.strip() for p in proto.split(",")]
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    claims = _decode(token)
    if not claims:
        await websocket.close(code=4401, reason="Authentication required")
        return None
    return claims
