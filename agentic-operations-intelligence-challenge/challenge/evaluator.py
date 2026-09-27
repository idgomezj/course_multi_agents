from __future__ import annotations

from typing import Any

from .cost_engine import cost_gap, cost_score_from_gap
from .schemas import EvaluationResult, MonthlyOperationsPlan, ToolTraceEntry
from .simulator import simulate_month


def _trace_tool_names(trace: list[dict[str, Any]]) -> list[str]:
    return [str(x.get("tool")) for x in trace]


def score_skill_tools(scenario: dict[str, Any], trace: list[dict[str, Any]]) -> float:
    expectations = scenario.get("public_expectations", {})
    required = set(expectations.get("required_tools", []))
    discouraged = set(expectations.get("discouraged_tools", []))
    names = _trace_tool_names(trace)
    used = set(names)

    required_score = 100.0 if not required else 100.0 * len(required & used) / len(required)
    irrelevant_calls = sum(1 for name in names if name in discouraged)
    repeated = max(0, len(names) - len(set(names)) - 2)
    return max(0.0, min(100.0, required_score - 7.5 * irrelevant_calls - 2.0 * repeated))


def score_rag(scenario: dict[str, Any], rag_hits: set[str]) -> float:
    expected = set(scenario.get("public_expectations", {}).get("rag_expected_sources", []))
    if not expected:
        return 100.0
    return 100.0 * len(expected & rag_hits) / len(expected)


def evaluate_plan(
    case: dict[str, Any],
    scenario: dict[str, Any],
    plan: MonthlyOperationsPlan,
    trace: list[dict[str, Any]],
    rag_hits: set[str],
) -> EvaluationResult:
    sim = simulate_month(case, scenario, plan)
    feasibility_score = 100.0 if sim.feasible else 0.0
    target = float(case.get("policies", {}).get("service_level_target", 0.95))
    service_score = min(100.0, 100.0 * sim.service_level / max(target, 1e-6))
    benchmark_cost = scenario.get("benchmark_cost")
    gap = cost_gap(sim.total_cost, float(benchmark_cost) if benchmark_cost else None)
    cost_score = cost_score_from_gap(gap) if sim.feasible else 0.0
    skill_tool = score_skill_tools(scenario, trace)
    rag = score_rag(scenario, rag_hits)

    if not sim.feasible:
        operational = 0.0
    else:
        operational = 0.35 * feasibility_score + 0.25 * service_score + 0.40 * cost_score

    return EvaluationResult(
        team_id=plan.team_id,
        scenario_id=plan.scenario_id,
        operational_score=round(operational, 2),
        feasibility_score=round(feasibility_score, 2),
        service_score=round(service_score, 2),
        cost_score=round(cost_score, 2),
        skill_tool_score=round(skill_tool, 2),
        rag_score=round(rag, 2),
        total_cost=sim.total_cost,
        benchmark_cost=float(benchmark_cost) if benchmark_cost else None,
        cost_gap=round(gap, 4) if gap is not None else None,
        violations=sim.violations,
        trace=[ToolTraceEntry.model_validate(x) for x in trace],
        plan=plan,
    )
