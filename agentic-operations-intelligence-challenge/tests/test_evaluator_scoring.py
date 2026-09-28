from challenge.evaluator import rag_breakdown, skill_tool_breakdown


def _scenario():
    return {
        "public_expectations": {
            "required_tools": [
                "forecast_pytorch",
                "predict_supplier_delay",
                "get_inventory",
                "get_open_purchase_orders",
                "calculate_bom_requirements",
                "get_supplier_options",
                "calculate_plan_cost",
                "search_knowledge",
                "validate_plan",
            ],
            "discouraged_tools": ["calculate_jit_requirement"],
            "rag_expected_sources": ["operations_policy.md", "supplier_contracts.md"],
        }
    }


def _entry(tool, inputs=None):
    return {"tool": tool, "inputs": inputs or {}, "output": {}}


def test_full_skill_tool_workflow_scores_100():
    trace = [
        _entry("list_skills"),
        _entry("load_skill", {"name": "monthly_planning.md"}),
        _entry("search_knowledge", {"query": "policy"}),
        _entry("forecast_pytorch", {"product_id": "FG01"}),
        _entry("predict_supplier_delay", {"supplier_id": "SUP01", "material_id": "RM01", "quantity": 1000}),
        _entry("get_inventory"),
        _entry("get_open_purchase_orders"),
        _entry("calculate_bom_requirements", {"product_id": "FG01", "quantity": 1000}),
        _entry("get_supplier_options", {"material_id": "RM01"}),
        _entry("calculate_plan_cost", {"candidate_plan": {}}),
        _entry("validate_plan", {"candidate_plan": {}}),
    ]
    details = skill_tool_breakdown(_scenario(), trace)
    assert details["total_score"] == 100.0
    assert details["components"] == {
        "skill_usage": 25.0,
        "expected_operational_tools": 45.0,
        "cost_and_validation": 20.0,
        "efficiency": 10.0,
    }


def test_skill_usage_is_scored_directly():
    trace = [
        _entry("list_skills"),
        _entry("load_skill", {"name": "monthly_planning.md"}),
    ]
    details = skill_tool_breakdown(_scenario(), trace)
    assert details["components"]["skill_usage"] == 25.0
    assert details["total_score"] == 35.0


def test_same_tool_with_different_inputs_is_not_duplicate_penalty():
    trace = [
        _entry("forecast_pytorch", {"product_id": "FG01"}),
        _entry("forecast_pytorch", {"product_id": "FG02"}),
        _entry("forecast_pytorch", {"product_id": "FG03"}),
    ]
    details = skill_tool_breakdown(_scenario(), trace)
    assert details["efficiency"]["exact_duplicate_calls"] == 0
    assert details["components"]["efficiency"] == 10.0


def test_exact_duplicate_and_discouraged_calls_are_penalized():
    trace = [
        _entry("get_inventory"),
        _entry("get_inventory"),
        _entry("calculate_jit_requirement", {"gross_requirement": 10, "on_hand": 2, "incoming_before_need": 0}),
    ]
    details = skill_tool_breakdown(_scenario(), trace)
    assert details["efficiency"]["exact_duplicate_calls"] == 1
    assert details["efficiency"]["discouraged_calls"] == ["calculate_jit_requirement"]
    assert details["components"]["efficiency"] == 3.0


def test_empty_trace_gets_no_efficiency_credit():
    details = skill_tool_breakdown(_scenario(), [])
    assert details["components"]["efficiency"] == 0.0


def test_rag_is_scored_separately_from_skill_tools():
    details = rag_breakdown(_scenario(), {"operations_policy.md", "supplier_contracts.md"})
    assert details["total_score"] == 100.0
    assert details["missing_sources"] == []
