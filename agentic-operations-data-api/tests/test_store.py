from app.store import available_teams, case_without_scenarios, load_knowledge, load_model_spec
from app.training_data import generate_training_rows


def test_five_teams_exist():
    assert available_teams() == ("team_1", "team_2", "team_3", "team_4", "team_5")


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
