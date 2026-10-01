import inspect

from challenge.manager import _manager_tool_retry_limit
from challenge.schemas import MonthlyOperationsPlan
from challenge.tools import calculate_plan_cost, validate_plan


def test_manager_tool_retry_limit_defaults_to_three(monkeypatch):
    monkeypatch.delenv("MANAGER_TOOL_RETRY_LIMIT", raising=False)
    assert _manager_tool_retry_limit() == 3


def test_manager_tool_retry_limit_is_bounded(monkeypatch):
    monkeypatch.setenv("MANAGER_TOOL_RETRY_LIMIT", "0")
    assert _manager_tool_retry_limit() == 1

    monkeypatch.setenv("MANAGER_TOOL_RETRY_LIMIT", "99")
    assert _manager_tool_retry_limit() == 8


def test_plan_tools_expose_full_monthly_plan_schema():
    for tool in (calculate_plan_cost, validate_plan):
        annotation = inspect.signature(tool).parameters["candidate_plan"].annotation
        assert annotation is MonthlyOperationsPlan
