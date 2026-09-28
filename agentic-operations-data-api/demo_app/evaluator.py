from __future__ import annotations

import json
import logging
from typing import Any

from .cost_engine import cost_gap, cost_score_from_gap
from .schemas import EvaluationResult, MonthlyOperationsPlan, ToolTraceEntry
from .simulator import simulate_month
from app.observability import log_event

logger = logging.getLogger(__name__)


_SKILL_META_TOOLS = {"list_skills", "load_skill"}
_RAG_TOOLS = {"search_knowledge"}
_DISCIPLINE_TOOLS = {"calculate_plan_cost", "validate_plan"}


def _trace_tool_names(trace: list[dict[str, Any]]) -> list[str]:
    return [str(x.get("tool")) for x in trace]


def _exact_duplicate_calls(trace: list[dict[str, Any]]) -> int:
    """Count only truly duplicated calls: same tool with the same inputs.

    Calling the same tool for different products/materials is normal and must
    not be penalized.
    """
    seen: set[tuple[str, str]] = set()
    duplicates = 0
    for entry in trace:
        tool = str(entry.get("tool"))
        inputs = json.dumps(entry.get("inputs", {}), sort_keys=True, default=str)
        key = (tool, inputs)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates


def skill_tool_breakdown(
    scenario: dict[str, Any],
    trace: list[dict[str, Any]],
) -> dict[str, Any]:
    """Transparent 100-point diagnostic score for Skills + tool discipline.

    This score is intentionally separate from the operational score.

    - Skill usage: 25 points
        * list_skills: 5
        * load at least one Skill: 20
    - Expected operational tool coverage: 45 points
        * coverage of scenario-required operational tools
        * RAG and cost/validation tools are scored in their own components
    - Cost + validation discipline: 20 points
        * calculate_plan_cost: 10
        * validate_plan: 10
    - Efficiency: 10 points
        * starts at 10
        * discouraged calls: -5 each
        * exact duplicate calls (same tool + same inputs): -2 each
        * repeated calls with different inputs are NOT penalized
    """
    expectations = scenario.get("private_expectations") or scenario.get("public_expectations", {})
    required = set(expectations.get("required_tools", []))
    discouraged = set(expectations.get("discouraged_tools", []))

    names = _trace_tool_names(trace)
    used = set(names)

    listed_skills = "list_skills" in used
    loaded_skills = [
        str(entry.get("inputs", {}).get("name"))
        for entry in trace
        if entry.get("tool") == "load_skill" and entry.get("inputs", {}).get("name")
    ]

    skill_usage_score = (5.0 if listed_skills else 0.0) + (20.0 if loaded_skills else 0.0)

    excluded_from_operational_coverage = _SKILL_META_TOOLS | _RAG_TOOLS | _DISCIPLINE_TOOLS
    expected_operational = sorted(required - excluded_from_operational_coverage)
    used_operational = sorted(set(expected_operational) & used)
    missing_operational = sorted(set(expected_operational) - used)

    if expected_operational:
        operational_tool_score = 45.0 * len(used_operational) / len(expected_operational)
    else:
        operational_tool_score = 45.0

    cost_called = "calculate_plan_cost" in used
    validation_called = "validate_plan" in used
    discipline_score = (10.0 if cost_called else 0.0) + (10.0 if validation_called else 0.0)

    discouraged_calls = [name for name in names if name in discouraged]
    duplicate_calls = _exact_duplicate_calls(trace)
    efficiency_penalty = min(10.0, 5.0 * len(discouraged_calls) + 2.0 * duplicate_calls)
    efficiency_score = (10.0 - efficiency_penalty) if names else 0.0

    total = max(
        0.0,
        min(
            100.0,
            skill_usage_score + operational_tool_score + discipline_score + efficiency_score,
        ),
    )

    return {
        "total_score": round(total, 2),
        "components": {
            "skill_usage": round(skill_usage_score, 2),
            "expected_operational_tools": round(operational_tool_score, 2),
            "cost_and_validation": round(discipline_score, 2),
            "efficiency": round(efficiency_score, 2),
        },
        "weights": {
            "skill_usage": 25,
            "expected_operational_tools": 45,
            "cost_and_validation": 20,
            "efficiency": 10,
        },
        "skill_usage": {
            "list_skills_called": listed_skills,
            "skills_loaded": loaded_skills,
        },
        "operational_tools": {
            "expected": expected_operational,
            "used": used_operational,
            "missing": missing_operational,
        },
        "discipline": {
            "calculate_plan_cost_called": cost_called,
            "validate_plan_called": validation_called,
        },
        "efficiency": {
            "discouraged_tools": sorted(discouraged),
            "discouraged_calls": discouraged_calls,
            "exact_duplicate_calls": duplicate_calls,
            "penalty": round(efficiency_penalty, 2),
        },
        "note": (
            "search_knowledge is evaluated under the separate RAG score. "
            "Repeated calls with different inputs are not penalized."
        ),
    }


