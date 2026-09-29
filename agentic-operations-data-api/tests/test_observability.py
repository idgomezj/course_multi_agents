import logging

from app.observability import (
    StructuredFormatter,
    current_trace_id,
    log_event,
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


def test_structured_formatter_uses_requested_text_field_order():
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

    text_line = StructuredFormatter("test-service", use_colors=False).format(record)
    assert text_line.startswith("<INFO> ")
    assert "[trace_id:trace-123]" in text_line
    assert "[span_id:span-456]" in text_line
    assert "<example_worker.py:42>" in text_line
    assert "<demo.event safe=true>" in text_line

    # Required field order: <level> time [trace_id:] [span_id:] <file> <body>.
    assert text_line.index("[trace_id:") < text_line.index("[span_id:")
    assert text_line.index("[span_id:") < text_line.index("<example_worker.py:42>")
    assert text_line.index("<example_worker.py:42>") < text_line.index("<demo.event")


def test_structured_formatter_colors_level_prefix():
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
    record.event_data = {}
    record.trace_id = "-"
    record.span_id = "-"

    colored = StructuredFormatter("test-service", use_colors=True).format(record)
    plain = StructuredFormatter("test-service", use_colors=False).format(record)

    assert colored.startswith("\x1b[32m<INFO>")
    assert "\x1b[0m" in colored
    assert plain.startswith("<INFO> ")
    assert "\x1b[" not in plain



def test_log_event_uses_real_caller_location():
    records = []

    class CaptureHandler(logging.Handler):
        def emit(self, record):
            records.append(record)

    logger = logging.getLogger("test.observability.callsite")
    handler = CaptureHandler()
    previous_level = logger.level
    previous_propagate = logger.propagate
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
    try:
        log_event(logger, "callsite.test", answer=42)
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate

    assert len(records) == 1
    assert records[0].filename == "test_observability.py"
    assert records[0].funcName == "test_log_event_uses_real_caller_location"
