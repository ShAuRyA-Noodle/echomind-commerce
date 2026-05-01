"""Echomind Commerce - Neo4j client wrapper.

Single async + sync Neo4j driver wrapper used by every read/write call from
the rest of the backend. The driver itself is lazily constructed and cached;
process-wide there is exactly one driver per (uri, user) pair.

Lifecycle:
    * `Neo4jClient.connect()` - initialize driver (idempotent).
    * `Neo4jClient.close()`   - close driver on shutdown.
    * `Neo4jClient.ping()`    - runs `RETURN 1` and returns a small dict
                                including the server version (used by /health).
"""

from __future__ import annotations

import logging
from typing import Any

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession, GraphDatabase

from config.settings import settings

logger = logging.getLogger("echomind.neo4j")


class Neo4jClient:
    """Async-first wrapper around the Neo4j Python driver."""

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> None:
        self.uri = uri or settings.NEO4J_URI
        self.username = username or settings.NEO4J_USERNAME
        self.password = password or settings.NEO4J_PASSWORD
        self.database = database or settings.NEO4J_DATABASE or "neo4j"
        self._driver: AsyncDriver | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> AsyncDriver:
        """Initialize the async driver if not already created. Idempotent."""
        if self._driver is not None:
            return self._driver
        if not self.uri:
            raise RuntimeError("Neo4j URI is not configured (NEO4J_URI is empty).")

        logger.info("neo4j.connect uri=%s db=%s", self.uri, self.database)
        self._driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password),
        )
        # Verify connectivity early so misconfig surfaces at startup, not first call.
        await self._driver.verify_connectivity()
        return self._driver

    async def close(self) -> None:
        """Close the driver (called from FastAPI lifespan shutdown)."""
        if self._driver is not None:
            logger.info("neo4j.close")
            await self._driver.close()
            self._driver = None

    @property
    def driver(self) -> AsyncDriver:
        """Return the live driver. Raises if `connect()` hasn't been called."""
        if self._driver is None:
            raise RuntimeError("Neo4jClient.connect() must be awaited before use.")
        return self._driver

    def session(self) -> AsyncSession:
        """Return a new async session bound to the configured database."""
        return self.driver.session(database=self.database)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    async def ping(self) -> dict[str, Any]:
        """Run `RETURN 1` to confirm connectivity and capture server version.

        Used by the `/health` endpoint. Never raises - returns a dict including
        a `status` key set to "ok" or "error".
        """
        try:
            await self.connect()
            async with self.session() as session:
                result = await session.run("RETURN 1 AS one")
                record = await result.single()
                summary = await result.consume()
                server_info = getattr(summary, "server", None)
                version = getattr(server_info, "agent", None) if server_info else None
                return {
                    "status": "ok",
                    "one": record["one"] if record else None,
                    "server": version,
                    "database": self.database,
                }
        except Exception as exc:  # noqa: BLE001 - health must be defensive
            logger.exception("neo4j.ping.failed")
            return {"status": "error", "error": repr(exc)}

    async def run(
        self,
        cypher: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Run a Cypher query and return the records as plain dicts.

        Thin convenience over `session.run` for read-or-small-write paths.
        Big writes should go through `graph/operations.py` for batching.
        """
        await self.connect()
        async with self.session() as session:
            result = await session.run(cypher, parameters or {})
            records = [record.data() async for record in result]
            return records

    # ------------------------------------------------------------------
    # Sync convenience (for one-shot bootstrap scripts only)
    # ------------------------------------------------------------------

    def sync_run(
        self,
        cypher: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a single statement synchronously. Used by bootstrap scripts."""
        with GraphDatabase.driver(self.uri, auth=(self.username, self.password)) as driver:
            with driver.session(database=self.database) as session:
                result = session.run(cypher, parameters or {})
                return [record.data() for record in result]


# Module-level singleton; bound to the configured environment.
neo4j_client = Neo4jClient()
