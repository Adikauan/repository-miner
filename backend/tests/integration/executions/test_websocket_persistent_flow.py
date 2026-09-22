from fastapi.testclient import TestClient
import pytest
from starlette.websockets import WebSocketDisconnect

from repository_miner.app import app


def test_ticket_is_persistent_single_use_and_snapshot_is_available():
    with TestClient(app) as client:
        created = client.post("/api/v1/configurations", json={"name": "ws-flow", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "secret"})
        configuration_id = created.json()["id"]
        client.post(f"/api/v1/configurations/{configuration_id}/connection-test")
        execution = client.post(f"/api/v1/configurations/{configuration_id}/executions").json()
        execution_id = execution["id"]
        ticket_response = client.post(f"/api/v1/executions/{execution_id}/websocket-tickets", headers={"x-operator-id": "operator-1"})
        assert ticket_response.status_code == 200
        ticket = ticket_response.json()["ticket"]
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(f"/api/v1/ws/executions/{execution_id}?ticket={ticket}", headers={"x-operator-id": "operator-2"}):
                pass
        with client.websocket_connect(f"/api/v1/ws/executions/{execution_id}?ticket={ticket}", headers={"x-operator-id": "operator-1"}) as socket:
            snapshot = socket.receive_json()
            assert snapshot["type"] == "execution.snapshot"
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(f"/api/v1/ws/executions/{execution_id}?ticket={ticket}", headers={"x-operator-id": "operator-1"}):
                pass
