from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from typing import Any

from httpx2 import AsyncClient
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIChatModelSettings
from pydantic_ai.providers.deepseek import DeepSeekProvider

from .observability import log_event

logger = logging.getLogger(__name__)

_DEEPSEEK_ACCEPT_ENCODING = "gzip, deflate"
_DEEPSEEK_HTTP_CLIENT: AsyncClient | None = None


def _deepseek_http_client() -> AsyncClient:
    """Return a DeepSeek HTTP client that does not negotiate Brotli.

    Older Brotli bindings can be importable while lacking the output-buffer
    keyword required by httpx2, causing successful API responses to fail during
    decompression. DeepSeek works with gzip/deflate, so this transport avoids
    that environment-dependent failure.
    """
    global _DEEPSEEK_HTTP_CLIENT
    if _DEEPSEEK_HTTP_CLIENT is None:
        _DEEPSEEK_HTTP_CLIENT = AsyncClient(
            headers={"Accept-Encoding": _DEEPSEEK_ACCEPT_ENCODING},
        )
    return _DEEPSEEK_HTTP_CLIENT


@dataclass(frozen=True)
class ManagerModelOption:
    id: str
    label: str
    provider: str
    model: str
    api_key_env: str


def _model_value(env_name: str, default: str) -> str:
    return os.getenv(env_name, default).strip()


def manager_model_options() -> list[ManagerModelOption]:
    """Return the supported Manager LLM providers without exposing credentials."""
    return [
        ManagerModelOption(
            id="google",
            label="Google Gemini",
            provider="google",
            model=_model_value("GOOGLE_MANAGER_MODEL", "google:gemini-2.5-flash"),
            api_key_env="GOOGLE_API_KEY",
        ),
        ManagerModelOption(
            id="openai",
            label="OpenAI / ChatGPT",
            provider="openai",
            model=_model_value("OPENAI_MANAGER_MODEL", "openai:gpt-5.6-sol"),
            api_key_env="OPENAI_API_KEY",
        ),
        ManagerModelOption(
            id="anthropic",
            label="Anthropic Claude",
            provider="anthropic",
            model=_model_value("ANTHROPIC_MANAGER_MODEL", "anthropic:claude-sonnet-4-6"),
            api_key_env="ANTHROPIC_API_KEY",
        ),
        ManagerModelOption(
            id="deepseek",
            label="DeepSeek",
            provider="deepseek",
            model=_model_value("DEEPSEEK_MANAGER_MODEL", "deepseek:deepseek-v4-flash"),
            api_key_env="DEEPSEEK_API_KEY",
        ),
    ]


def _option_map() -> dict[str, ManagerModelOption]:
    return {option.id: option for option in manager_model_options()}


def default_manager_model_id() -> str:
    requested = os.getenv("MANAGER_PROVIDER", "").strip().lower()
    if requested in _option_map():
        return requested

    legacy_model = os.getenv("MANAGER_MODEL", "").strip()
    if legacy_model:
        prefix = legacy_model.split(":", 1)[0].lower()
        return {
            "google": "google",
            "openai": "openai",
            "anthropic": "anthropic",
            "deepseek": "deepseek",
        }.get(prefix, "google")

    return "google"


def resolve_manager_model(model_id: str | None = None) -> tuple[Any, Any | None]:
    """Resolve a UI/provider id to the Pydantic AI model string and optional settings.

    MANAGER_MODEL remains supported as a legacy explicit override when no model_id
    is supplied. For DeepSeek V4, thinking is disabled because structured output
    and forced tool use are more reliable in that mode.
    """
    if model_id is None:
        legacy_model = os.getenv("MANAGER_MODEL", "").strip()
        if legacy_model:
            model = legacy_model
        else:
            option = _option_map()[default_manager_model_id()]
            model = option.model
    else:
        normalized = model_id.strip().lower()
        options = _option_map()
        if normalized not in options:
            raise ValueError(
                f"Unsupported manager model '{model_id}'. "
                f"Choose one of: {', '.join(sorted(options))}"
            )
        model = options[normalized].model

    settings: Any | None = None
    resolved_model: Any = model
    if model.startswith("deepseek:"):
        deepseek_model_name = model.split(":", 1)[1]
        resolved_model = OpenAIChatModel(
            deepseek_model_name,
            provider=DeepSeekProvider(http_client=_deepseek_http_client()),
        )
        settings = OpenAIChatModelSettings(thinking=False)

    provider = model.split(":", 1)[0] if ":" in model else "custom"
    option = next((x for x in manager_model_options() if x.id == (model_id or default_manager_model_id())), None)
    log_event(
        logger,
        "llm.model.resolved",
        requested_model_id=model_id,
        resolved_model=model,
        provider=provider,
        configured=bool(os.getenv(option.api_key_env)) if option else None,
        has_custom_settings=settings is not None,
    )
    return resolved_model, settings


def manager_model_status() -> list[dict[str, Any]]:
    default_id = default_manager_model_id()
    status = [
        {
            "id": option.id,
            "label": option.label,
            "provider": option.provider,
            "model": option.model,
            "api_key_env": option.api_key_env,
            "configured": bool(os.getenv(option.api_key_env)),
            "default": option.id == default_id,
        }
        for option in manager_model_options()
    ]
    log_event(
        logger,
        "llm.providers.status",
        level=logging.DEBUG,
        default_model_id=default_id,
        providers=[{"id": x["id"], "model": x["model"], "configured": x["configured"]} for x in status],
    )
    return status
