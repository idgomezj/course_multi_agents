import pytest

from challenge.config import student_team_ids


def test_student_team_ids_never_include_case_zero(monkeypatch):
    monkeypatch.delenv("ASSIGNED_TEAM_ID", raising=False)
    teams = student_team_ids()
    assert teams
    assert "team_0" not in teams
    assert all(team in {f"team_{i}" for i in range(1, 6)} for team in teams)


def test_assigned_student_team_is_single_workspace(monkeypatch):
    monkeypatch.setenv("ASSIGNED_TEAM_ID", "team_3")
    assert student_team_ids() == ["team_3"]


def test_case_zero_cannot_be_assigned_to_student_runtime(monkeypatch):
    monkeypatch.setenv("ASSIGNED_TEAM_ID", "team_0")
    with pytest.raises(ValueError, match="team_1"):
        student_team_ids()
