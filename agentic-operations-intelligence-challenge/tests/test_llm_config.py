from challenge.manager import _manager_request_limit
from challenge.llm_config import manager_model_options, resolve_manager_model


def test_manager_llm_providers_are_available():
    options = {option.id: option for option in manager_model_options()}
    assert set(options) == {"google", "openai", "anthropic", "deepseek"}
    assert options["openai"].model.startswith("openai:")
    assert options["anthropic"].model.startswith("anthropic:")
    assert options["deepseek"].model.startswith("deepseek:")


def test_deepseek_uses_structured_output_friendly_settings():
    model, settings = resolve_manager_model("deepseek")
    assert model.startswith("deepseek:")
    assert settings is not None


def test_manager_request_limit_defaults_and_is_bounded(monkeypatch):
    monkeypatch.delenv("MANAGER_REQUEST_LIMIT", raising=False)
    assert _manager_request_limit() == 75

    monkeypatch.setenv("MANAGER_REQUEST_LIMIT", "90")
    assert _manager_request_limit() == 90

    monkeypatch.setenv("MANAGER_REQUEST_LIMIT", "9999")
    assert _manager_request_limit() == 150

    monkeypatch.setenv("MANAGER_REQUEST_LIMIT", "not-a-number")
    assert _manager_request_limit() == 75
