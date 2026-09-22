from fastapi.testclient import TestClient

from repository_miner.app import app


def test_scope_requires_connection_validation():
    client = TestClient(app)
    response = client.post("/api/v1/configurations", json={"name": "scope", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "secret"})
    configuration_id = response.json()["id"]
    blocked = client.put(f"/api/v1/configurations/{configuration_id}/repository-selections", json={"rules": []})
    assert blocked.status_code == 409

