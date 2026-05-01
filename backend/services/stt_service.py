"""Echomind Commerce - Google STT V2 streaming wrapper (placeholder).

Real client wiring lands with the live-interview milestone. The class
signature mirrors the `long`-model + auto-punctuation + word-time-offsets
configuration documented in WINNING_PLAN §5.3 / §23.1.
"""

from __future__ import annotations

import logging
from typing import AsyncIterator

logger = logging.getLogger("echomind.stt")


class STTService:
    """Google Cloud STT V2 streaming client (long model)."""

    def __init__(
        self,
        model: str = "long",
        language_code: str = "en-US",
        sample_rate_hertz: int = 16000,
    ) -> None:
        self.model = model
        self.language_code = language_code
        self.sample_rate_hertz = sample_rate_hertz

    async def stream_transcribe(
        self,
        audio_chunks: AsyncIterator[bytes],
    ) -> AsyncIterator[dict]:
        """Stream PCM audio chunks in, yield interim/final transcripts out.

        Yielded events match the `out:` schema for `/api/interview/ws/{session_id}`
        in WINNING_PLAN §5.5: `interim_transcript`, `final_transcript`, etc.
        """
        logger.info("stt.stream_transcribe model=%s lang=%s", self.model, self.language_code)
        # Placeholder - real google-cloud-speech wiring lands later.
        return  # type: ignore[return-value]
        yield {}  # pragma: no cover - keeps async-generator typing happy

    async def close(self) -> None:
        """Release any active streaming connection."""
        return None


stt_service = STTService()
