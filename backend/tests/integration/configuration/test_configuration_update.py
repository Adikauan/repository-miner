from fastapi.testclient import TestClient

from repository_miner.app import app


def test_basic_update_preserves_configuration_identifier():
    with TestClient(app) as client:
        created = client.post("/api/v1/configurations", json={"name": "update", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "synthetic-update-token"})
        configuration_id = created.json()["id"]
        response = client.patch(f"/api/v1/configurations/{configuration_id}", json={"name": "updated", "enabled": False, "timezone": "UTC"})
        assert response.status_code == 200
        assert response.json()["id"] == configuration_id
        assert response.json()["name"] == "updated"
        assert response.json()["enabled"] is False
