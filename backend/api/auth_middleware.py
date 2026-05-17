"""ASGI middleware that enforces Firebase auth on /api/* routes.

Public whitelist (no token required):
    /health, /, /api/auth/*, /api/public_audit/*, /api/debug/*

`/api/debug/*` is reachable only when `settings.is_local` is true; in prod the
debug router is unmounted at startup, so this middleware never sees it.

Toggle the whole enforcement layer off with `AUTH_REQUIRED=false`
(local-demo escape hatch). Anything else and missing/invalid Bearer tokens
return a JSON 401 before the route is reached.
"""

from __future__ import annotations

import logging
import os
import re

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from services.firebase_service import firebase_service

logger = logging.getLogger("echomind.auth.mw")

_AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "true").lower() not in {"false", "0", "no"}

_PUBLIC_PATTERNS = [
    re.compile(r"^/$"),
    re.compile(r"^/health$"),
    re.compile(r"^/docs($|/)"),
    re.compile(r"^/openapi\.json$"),
    re.compile(r"^/redoc($|/)"),
    re.compile(r"^/api/auth(/|$)"),
    re.compile(r"^/api/public_audit(/|$)"),
    re.compile(r"^/api/debug(/|$)"),  # debug router itself is local-only-gated at mount time
]


def _is_public(path: str) -> bool:
    return any(p.match(path) for p in _PUBLIC_PATTERNS)


class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not _AUTH_REQUIRED:
            return await call_next(request)

        path = request.url.path
        # WebSocket scope reaches here as scope["type"] == "http" only for HTTP.
        # WS auth is handled separately in the WS endpoint via verify_ws_token.
        if request.scope.get("type") != "http":
            return await call_next(request)

        if _is_public(path):
            return await call_next(request)

        if not path.startswith("/api/"):
            return await call_next(request)

        auth = request.headers.get("authorization", "")
        if not auth.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing Authorization: Bearer <id_token>"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth.split(" ", 1)[1].strip()
        try:
            claims = firebase_service.verify_id_token(token)
        except Exception:
            logger.warning("auth.mw.verify_failed path=%s", path)
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired Firebase ID token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user = claims
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        is_prod = os.getenv("ENV", "local").lower() not in {"local", "dev", "development"}
        if is_prod:
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=63072000; includeSubDomains; preload",
            )
        return response
