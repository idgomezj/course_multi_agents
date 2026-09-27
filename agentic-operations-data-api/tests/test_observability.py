import json
import logging

from app.observability import (
    StructuredFormatter,
    current_trace_id,
    new_trace_id,
    reset_trace_context,
    sanitize,
    set_trace_context,
)


def test_sanitize_redacts_secret_like_fields():
    payload = {
        "DEEPSEEK_API_KEY": "secret-value",
        "authorization": "Bearer abc",
        "nested": {"team_token": "token-value", "safe": 7},
    }
    cleaned = sanitize(payload)
    assert cleaned["DEEPSEEK_API_KEY"] == "<redacted>"
    assert cleaned["authorization"] == "<redacted>"
    assert cleaned["nested"]["team_token"] == "<redacted>"
    assert cleaned["nested"]["safe"] == 7


def test_trace_context_round_trip():
    trace_id = new_trace_id()
    tokens = set_trace_context(trace_id)
    try:
        assert current_trace_id() == trace_id
    finally:
        reset_trace_context(tokens)
    assert current_trace_id() == "-"


def test_structured_formatter_includes_source_location():
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname="/tmp/example_worker.py",
        lineno=42,
        msg="demo",
        args=(),
        exc_info=None,
        func="run_job",
    )
    record.event = "demo.event"
    record.event_data = {"safe": True}
    record.trace_id = "trace-123"
    record.span_id = "span-456"

    payload = json.loads(StructuredFormatter("test-service", json_mode=True).format(record))
    assert payload["file"] == "example_worker.py"
    assert payload["line"] == 42
    assert payload["function"] == "run_job"

    text_line = StructuredFormatter("test-service", json_mode=False).format(record)
    assert "[example_worker.py:42:run_job]" in text_line
