import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.mark.parametrize(
    ("scenario_id", "expected_cost"),
    [
        ("T0-P01", 79249.05),
        ("T0-P02", 77827.30),
        ("T0-P03", 82983.90),
    ],
)
def test_demo_reference_endpoint_supports_every_case0_scenario(scenario_id, expected_cost):
    response = client.get(f"/demo/api/reference/{scenario_id}")
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["mode"] == "published_reference"
    assert payload["scenario_id"] == scenario_id
    assert payload["benchmark_cost"] == pytest.approx(expected_cost, abs=0.01)
    assert payload["plan"]["scenario_id"] == scenario_id
    assert payload["simulation"]["feasible"] is True
    assert payload["simulation"]["service_level"] == pytest.approx(1.0, abs=1e-9)
    assert payload["simulation"]["total_cost"] == pytest.approx(expected_cost, abs=0.01)


def test_demo_reference_unknown_scenario_is_controlled_404():
    response = client.get("/demo/api/reference/T0-DOES-NOT-EXIST")
    assert response.status_code == 404
