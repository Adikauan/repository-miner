from fastapi.testclient import TestClient

from repository_miner.app import app


def test_connection_identity_change_invalidates_dependent_scope_operations():
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/configurations",
            json={"name": "connection-edit", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "synthetic-token"},
        )
        configuration_id = created.json()["id"]
        assert client.post(f"/api/v1/configurations/{configuration_id}/connection-test").status_code == 200
        changed = client.put(f"/api/v1/configurations/{configuration_id}/connection", json={"gitlab_base_url": "https://other.example.com"})
        assert changed.status_code == 200
        blocked = client.put(f"/api/v1/configurations/{configuration_id}/repository-selections", json={"target_branch": "QA", "rules": []})
        assert blocked.status_code == 409
        assert blocked.json()["detail"]["code"] == "connection_not_validated"
