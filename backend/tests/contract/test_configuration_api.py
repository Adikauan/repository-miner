from fastapi.testclient import TestClient

from repository_miner.app import app


def test_configuration_contract_requires_connection_before_scope_and_normalizes_users():
    with TestClient(app) as client:
        created = client.post("/api/v1/configurations", json={"name": "contract", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "secret"})
        assert created.status_code == 201
        configuration_id = created.json()["id"]
        blocked = client.put(f"/api/v1/configurations/{configuration_id}/repository-selections", json={"target_branch": "QA", "rules": []})
        assert blocked.status_code == 409
        assert client.post(f"/api/v1/configurations/{configuration_id}/connection-test").status_code == 200
        saved = client.put(f"/api/v1/configurations/{configuration_id}/repository-selections", json={"target_branch": "QA", "rules": [{"kind": "repository", "external_id": "r1"}]})
        assert saved.status_code == 200
        users = client.put(f"/api/v1/configurations/{configuration_id}/allowed-users", json={"emails": [" Dev@Example.COM "]})
        assert users.status_code == 200
        assert users.json()["emails"] == ["dev@example.com"]


def test_credential_incident_rejects_missing_identity():
    with TestClient(app) as client:
        configuration_id = client.post("/api/v1/configurations", json={"name": "incident-auth", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "secret"}).json()["id"]
        assert client.post(f"/api/v1/configurations/{configuration_id}/credential-incidents").status_code == 401


def test_configuration_detail_is_write_only_and_patch_rejects_dependent_fields():
    with TestClient(app) as client:
        created = client.post(
            "/api/v1/configurations",
            json={"name": "contract-detail", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "synthetic-token"},
        )
        assert created.status_code == 201
        configuration_id = created.json()["id"]
        detail = client.get(f"/api/v1/configurations/{configuration_id}")
        assert detail.status_code == 200
        assert "gitlab_token" not in detail.json()
        assert "credential_plaintext" not in detail.json()
        rejected = client.patch(
            f"/api/v1/configurations/{configuration_id}",
            json={"name": "changed", "branch": "main", "allowed_users": ["dev@example.com"]},
        )
        assert rejected.status_code == 422
