"""Echomind Commerce - audio I/O service (placeholder).

Will own browser-side audio negotiation (chunk size, mime, resampling) when
the live-interview milestone lands. Today this file exists so that
`from services.audio_service import audio_service` works in calling code.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("echomind.audio")


class AudioService:
    """Audio chunk handling: resample, normalize, route to STT."""

    def __init__(self, target_sample_rate: int = 16000) -> None:
        self.target_sample_rate = target_sample_rate

    async def normalize_chunk(self, chunk: bytes, *, source_sample_rate: int) -> bytes:
        """Resample/normalize a single PCM chunk to `target_sample_rate`."""
        logger.debug(
            "audio.normalize_chunk bytes=%d src=%d -> dst=%d",
            len(chunk),
            source_sample_rate,
            self.target_sample_rate,
        )
        # Placeholder pass-through; real DSP lands later.
        return chunk


audio_service = AudioService()
