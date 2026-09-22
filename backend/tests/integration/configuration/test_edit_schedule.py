from fastapi.testclient import TestClient

from repository_miner.app import app


def test_schedule_can_be_updated_before_gitlab_validation():
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/configurations",
            json={"name": "schedule-edit", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "synthetic-token"},
        )
        configuration_id = created.json()["id"]
        response = client.put(
            f"/api/v1/configurations/{configuration_id}/schedule",
            json={"recurrence": "monthly", "local_time": "09:00", "day_of_month": 31, "timezone": "UTC"},
        )
        assert response.status_code == 200
        assert response.json()["recurrence"] == "monthly"
