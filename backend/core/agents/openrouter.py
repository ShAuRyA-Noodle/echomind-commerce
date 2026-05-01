"""Echomind Commerce - OpenRouter client for the agent swarm.

OpenAI-compatible client wrapping all four free-tier swarm models. Per-model
configuration lives in `config/settings.py`; the swarm runner (next file)
fans out one call per model per buyer prompt with concurrency control.

Free-tier lineup (verified live 2026-05-01):
    * `openai/gpt-oss-120b:free`               - GPT-class representation
    * `meta-llama/llama-3.3-70b-instruct:free` - Llama family
    * `qwen/qwen3-next-80b-a3b-instruct:free`  - Qwen ecosystem (80B MoE)
    * `z-ai/glm-4.5-air:free`                  - Chinese frontier

Adversarial mode adds:
    * `nousresearch/hermes-3-llama-3.1-405b:free` - 405B for hostile prompts

Resilience:
    * tenacity 3-retry with exp backoff
    * 30s timeout per call
    * provider-specific error classification - rate-limit, parse-failed,
      network - all captured into a typed `AgentResponse`
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError as OpenAIRateLimitError
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import settings
from services.llm_service import safe_json_loads

logger = logging.getLogger("echomind.agents.openrouter")


# Mapping from a logical "swarm slot" to the configured model id.
def swarm_model_lineup() -> dict[str, str]:
    return {
        "gpt_oss":   settings.OPENROUTER_AGENT_GPTOSS,
        "llama":     settings.OPENROUTER_AGENT_LLAMA,
        "qwen":      settings.OPENROUTER_AGENT_QWEN,
        "glm":       settings.OPENROUTER_AGENT_GLM,
    }


def adversarial_model() -> str:
    return settings.OPENROUTER_AGENT_ADVERSARIAL


_TRANSIENT_EXC: tuple[type[BaseException], ...] = (
    OpenAIRateLimitError,
    APITimeoutError,
    APIError,
    TimeoutError,
    ConnectionError,
)


@dataclass(frozen=True)
class AgentCall:
    """Single agent invocation: one swarm slot × one buyer prompt."""

    slot: str       # logical name (gpt_oss / llama / qwen / glm)
    model: str      # OpenRouter model id (e.g., "openai/gpt-oss-120b:free")
    system_prompt: str
    user_prompt: str
    max_tokens: int = 600
    temperature: float = 0.7


@dataclass
class AgentResponse:
    """Captured result from one AgentCall."""

    slot: str
    model: str
    response_text: str
    parsed_json: dict[str, Any] | None
    parse_failed: bool
    latency_ms: int
    error: str | None = None


_async_client: AsyncOpenAI | None = None


def _client() -> AsyncOpenAI:
    global _async_client
    if _async_client is None:
        _async_client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY or "missing",
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers={
                # OpenRouter recommends sending these so the call shows up
                # under our app's leaderboard slot.
                "HTTP-Referer": settings.OPENROUTER_HTTP_REFERER,
                "X-Title": settings.OPENROUTER_APP_NAME,
            },
        )
    return _async_client


async def call_one(call: AgentCall) -> AgentResponse:
    """Single OpenRouter chat-completion. JSON-parses if the response is JSON."""
    started = time.perf_counter()
    last_exc: BaseException | None = None
    text = ""
    try:
        async for attempt in AsyncRetrying(
            reraise=True,
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            retry=retry_if_exception_type(_TRANSIENT_EXC),
        ):
            with attempt:
                completion = await _client().chat.completions.create(
                    model=call.model,
                    messages=[
                        {"role": "system", "content": call.system_prompt},
                        {"role": "user", "content": call.user_prompt},
                    ],
                    max_tokens=call.max_tokens,
                    temperature=call.temperature,
                )
                if completion.choices:
                    text = completion.choices[0].message.content or ""
                break
    except Exception as exc:  # noqa: BLE001 - surface, don't crash the swarm
        last_exc = exc
        logger.warning("openrouter.call_failed slot=%s model=%s exc=%r", call.slot, call.model, exc)

    latency_ms = int((time.perf_counter() - started) * 1000)
    parsed = safe_json_loads(text) if text else None
    return AgentResponse(
        slot=call.slot,
        model=call.model,
        response_text=text,
        parsed_json=parsed if isinstance(parsed, dict) else None,
        parse_failed=text != "" and not isinstance(parsed, dict),
        latency_ms=latency_ms,
        error=repr(last_exc) if last_exc else None,
    )


__all__ = [
    "swarm_model_lineup",
    "adversarial_model",
    "AgentCall",
    "AgentResponse",
    "call_one",
]
