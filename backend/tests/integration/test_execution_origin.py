from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from repository_miner.app import app
from repository_miner.persistence.database import SessionLocal
from repository_miner.persistence.models import MiningExecution, ScheduleOccurrence


def test_schedule_occurrence_marks_execution_as_scheduled():
    configuration_id, execution_id = str(uuid4()), str(uuid4())
    with SessionLocal.begin() as session:
        session.add(MiningExecution(id=execution_id, configuration_id=configuration_id, status="pending"))
        session.add(ScheduleOccurrence(id=str(uuid4()), configuration_id=configuration_id, execution_id=execution_id, due_at=datetime.now(UTC), status="started"))
    with TestClient(app) as client:
        item = next(value for value in client.get(f"/api/v1/executions?configuration_id={configuration_id}").json()["items"] if value["id"] == execution_id)
    assert item["origin"] == "scheduled"
