from challenge.config import CASES_DIR, available_teams, load_case, student_path
from challenge.rag import RagIndex
from challenge.scenarios import list_public_scenarios
from challenge.training_data import generate_training_frame


def test_all_five_cases_load():
    assert available_teams() == ["team_1", "team_2", "team_3", "team_4", "team_5"]
    for team in available_teams():
        case = load_case(team)
        assert case["products"]
        assert case["materials"]
        assert case["suppliers"]
        assert len(list_public_scenarios(team)) >= 3


def test_training_data_matches_model_specs():
    for team in available_teams():
        for key in ("model_a", "model_b"):
            df = generate_training_frame(team, key, rows=120, seed=7)
            assert len(df) == 120
            assert not df.isna().any().any()


def test_rag_indexes_each_case():
    for team in available_teams():
        index = RagIndex(CASES_DIR / team / "knowledge", student_path(team) / "rag" / "config.yaml")
        assert index.chunks
        assert isinstance(index.search("policy supplier inventory production"), list)
