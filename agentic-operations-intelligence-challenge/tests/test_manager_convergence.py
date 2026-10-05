from pydantic_ai import ModelMessage, ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.usage import UsageLimits

from challenge.manager import _manager_research_step_limit, build_agent
from challenge.runtime import RuntimeDeps
from challenge.schemas import MonthlyOperationsPlan


FINAL_PLAN = {
    "team_id": "team_1",
    "scenario_id": "T1-TEST",
    "production_plan": [],
    "purchase_orders": [],
    "actions": [],
    "assumptions": ["bounded convergence test"],
    "explanation": "Finalized after the investigation tool budget closed.",
}


class RepeatingToolModel:
    """Keep requesting a function tool until the Manager hides function tools."""

    def __init__(self) -> None:
        self.requests = 0
        self.function_tool_counts: list[int] = []

    def __call__(self, _messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
        self.requests += 1
        self.function_tool_counts.append(len(info.function_tools))

        if info.function_tools:
            assert any(tool.name == "get_student_configuration" for tool in info.function_tools)
            return ModelResponse(parts=[ToolCallPart("get_student_configuration", {})])

        assert info.output_tools, "Output tool must remain available during finalization."
        return ModelResponse(
            parts=[ToolCallPart(info.output_tools[0].name, FINAL_PLAN)]
        )


def _deps() -> RuntimeDeps:
    return RuntimeDeps(
        team_id="team_1",
        case={},
        scenario={"id": "T1-TEST"},
        rag=object(),
        skills=object(),
        models=object(),
        student_config={},
    )


def test_manager_switches_from_research_to_output_only_and_converges(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "offline-test-key")
    monkeypatch.setenv("MANAGER_RESEARCH_STEP_LIMIT", "4")

    model = RepeatingToolModel()
    agent = build_agent("deepseek", {})

    with agent.override(model=FunctionModel(model)):
        result = agent.run_sync(
            "Exercise bounded manager convergence.",
            deps=_deps(),
            usage_limits=UsageLimits(request_limit=10),
        )

    assert isinstance(result.output, MonthlyOperationsPlan)
    assert result.output.scenario_id == "T1-TEST"
    assert model.function_tool_counts[-1] == 0
    assert model.requests <= 6


def test_manager_research_step_limit_is_bounded(monkeypatch):
    monkeypatch.delenv("MANAGER_RESEARCH_STEP_LIMIT", raising=False)
    assert _manager_research_step_limit() == 12

    monkeypatch.setenv("MANAGER_RESEARCH_STEP_LIMIT", "2")
    assert _manager_research_step_limit() == 4

    monkeypatch.setenv("MANAGER_RESEARCH_STEP_LIMIT", "999")
    assert _manager_research_step_limit() == 24

    monkeypatch.setenv("MANAGER_RESEARCH_STEP_LIMIT", "invalid")
    assert _manager_research_step_limit() == 12
