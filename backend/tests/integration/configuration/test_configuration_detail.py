from fastapi.testclient import TestClient

from repository_miner.app import app


def test_configuration_detail_loads_without_plaintext_credential():
    with TestClient(app) as client:
        created = client.post("/api/v1/configurations", json={"name": "detail", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "synthetic-detail-token"})
        configuration_id = created.json()["id"]
        response = client.get(f"/api/v1/configurations/{configuration_id}")
        assert response.status_code == 200
        assert "gitlab_token" not in response.json()
        assert "synthetic-detail-token" not in response.text


def test_missing_configuration_detail_is_not_found():
    with TestClient(app) as client:
        response = client.get("/api/v1/configurations/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
