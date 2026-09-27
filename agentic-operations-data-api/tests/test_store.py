import pytest

from app.store import (
    available_teams,
    case_without_scenarios,
    load_case,
    load_knowledge,
    load_model_spec,
    public_scenario,
    reference_solution,
)
from app.training_data import generate_training_rows
from demo_app.schemas import MonthlyOperationsPlan
from demo_app.simulator import simulate_month


def test_all_teams_exist():
    assert available_teams() == (
        "team_0",
        "team_1",
        "team_2",
        "team_3",
        "team_4",
        "team_5",
    )


def test_each_team_has_required_assets():
    for team in available_teams():
        case = case_without_scenarios(team)
        assert case["products"] and case["materials"] and case["suppliers"]
        assert load_knowledge(team)
        assert set(load_model_spec(team)["models"]) == {"model_a", "model_b"}


def test_training_generation():
    for team in available_teams():
        for model in ("model_a", "model_b"):
            rows = generate_training_rows(team, model, rows=120, seed=7)
            assert len(rows) == 120


@pytest.mark.parametrize(
    ("scenario_id", "expected_cost"),
    [
        ("T0-P01", 79249.05),
        ("T0-P02", 77827.30),
        ("T0-P03", 82983.90),
    ],
)
def test_case0_reference_solution_exists_and_matches_benchmark(scenario_id, expected_cost):
    solved = reference_solution("team_0", scenario_id)
    assert solved["scenario_id"] == scenario_id
    assert solved["reference_plan"]["team_id"] == "team_0"
    assert solved["reference_plan"]["scenario_id"] == scenario_id
    assert solved["reference_plan"]["production_plan"]
    assert solved["reference_evaluation"]["benchmark_cost"] == pytest.approx(expected_cost, abs=0.01)

    plan = MonthlyOperationsPlan.model_validate(solved["reference_plan"])
    scenario = public_scenario("team_0", scenario_id)
    result = simulate_month(load_case("team_0"), scenario, plan)

    assert result.feasible is True
    assert result.service_level == pytest.approx(1.0, abs=1e-9)
    assert not [v for v in result.violations if v.critical]
    assert result.total_cost == pytest.approx(expected_cost, abs=0.01)
