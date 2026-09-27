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
