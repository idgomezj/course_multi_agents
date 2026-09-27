from demo_app.llm_config import manager_model_options, manager_model_status, resolve_manager_model


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


def test_deepseek_disables_thinking_for_structured_tool_output():
    model, settings = resolve_manager_model("deepseek")
    assert model.startswith("deepseek:")
    assert settings is not None
