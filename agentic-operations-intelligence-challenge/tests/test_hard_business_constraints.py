from challenge.schemas import MonthlyOperationsPlan, ProductionOrder
from challenge.simulator import simulate_month


def _case():
    return {
        "products": {
            "FG": {
                "base_demand": [1, 1, 1, 1],
                "initial_fg": 0,
                "hours_per_unit": 1.0,
                "production_cost": 10.0,
                "preferred_line": "L1",
            }
        },
        "materials": {},
        "bom": {"FG": {}},
        "suppliers": {},
        "lines": {"L1": {"weekly_hours": 10, "products": ["FG"]}},
        "open_purchase_orders": [],
        "policies": {
            "service_level_target": 0.90,
            "max_overtime_hours_per_line_week": 5,
        },
        "constraints": {
            "monthly_operating_budget": 30,
            "max_monthly_overtime_hours": 2,
            "max_expedited_units": 0,
            "max_finished_goods_inventory_units": 100,
        },
        "costs": {
            "stockout_per_unit": 0,
            "lost_sale_per_unit": 0,
            "holding_per_unit_week": 0,
            "working_capital_rate": 0,
            "overtime_per_hour": 0,
            "line_stop_per_hour": 0,
            "expedite_per_unit": 0,
            "changeover_cost": 0,
        },
    }


def test_case_hard_budget_is_not_a_student_preference():
    plan = MonthlyOperationsPlan(
        team_id="team_1",
        scenario_id="TEST",
        production_plan=[
            ProductionOrder(week=1, product_id="FG", quantity=4, line_id="L1"),
        ],
        purchase_orders=[],
    )
    result = simulate_month(_case(), {"id": "TEST", "realized": {}}, plan)
    codes = {violation.code for violation in result.violations}
    assert "OPERATING_BUDGET" in codes
    assert result.feasible is False
