from fastapi.testclient import TestClient

from repository_miner.app import app


def test_allowed_users_can_be_updated_before_gitlab_validation():
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/configurations",
            json={"name": "allowed-users-edit", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "synthetic-token"},
        )
        configuration_id = created.json()["id"]
        response = client.put(f"/api/v1/configurations/{configuration_id}/allowed-users", json={"emails": [" Dev@Example.COM "]})
        assert response.status_code == 200
        assert response.json()["emails"] == ["dev@example.com"]
