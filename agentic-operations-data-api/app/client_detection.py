from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request


AI_CLIENT_MARKERS: dict[str, tuple[str, ...]] = {
    "codex": ("codex", "openai-codex"),
    "chatgpt": ("chatgpt", "openai"),
    "claude": ("claude", "anthropic"),
    "gemini": ("gemini", "google-genai", "google-ai", "generativelanguage"),
    "copilot": ("github-copilot", "copilot"),
    "cursor": ("cursor",),
    "aider": ("aider",),
    "windsurf": ("windsurf",),
    "cody": ("sourcegraph-cody", "cody"),
    "perplexity": ("perplexity",),
}

APPLICATION_CLIENT_MARKERS = {
    "challenge-runtime",
    "agentic-operations-challenge",
    "course-runtime",
}

HUMAN_CLIENT_MARKERS = {
    "human",
    "browser",
    "person",
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


def _classify(value: str) -> tuple[str, str] | None:
    normalized = value.strip().lower()
    if not normalized:
        return None

    if normalized in APPLICATION_CLIENT_MARKERS:
        return ("application", normalized)
    if normalized in HUMAN_CLIENT_MARKERS:
        return ("human_or_unknown", normalized)

    for name, markers in AI_CLIENT_MARKERS.items():
        if any(marker in normalized for marker in markers):
            return ("ai", name)
    return None


def detect_request_client(request: Request) -> ClientDetection:
    """Best-effort client classification.

    HTTP headers are assertions, not proof of identity. Explicit course headers
    are preferred; User-Agent matching is only a heuristic fallback.
    """
    explicit_headers = (
        ("x-client-type", request.headers.get("X-Client-Type")),
        ("x-ai-client", request.headers.get("X-AI-Client")),
    )
    for header_name, value in explicit_headers:
        if not value:
            continue
        classified = _classify(value)
        if classified:
            kind, name = classified
            return ClientDetection(
                kind=kind,
                name=name,
                confidence="declared",
                signal=header_name,
            )
        return ClientDetection(
            kind="human_or_unknown",
            name=value.strip().lower(),
            confidence="declared_unknown",
            signal=header_name,
        )

    user_agent = request.headers.get("User-Agent", "")
    classified = _classify(user_agent)
    if classified:
        kind, name = classified
        return ClientDetection(
            kind=kind,
            name=name,
            confidence="heuristic",
            signal="user-agent",
        )

    return ClientDetection(
        kind="human_or_unknown",
        name="unidentified",
        confidence="unknown",
        signal="none",
    )
