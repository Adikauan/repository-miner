from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from repository_miner.app import app
from repository_miner.persistence.database import SessionLocal
from repository_miner.persistence.models import MiningExecution


def test_pending_execution_order_is_deterministic_across_pages_and_new_records_start_page_one():
    configuration_id = str(uuid4())
    with SessionLocal.begin() as session:
        for execution_id in ("pending-a", "pending-m", "pending-z"):
            session.add(MiningExecution(id=execution_id + configuration_id[:8], configuration_id=configuration_id, status="pending", started_at=None))
    with TestClient(app) as client:
        before = client.get(f"/api/v1/executions?configuration_id={configuration_id}&offset=0&limit=2").json()
        before_again = client.get(f"/api/v1/executions?configuration_id={configuration_id}&offset=0&limit=2").json()
        with SessionLocal.begin() as session:
            session.add(MiningExecution(id="pending-new" + configuration_id[:8], configuration_id=configuration_id, status="pending", started_at=None))
        after = client.get(f"/api/v1/executions?configuration_id={configuration_id}&offset=0&limit=2").json()
    assert [item["id"] for item in before["items"]] == [item["id"] for item in before_again["items"]]
    assert [item["id"] for item in after["items"]] == sorted([item["id"] for item in after["items"]], reverse=True)
