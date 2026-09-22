from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from repository_miner.app import app
from repository_miner.persistence.database import SessionLocal
from repository_miner.persistence.models import WebSocketTicket
from repository_miner.shared.domain.types import utc_now


def _execution(client: TestClient) -> str:
    config = client.post("/api/v1/configurations", json={"name": "ticket-contract", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "secret"}).json()
    return client.post(f"/api/v1/configurations/{config['id']}/executions").json()["id"]


def test_ticket_issuance_binds_operator_and_execution():
    with TestClient(app) as client:
        execution_id = _execution(client)
        response = client.post(f"/api/v1/executions/{execution_id}/websocket-tickets", headers={"x-operator-id": "operator-1"})
        assert response.status_code == 200
        body = response.json()
        assert body["execution_id"] == execution_id
        assert body["operator_id"] == "operator-1"
        with SessionLocal() as session:
            stored = session.query(WebSocketTicket).filter_by(execution_id=execution_id).order_by(WebSocketTicket.created_at.desc()).first()
            assert stored is not None
            assert body["ticket"] not in stored.ticket_digest
            assert stored.expires_at.replace(tzinfo=utc_now().tzinfo) > utc_now()


def test_expired_ticket_is_rejected_without_consumption():
    with TestClient(app) as client:
        execution_id = _execution(client)
        ticket = client.post(f"/api/v1/executions/{execution_id}/websocket-tickets", headers={"x-operator-id": "operator-1"}).json()["ticket"]
        with SessionLocal.begin() as session:
            row = session.query(WebSocketTicket).filter_by(execution_id=execution_id).order_by(WebSocketTicket.created_at.desc()).first()
            row.expires_at = utc_now() - timedelta(seconds=1)
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(f"/api/v1/ws/executions/{execution_id}?ticket={ticket}", headers={"x-operator-id": "operator-1"}):
                raise AssertionError("expired ticket was accepted")
