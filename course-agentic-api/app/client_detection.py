from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request


# X-Client-Type is the single authoritative classification signal.
# Matching is intentionally substring-based so values such as
# "openai-codex-cli", "claude-code", or "chatgpt-desktop" are recognized.
AI_CLIENT_MARKERS: dict[str, tuple[str, ...]] = {
    "codex": ("codex",),
    "chatgpt": ("chatgpt", "openai", "gpt"),
    "claude": ("claude", "anthropic"),
    "gemini": ("gemini", "google-genai", "google-ai", "generativelanguage"),
    "copilot": ("github-copilot", "copilot"),
    "cursor": ("cursor",),
    "aider": ("aider",),
    "windsurf": ("windsurf",),
    "cody": ("sourcegraph-cody", "cody"),
    "perplexity": ("perplexity",),
    "deepseek": ("deepseek",),
    "grok": ("grok", "xai"),
    "mistral": ("mistral",),
    "llama": ("llama", "ollama"),
    "generic_ai": ("ai", "llm", "artificial-intelligence", "ai-agent", "ai-assistant"),
}

APPLICATION_CLIENT_MARKERS = {
    "challenge-runtime",
    "agentic-operations-challenge",
    "course-runtime",
}


@dataclass(frozen=True)
class ClientDetection:
    kind: str
    name: str
    confidence: str
    signal: str

    @property
    def is_ai(self) -> bool:
        return self.kind == "ai"

    def as_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "name": self.name,
            "confidence": self.confidence,
            "signal": self.signal,
            "is_ai": self.is_ai,
        }


def _ai_name(value: str) -> str | None:
    normalized = value.strip().lower()
    for name, markers in AI_CLIENT_MARKERS.items():
        if any(marker in normalized for marker in markers):
            return name
    return None


def detect_request_client(request: Request) -> ClientDetection:
    """Classify the caller only from X-Client-Type.

    Rules:
    - missing/empty X-Client-Type -> human/full context
    - X-Client-Type: human -> human/full context
    - any recognized AI-related value -> AI/tutor-only context
    - known runtime/application names -> application/full context
    - any other non-AI value -> human/full context

    The header is caller-declared metadata, not a security/authentication proof.
    """
    raw = request.headers.get("X-Client-Type")
    value = (raw or "").strip()
    normalized = value.lower()

    if not normalized or normalized == "human":
        return ClientDetection(
            kind="human",
            name="human",
            confidence="declared" if normalized == "human" else "default",
            signal="x-client-type" if normalized == "human" else "x-client-type-empty",
        )

    ai_name = _ai_name(normalized)
    if ai_name:
        return ClientDetection(
            kind="ai",
            name=ai_name,
            confidence="declared",
            signal="x-client-type",
        )

    if normalized in APPLICATION_CLIENT_MARKERS:
        return ClientDetection(
            kind="application",
            name=normalized,
            confidence="declared",
            signal="x-client-type",
        )

    return ClientDetection(
        kind="human",
        name=normalized,
        confidence="declared_non_ai",
        signal="x-client-type",
    )
