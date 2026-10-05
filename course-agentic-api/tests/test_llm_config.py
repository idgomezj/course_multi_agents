import brotli
from httpx2._decoders import BrotliDecoder
from pydantic_ai.models.openai import OpenAIChatModel

from demo_app.manager import _manager_request_limit, build_agent
from demo_app.llm_config import (\n    _deepseek_http_client,\n    manager_model_options,\n    manager_model_status,\n    resolve_manager_model,\n)


def test_case0_manager_supports_four_llm_providers():
    options = {option.id: option for option in manager_model_options()}
    assert set(options) == {"google", "openai", "anthropic", "deepseek"}


def test_manager_model_status_does_not_expose_api_key_values(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "do-not-expose-this-value")
    status = manager_model_status()
    serialized = repr(status)
    assert "do-not-expose-this-value" not in serialized
    openai = next(item for item in status if item["id"] == "openai")
    assert openai["configured"] is True


def test_deepseek_uses_explicit_chat_model_and_disables_thinking(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    model, settings = resolve_manager_model("deepseek")
    assert isinstance(model, OpenAIChatModel)
    assert model.model_name == "deepseek-v4-flash"
    assert settings is not None
    assert settings["thinking"] is False


def test_manager_request_limit_defaults_and_is_bounded(monkeypatch):
    monkeypatch.delenv("MANAGER_REQUEST_LIMIT", raising=False)
    assert _manager_request_limit() == 75

    monkeypatch.setenv("MANAGER_REQUEST_LIMIT", "90")
    assert _manager_request_limit() == 90

    monkeypatch.setenv("MANAGER_REQUEST_LIMIT", "9999")
    assert _manager_request_limit() == 150

    monkeypatch.setenv("MANAGER_REQUEST_LIMIT", "not-a-number")
    assert _manager_request_limit() == 75


def test_case0_manager_agent_builds_with_deepseek(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    agent = build_agent("deepseek")
    assert agent is not None


def test_case0_deepseek_transport_does_not_negotiate_brotli():
    client = _deepseek_http_client()
    assert client.headers["accept-encoding"] == "gzip, deflate"


def test_case0_httpx2_brotli_decoder_matches_installed_brotli():
    payload = b'{"choices":[{"message":{"content":"ok"}}]}'
    compressed = brotli.compress(payload)
    decoder = BrotliDecoder()
    decoded = b"".join(decoder.decode(compressed)) + b"".join(decoder.flush())
    assert decoded == payload
