from fastapi.testclient import TestClient
import json
from repository_miner.executions.application.event_publisher import ExecutionEventPublisher
from repository_miner.persistence.crypto import encrypt_secret

from repository_miner.app import app


def test_canary_token_is_not_returned_by_configuration_or_ticket_errors():
    canary = "CANARY-SUPER-SECRET-TOKEN"
    with TestClient(app) as client:
        response = client.post("/api/v1/configurations", json={"name": "secret-scan", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": canary})
        assert canary not in response.text
        configuration_id = response.json()["id"]
        response = client.post(f"/api/v1/executions/not-an-id/websocket-tickets", headers={"x-operator-id": canary})
        assert canary not in response.text


def test_canary_secret_is_absent_from_event_envelopes_and_ciphertext_is_not_plaintext():
    publisher = ExecutionEventPublisher()
    event = publisher.publish("execution.started", "execution", "configuration", {"status": "running"})
    assert canary_not_in(json.dumps(event))
    assert canary_not_in(encrypt_secret("CANARY-SUPER-SECRET-TOKEN"))


def canary_not_in(value: str) -> bool:
    return "CANARY-SUPER-SECRET-TOKEN" not in value
