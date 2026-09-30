from pathlib import Path

from challenge.scenarios import student_visible_scenario


ROOT = Path(__file__).resolve().parents[1]


def test_student_visible_public_scenario_keeps_benchmark_cost():
    scenario = {
        "id": "T3-P01",
        "title": "Example",
        "description": "Example scenario",
        "visible": {"season_risk": 0.4},
        "benchmark_cost": 61000,
        "realized": {"supplier_delay_days": {"SUP02": 4}},
        "public_expectations": {"required_tools": ["calculate_plan_cost"]},
    }

    payload = student_visible_scenario(scenario)

    assert payload["benchmark_cost"] == 61000
    assert "realized" not in payload
    assert "public_expectations" not in payload


def test_frontend_matches_instructor_review_layout_without_case_zero():
    html = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "frontend" / "app.js").read_text(encoding="utf-8")

    for element_id in (
        'id="runtimeStatus"',
        'id="scenarioSummary"',
        'id="feasibility"',
        'id="service"',
        'id="totalCost"',
        'id="expectedCost"',
        'id="ragScore"',
        'id="skillScore"',
        'id="costBreakdown"',
        'id="violations"',
        'id="evaluationBreakdown"',
        'id="trace"',
        'id="plan"',
    ):
        assert element_id in html

    assert "Expected Optimized Cost" in html
    assert "Run AI Manager end-to-end" in html
    assert "/api/status/" in js
    assert "benchmark_cost" in js
    assert "cost_breakdown" in js
    assert "team_0" not in html
    assert "T0-P" not in html
