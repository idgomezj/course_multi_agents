from __future__ import annotations

import json
import logging
import os
import traceback
import uuid
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_TRACE_ID: ContextVar[str] = ContextVar("trace_id", default="-")
_SPAN_ID: ContextVar[str] = ContextVar("span_id", default="-")

_SENSITIVE_MARKERS = (
    "authorization",
    "api_key",
    "apikey",
    "token",
    "password",
    "passwd",
    "secret",
    "cookie",
    "credential",
)


def _truthy(name: str, default: str = "true") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def current_trace_id() -> str:
    return _TRACE_ID.get()


def current_span_id() -> str:
    return _SPAN_ID.get()


def new_trace_id() -> str:
    return uuid.uuid4().hex


def new_span_id() -> str:
    return uuid.uuid4().hex[:16]


def set_trace_context(trace_id: str | None = None, span_id: str | None = None) -> tuple[Token, Token]:
    trace_token = _TRACE_ID.set(trace_id or new_trace_id())
    span_token = _SPAN_ID.set(span_id or new_span_id())
    return trace_token, span_token


def reset_trace_context(tokens: tuple[Token, Token]) -> None:
    trace_token, span_token = tokens
    _TRACE_ID.reset(trace_token)
    _SPAN_ID.reset(span_token)


def set_span_id(span_id: str | None = None) -> Token:
    return _SPAN_ID.set(span_id or new_span_id())


def reset_span_id(token: Token) -> None:
    _SPAN_ID.reset(token)


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in _SENSITIVE_MARKERS)


def sanitize(value: Any, *, depth: int = 0) -> Any:
    """Redact secrets and keep log payloads bounded/readable."""
    if depth > 6:
        return "<max-depth>"

    max_chars = int(os.getenv("LOG_MAX_VALUE_CHARS", "4000"))
    max_items = int(os.getenv("LOG_MAX_COLLECTION_ITEMS", "100"))

    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for i, (key, item) in enumerate(value.items()):
            if i >= max_items:
                out["<truncated>"] = f"{len(value) - max_items} additional entries"
                break
            key_str = str(key)
            out[key_str] = "<redacted>" if _is_sensitive_key(key_str) else sanitize(item, depth=depth + 1)
        return out

    if isinstance(value, (list, tuple, set)):
        items = list(value)
        sanitized = [sanitize(item, depth=depth + 1) for item in items[:max_items]]
        if len(items) > max_items:
            sanitized.append(f"<truncated {len(items) - max_items} additional items>")
        return sanitized

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, str):
        return value if len(value) <= max_chars else value[:max_chars] + f"...<truncated {len(value)-max_chars} chars>"

    if isinstance(value, (int, float, bool)) or value is None:
        return value

    try:
        text = str(value)
    except Exception:
        return f"<unserializable {type(value).__name__}>"
    return text if len(text) <= max_chars else text[:max_chars] + "...<truncated>"


class StructuredFormatter(logging.Formatter):
    def __init__(self, service_name: str, json_mode: bool):
        super().__init__()
        self.service_name = service_name
        self.json_mode = json_mode

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        event = getattr(record, "event", record.getMessage())
        data = sanitize(getattr(record, "event_data", {}))
        trace_id = getattr(record, "trace_id", current_trace_id())
        span_id = getattr(record, "span_id", current_span_id())

        if self.json_mode:
            payload = {
                "timestamp": timestamp,
                "level": record.levelname,
                "service": self.service_name,
                "logger": record.name,
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
                "trace_id": trace_id,
                "span_id": span_id,
                "event": event,
                "data": data,
            }
            if record.exc_info:
                payload["exception"] = "".join(traceback.format_exception(*record.exc_info))
            return json.dumps(payload, default=str, ensure_ascii=False)

        suffix = ""
        if data:
            suffix = " " + json.dumps(data, default=str, ensure_ascii=False)
        message = (
            f"{timestamp} {record.levelname:<8} "
            f"[{self.service_name}] [{record.filename}:{record.lineno}:{record.funcName}] "
            f"[trace={trace_id}] [span={span_id}] {event}{suffix}"
        )
        if record.exc_info:
            message += "\n" + "".join(traceback.format_exception(*record.exc_info))
        return message


def setup_logging(service_name: str) -> logging.Logger:
    """Configure safe console + rotating-file logs exactly once per process."""
    root = logging.getLogger()
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    root.setLevel(level)

    marker = f"_agentic_logging_{service_name}"
    if not getattr(root, marker, False):
        json_mode = os.getenv("LOG_FORMAT", "text").strip().lower() == "json"
        formatter = StructuredFormatter(service_name, json_mode=json_mode)

        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(formatter)
        root.addHandler(console)

        log_file = os.getenv("LOG_FILE", "").strip()
        if log_file:
            path = Path(log_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                path,
                maxBytes=int(os.getenv("LOG_MAX_BYTES", "10485760")),
                backupCount=int(os.getenv("LOG_BACKUP_COUNT", "5")),
                encoding="utf-8",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)

        setattr(root, marker, True)

    logger = logging.getLogger(service_name)
    log_event(
        logger,
        "logging.configured",
        level=logging.INFO,
        log_level=level_name,
        log_format=os.getenv("LOG_FORMAT", "text"),
        log_file=os.getenv("LOG_FILE", ""),
        log_payloads=_truthy("LOG_PAYLOADS", "true"),
    )
    return logger


def log_event(logger: logging.Logger, event: str, *, level: int = logging.INFO, **fields: Any) -> None:
    if not logger.isEnabledFor(level):
        return

    if not _truthy("LOG_PAYLOADS", "true"):
        payload_fields = {"summary": fields.get("summary")} if "summary" in fields else {}
    else:
        payload_fields = fields

    logger.log(
        level,
        event,
        extra={
            "event": event,
            "event_data": sanitize(payload_fields),
            "trace_id": current_trace_id(),
            "span_id": current_span_id(),
        },
        stacklevel=2,
    )


def log_exception(logger: logging.Logger, event: str, **fields: Any) -> None:
    logger.error(
        event,
        exc_info=True,
        extra={
            "event": event,
            "event_data": sanitize(fields),
            "trace_id": current_trace_id(),
            "span_id": current_span_id(),
        },
        stacklevel=2,
    )
