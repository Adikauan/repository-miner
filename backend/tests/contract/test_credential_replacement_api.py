from fastapi.testclient import TestClient

from repository_miner.app import app


def test_replacement_requires_authenticated_operator():
    with TestClient(app) as client:
        created = client.post("/api/v1/configurations", json={"name": "replacement-contract", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "secret"})
        response = client.post(f"/api/v1/configurations/{created.json()['id']}/credential-replacements", json={"gitlab_token": "new-secret", "reason": "preventive"})
        assert response.status_code == 401


def test_replacement_reason_is_validated_without_echoing_secret():
    with TestClient(app) as client:
        created = client.post("/api/v1/configurations", json={"name": "replacement-reason", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "secret"})
        canary = "CANARY-REPLACEMENT-SECRET"
        response = client.post(f"/api/v1/configurations/{created.json()['id']}/credential-replacements", headers={"x-operator-id": "operator-1"}, json={"gitlab_token": canary, "reason": "invalid"})
        assert response.status_code == 422
        assert canary not in response.text


def test_preventive_replacement_returns_active_and_compromised_requires_remediation():
    with TestClient(app) as client:
        config = client.post("/api/v1/configurations", json={"name": "replacement-flow", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "old"}).json()
        replacement = client.post(f"/api/v1/configurations/{config['id']}/credential-replacements", headers={"x-operator-id": "operator-1"}, json={"gitlab_token": "new", "reason": "preventive"})
        assert replacement.status_code == 201
        assert replacement.json()["credential_status"] == "active"
        config = client.post("/api/v1/configurations", json={"name": "replacement-compromised", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "old"}).json()
        client.post(f"/api/v1/configurations/{config['id']}/credential-incidents", headers={"x-operator-id": "operator-1"})
        refused = client.post(f"/api/v1/configurations/{config['id']}/credential-replacements", headers={"x-operator-id": "operator-1"}, json={"gitlab_token": "new", "reason": "preventive"})
        assert refused.status_code == 409
        repaired = client.post(f"/api/v1/configurations/{config['id']}/credential-replacements", headers={"x-operator-id": "operator-1"}, json={"gitlab_token": "new", "reason": "compromise_remediation"})
        assert repaired.status_code == 201
