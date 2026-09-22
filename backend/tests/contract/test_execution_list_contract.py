from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from repository_miner.app import app
from repository_miner.persistence.database import SessionLocal
from repository_miner.persistence.models import MiningExecution


def test_execution_list_filters_before_pagination_and_exposes_origin_and_counters():
    first, second = str(uuid4()), str(uuid4())
    with SessionLocal.begin() as session:
        for index in range(3):
            session.add(MiningExecution(id=str(uuid4()), configuration_id=first if index != 1 else second, status="completed", started_at=datetime(2026, 1, index + 1, tzinfo=UTC), repositories_total=1, repositories_completed=1, repositories_failed=0, commits_discovered=2, commits_verified=2, allowed_commits=2, unauthorized_commits=0))
    with TestClient(app) as client:
        body = client.get(f"/api/v1/executions?configuration_id={first}&offset=1&limit=1").json()
    assert len(body["items"]) == 1
    assert body["items"][0]["configuration_id"] == first
    assert body["items"][0]["origin"] == "manual"
    assert all(isinstance(body["items"][0][field], int) for field in ("repositories_total", "repositories_completed", "repositories_failed", "commits_discovered", "commits_verified", "allowed_commits", "unauthorized_commits"))


def test_execution_list_orders_newest_first_before_pagination_and_stably_orders_nulls():
    configuration_id = str(uuid4())
    prefix = configuration_id[:8]
    with SessionLocal.begin() as session:
        for execution_id, started_at, status in (
            (f"exec-old-{prefix}", datetime(2026, 1, 1, tzinfo=UTC), "completed"),
            (f"exec-new-{prefix}", datetime(2026, 1, 3, tzinfo=UTC), "completed"),
            (f"exec-tie-a-{prefix}", datetime(2026, 1, 2, tzinfo=UTC), "completed"),
            (f"exec-tie-z-{prefix}", datetime(2026, 1, 2, tzinfo=UTC), "completed"),
            (f"pending-a-{prefix}", None, "pending"),
            (f"pending-z-{prefix}", None, "pending"),
        ):
            session.add(MiningExecution(id=execution_id, configuration_id=configuration_id, status=status, started_at=started_at))
    with TestClient(app) as client:
        first = client.get(f"/api/v1/executions?configuration_id={configuration_id}&offset=0&limit=3").json()
        second = client.get(f"/api/v1/executions?configuration_id={configuration_id}&offset=3&limit=3").json()
        repeated = client.get(f"/api/v1/executions?configuration_id={configuration_id}&offset=3&limit=3").json()
    assert [item["id"] for item in first["items"]] == [f"exec-new-{prefix}", f"exec-tie-z-{prefix}", f"exec-tie-a-{prefix}"]
    assert [item["id"] for item in second["items"]] == [f"exec-old-{prefix}", f"pending-z-{prefix}", f"pending-a-{prefix}"]
    assert [item["id"] for item in second["items"]] == [item["id"] for item in repeated["items"]]


def test_new_execution_is_first_on_a_fresh_configuration_scoped_query():
    configuration_id = str(uuid4())
    with SessionLocal.begin() as session:
        session.add(MiningExecution(id=f"older-{configuration_id[:8]}", configuration_id=configuration_id, status="completed", started_at=datetime(2026, 1, 1, tzinfo=UTC)))
        session.add(MiningExecution(id=f"newer-{configuration_id[:8]}", configuration_id=configuration_id, status="completed", started_at=datetime(2026, 1, 4, tzinfo=UTC)))
    with TestClient(app) as client:
        page = client.get(f"/api/v1/executions?configuration_id={configuration_id}&offset=0&limit=1").json()
    assert page["items"][0]["id"] == f"newer-{configuration_id[:8]}"