def score_skill_tools(scenario: dict[str, Any], trace: list[dict[str, Any]]) -> float:
    return float(skill_tool_breakdown(scenario, trace)["total_score"])


def rag_breakdown(scenario: dict[str, Any], rag_hits: set[str]) -> dict[str, Any]:
    expectations = scenario.get("private_expectations") or scenario.get("public_expectations", {})
    expected = set(expectations.get("rag_expected_sources", []))
    used = set(rag_hits)
    if not expected:
        score = 100.0
    else:
        score = 100.0 * len(expected & used) / len(expected)
    return {
        "total_score": round(score, 2),
        "expected_sources": sorted(expected),
        "retrieved_expected_sources": sorted(expected & used),
        "missing_sources": sorted(expected - used),
        "all_retrieved_sources": sorted(used),
    }


def score_rag(scenario: dict[str, Any], rag_hits: set[str]) -> float:
    return float(rag_breakdown(scenario, rag_hits)["total_score"])


def evaluate_plan(
    case: dict[str, Any],
    scenario: dict[str, Any],
    plan: MonthlyOperationsPlan,
    trace: list[dict[str, Any]],
    rag_hits: set[str],
) -> EvaluationResult:
    log_event(logger, "evaluation.scoring.started", team_id=plan.team_id, scenario_id=plan.scenario_id, tool_calls=len(trace), rag_hits=sorted(rag_hits))
    sim = simulate_month(case, scenario, plan)

    feasibility_score = 100.0 if sim.feasible else 0.0

    target = float(case.get("policies", {}).get("service_level_target", 0.95))
    service_score = min(100.0, 100.0 * sim.service_level / max(target, 1e-6))

    benchmark_cost = scenario.get("benchmark_cost")
    gap = cost_gap(sim.total_cost, float(benchmark_cost) if benchmark_cost else None)
    cost_score = cost_score_from_gap(gap) if sim.feasible else 0.0

    skill_details = skill_tool_breakdown(scenario, trace)
    rag_details = rag_breakdown(scenario, rag_hits)
    skill_tool = float(skill_details["total_score"])
    rag = float(rag_details["total_score"])

    if not sim.feasible:
        operational = 0.0
        contributions = {
            "feasibility": 0.0,
            "service": 0.0,
            "cost": 0.0,
        }
    else:
        contributions = {
            "feasibility": 0.35 * feasibility_score,
            "service": 0.25 * service_score,
            "cost": 0.40 * cost_score,
        }
        operational = sum(contributions.values())

    evaluation_breakdown = {
        "operational": {
            "total_score": round(operational, 2),
            "feasible_gate": sim.feasible,
            "weights": {
                "feasibility": 35,
                "service": 25,
                "cost": 40,
            },
            "component_scores": {
                "feasibility": round(feasibility_score, 2),
                "service": round(service_score, 2),
                "cost": round(cost_score, 2),
            },
            "weighted_contributions": {
                key: round(value, 2) for key, value in contributions.items()
            },
            "service_level": round(sim.service_level, 6),
            "service_level_target": target,
            "cost_gap": round(gap, 4) if gap is not None else None,
            "rule": (
                "If the plan has any critical feasibility violation, operational score is 0. "
                "Otherwise: 35% feasibility + 25% service + 40% cost."
            ),
        },
        "rag": rag_details,
        "skills_tools": skill_details,
        "important": (
            "RAG and Skills/Tools are transparent diagnostic learning scores. "
            "They do not change the operational score."
        ),
    }

    log_event(
        logger,
        "evaluation.scoring.completed",
        team_id=plan.team_id,
        scenario_id=plan.scenario_id,
        feasible=sim.feasible,
        service_level=sim.service_level,
        total_cost=sim.total_cost,
        benchmark_cost=benchmark_cost,
        cost_gap=gap,
        operational_score=round(operational, 2),
        rag_score=round(rag, 2),
        skill_tool_score=round(skill_tool, 2),
        violations=[v.model_dump() for v in sim.violations],
        evaluation_breakdown=evaluation_breakdown,
    )

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
        evaluation_breakdown=evaluation_breakdown,
    )
