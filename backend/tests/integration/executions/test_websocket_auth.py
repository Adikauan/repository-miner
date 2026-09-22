import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from repository_miner.app import app


def _execution(client: TestClient) -> str:
    config = client.post("/api/v1/configurations", json={"name": "ws-auth", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "secret"}).json()
    return client.post(f"/api/v1/configurations/{config['id']}/executions").json()["id"]


def test_wrong_execution_and_invalid_ticket_are_rejected():
    with TestClient(app) as client:
        execution_id = _execution(client)
        other_execution_id = _execution(client)
        ticket = client.post(f"/api/v1/executions/{execution_id}/websocket-tickets", headers={"x-operator-id": "operator-1"}).json()["ticket"]
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(f"/api/v1/ws/executions/{other_execution_id}?ticket={ticket}", headers={"x-operator-id": "operator-1"}):
                pass
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(f"/api/v1/ws/executions/{execution_id}?ticket=invalid", headers={"x-operator-id": "operator-1"}):
                pass
