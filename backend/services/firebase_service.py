"""Echomind Commerce - Firebase Admin SDK service.

Initializes the Firebase Admin app from `GOOGLE_APPLICATION_CREDENTIALS`
once per process. Provides thin convenience wrappers over Auth, Firestore,
and Cloud Storage. The credentials JSON file lives outside the repo and is
gitignored; if it's missing we log a warning and let downstream calls fail
loudly rather than silently faking auth.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import firebase_admin
from firebase_admin import auth as fb_auth
from firebase_admin import credentials, firestore, storage

from config.settings import settings

logger = logging.getLogger("echomind.firebase")


class FirebaseService:
    """Firebase Admin lifecycle + thin convenience methods."""

    def __init__(self) -> None:
        self._app: firebase_admin.App | None = None
        self._firestore_client: Any | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> firebase_admin.App | None:
        """Initialize firebase-admin once. Idempotent. Returns the app or None."""
        if self._app is not None:
            return self._app

        creds_path = Path(settings.GOOGLE_APPLICATION_CREDENTIALS).expanduser()
        if not creds_path.is_absolute():
            creds_path = settings.project_dir / creds_path

        if not creds_path.exists():
            logger.warning(
                "firebase.init.missing_credentials path=%s - "
                "Auth/Firestore/Storage calls will fail until provided",
                creds_path,
            )
            return None

        try:
            cred = credentials.Certificate(str(creds_path))
            options = {}
            if settings.FIREBASE_STORAGE_BUCKET:
                options["storageBucket"] = settings.FIREBASE_STORAGE_BUCKET
            if settings.FIREBASE_PROJECT_ID:
                options["projectId"] = settings.FIREBASE_PROJECT_ID
            self._app = firebase_admin.initialize_app(cred, options)
            logger.info(
                "firebase.init project=%s bucket=%s",
                settings.FIREBASE_PROJECT_ID,
                settings.FIREBASE_STORAGE_BUCKET,
            )
        except ValueError:
            # Already initialized in this process.
            self._app = firebase_admin.get_app()
        return self._app

    def shutdown(self) -> None:
        """Tear down the Firebase Admin app on graceful shutdown."""
        if self._app is not None:
            try:
                firebase_admin.delete_app(self._app)
            except Exception:  # noqa: BLE001
                logger.exception("firebase.shutdown.failed")
            self._app = None

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def verify_id_token(self, id_token: str) -> dict[str, Any]:
        """Verify a Firebase ID token and return the decoded claims."""
        self.initialize()
        return fb_auth.verify_id_token(id_token)

    # ------------------------------------------------------------------
    # Firestore
    # ------------------------------------------------------------------

    def firestore_client(self) -> Any:
        """Return a memoized Firestore client (raises if not initialized)."""
        if self._firestore_client is None:
            self.initialize()
            self._firestore_client = firestore.client()
        return self._firestore_client

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    def storage_bucket(self) -> Any:
        """Return the default Cloud Storage bucket."""
        self.initialize()
        return storage.bucket()


firebase_service = FirebaseService()
