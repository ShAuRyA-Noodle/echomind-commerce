"""Echomind Commerce - central settings.

All environment variables are loaded from `../.env` (one level up from the
backend package) via pydantic-settings. There is exactly ONE source of typing
truth for configuration; any new env var must be added here with a type and a
sensible default (or be marked required).

Usage:
    from config.settings import settings
    settings.GEMINI_API_KEY
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve `../.env` relative to this file so it works regardless of CWD.
_THIS_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _THIS_DIR.parent
_PROJECT_DIR = _BACKEND_DIR.parent
_ENV_FILE = _PROJECT_DIR / ".env"


class Settings(BaseSettings):
    """Typed view of every environment variable used by the backend."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---------- Gemini (direct Google AI Studio) ----------
    GEMINI_API_KEY: str = Field(default="", description="Google AI Studio API key")
    GEMINI_FLASH_MODEL: str = "gemini-2.5-flash"
    GEMINI_PRO_MODEL: str = "gemini-2.5-pro"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

    # ---------- Groq (fallback when Gemini Flash quota exhausted) ----------
    # Free tier: 14,400 req/day, 100K TPM. OpenAI-compatible endpoint.
    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_FLASH_MODEL: str = "llama-3.3-70b-versatile"

    # ---------- OpenRouter (agent swarm - free-tier-first per Decision Log #4) ----------
    # Model lineup verified live against /v1/models on 2026-05-01. The original
    # qwen-2.5-72b / deepseek-chat / gemini-2.0-flash-exp free aliases moved off
    # free tier; replaced with current frontier-grade `:free` equivalents.
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_APP_NAME: str = "Echomind Commerce"
    OPENROUTER_HTTP_REFERER: str = "https://github.com/echomind-commerce"
    OPENROUTER_AGENT_GPTOSS: str = "openai/gpt-oss-120b:free"
    OPENROUTER_AGENT_LLAMA: str = "meta-llama/llama-3.3-70b-instruct:free"
    OPENROUTER_AGENT_QWEN: str = "qwen/qwen3-next-80b-a3b-instruct:free"
    OPENROUTER_AGENT_GLM: str = "z-ai/glm-4.5-air:free"
    OPENROUTER_AGENT_ADVERSARIAL: str = "nousresearch/hermes-3-llama-3.1-405b:free"

    # ---------- Neo4j AuraDB ----------
    NEO4J_URI: str = ""
    NEO4J_USERNAME: str = ""
    NEO4J_PASSWORD: str = ""
    NEO4J_DATABASE: str = "neo4j"

    # ---------- Firebase (web client config) ----------
    FIREBASE_API_KEY: str = ""
    FIREBASE_AUTH_DOMAIN: str = ""
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""
    FIREBASE_MESSAGING_SENDER_ID: str = ""
    FIREBASE_APP_ID: str = ""
    FIREBASE_MEASUREMENT_ID: str = ""

    # ---------- Firebase Admin SDK ----------
    GOOGLE_APPLICATION_CREDENTIALS: str = "./firebase-admin-credentials.json"

    # ---------- Shopify ----------
    SHOPIFY_STORE_DOMAIN: str = ""
    SHOPIFY_API_KEY: str = ""
    SHOPIFY_API_SECRET: str = ""
    SHOPIFY_ADMIN_ACCESS_TOKEN: str = ""
    SHOPIFY_STOREFRONT_ACCESS_TOKEN: str = ""
    SHOPIFY_API_VERSION: str = "2025-01"

    # ---------- Backend ----------
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    ENV: str = "local"

    # ---------- Frontend (mirrored only for reference; not used server-side) ----------
    NEXT_PUBLIC_API_BASE_URL: str = "http://localhost:8000"
    NEXT_PUBLIC_WS_BASE_URL: str = "ws://localhost:8000"

    # ---------- Derived helpers ----------
    @property
    def project_dir(self) -> Path:
        return _PROJECT_DIR

    @property
    def is_local(self) -> bool:
        return self.ENV.lower() in {"local", "dev", "development"}

    @property
    def cors_origins(self) -> list[str]:
        # Frontend dev server + the production URL once deployed.
        origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
        if self.NEXT_PUBLIC_API_BASE_URL and self.NEXT_PUBLIC_API_BASE_URL not in origins:
            origins.append(self.NEXT_PUBLIC_API_BASE_URL)
        return origins


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a process-wide cached Settings instance."""
    return Settings()


# Convenience module-level singleton; safe to import directly.
settings: Settings = get_settings()
