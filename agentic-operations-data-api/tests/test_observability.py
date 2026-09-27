from app.observability import (
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
