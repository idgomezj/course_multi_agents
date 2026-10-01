import inspect

from demo_app.manager import _manager_tool_retry_limit
from demo_app.schemas import MonthlyOperationsPlan
from demo_app.tools import calculate_plan_cost, validate_plan


def test_demo_manager_tool_retry_limit_defaults_to_three(monkeypatch):
    monkeypatch.delenv("MANAGER_TOOL_RETRY_LIMIT", raising=False)
    assert _manager_tool_retry_limit() == 3


def test_demo_plan_tools_expose_full_monthly_plan_schema():
    for tool in (calculate_plan_cost, validate_plan):
        annotation = inspect.signature(tool).parameters["candidate_plan"].annotation
        assert annotation is MonthlyOperationsPlan
