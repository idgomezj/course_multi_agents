import brotli
from httpx2._decoders import BrotliDecoder
from pydantic_ai.models.openai import OpenAIChatModel

from challenge.manager import _manager_request_limit, build_agent
from challenge.llm_config import _deepseek_http_client, manager_model_options, resolve_manager_model
from challenge.student_config import load_runtime_config


def test_manager_llm_providers_are_available():
    options = {option.id: option for option in manager_model_options()}
    assert set(options) == {"google", "openai", "anthropic", "deepseek"}
    assert options["openai"].model.startswith("openai:")
    assert options["anthropic"].model.startswith("anthropic:")
    assert options["deepseek"].model.startswith("deepseek:")


def test_deepseek_uses_explicit_chat_model_and_structured_output_settings(monkeypatch):
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


def test_all_team_manager_configs_build_with_deepseek_without_solution_artifacts(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    for team_id in [f"team_{i}" for i in range(1, 6)]:
        config = load_runtime_config(team_id)
        agent = build_agent("deepseek", config)
        assert agent is not None


def test_challenge_deepseek_transport_does_not_negotiate_brotli():
    client = _deepseek_http_client()
    assert client.headers["accept-encoding"] == "gzip, deflate"


def test_challenge_httpx2_brotli_decoder_matches_installed_brotli():
    payload = b'{"choices":[{"message":{"content":"ok"}}]}'
    compressed = brotli.compress(payload)
    decoder = BrotliDecoder()
    decoded = b"".join(decoder.decode(compressed)) + b"".join(decoder.flush())
    assert decoded == payload
