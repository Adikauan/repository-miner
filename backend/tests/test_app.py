from fastapi.testclient import TestClient

from repository_miner.app import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_scope_requires_connection_validation() -> None:
    created = client.post("/api/v1/configurations", json={"name": "QA", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "secret"})
    assert created.status_code == 201
    configuration_id = created.json()["id"]
    response = client.put(f"/api/v1/configurations/{configuration_id}/repository-selections", json={"rules": []})
    assert response.status_code == 409


def test_websocket_ticket_requires_operator() -> None:
    created = client.post("/api/v1/configurations", json={"name": "Ticket", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "secret"})
    client.post(f"/api/v1/configurations/{created.json()['id']}/connection-test")
    execution = client.post(f"/api/v1/configurations/{created.json()['id']}/executions").json()
    response = client.post(f"/api/v1/executions/{execution['id']}/websocket-tickets")
    assert response.status_code == 401

