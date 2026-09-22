from fastapi.testclient import TestClient
from sqlalchemy import event

from repository_miner.app import app
from repository_miner.persistence.database import engine


def test_plan_list_exposes_optional_schedule_summary_without_secrets():
    with TestClient(app) as client:
        created = client.post("/api/v1/configurations", json={"name": "Synthetic plan", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "synthetic-only"})
        configuration_id = created.json()["id"]
        for recurrence, extra in (("daily", {}), ("weekly", {"weekday": 2}), ("monthly", {"day_of_month": 15})):
            response = client.put(f"/api/v1/configurations/{configuration_id}/schedule", json={"recurrence": recurrence, "local_time": "09:30", "timezone": "UTC", **extra})
            assert response.status_code == 200
            page = client.get("/api/v1/configurations", params={"offset": 0, "limit": 200}).json()
            assert {"items", "offset", "limit", "total", "total_pages"} <= page.keys()
            item = next(value for value in page["items"] if value["id"] == configuration_id)
            assert item["schedule_summary"] == {"recurrence": recurrence, "local_time": "09:30", "weekday": extra.get("weekday"), "day_of_month": extra.get("day_of_month")}
            assert not {"gitlab_token", "ciphertext", "schedule_id", "occurrences"} & item.keys()


def test_plan_without_schedule_has_null_summary():
    with TestClient(app) as client:
        created = client.post("/api/v1/configurations", json={"name": "No schedule", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "synthetic-only"}).json()
        page = client.get("/api/v1/configurations", params={"offset": 0, "limit": 200}).json()
        item = next(value for value in page["items"] if value["id"] == created["id"])
        assert item["schedule_summary"] is None


def test_plan_list_query_count_does_not_grow_with_credentials():
    with TestClient(app) as client:
        for index in range(4):
            client.post("/api/v1/configurations", json={"name": f"Query plan {index}", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": f"synthetic-{index}"})
        statements: list[str] = []
        def record(_connection, _cursor, statement, _parameters, _context, _executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                statements.append(statement)
        event.listen(engine, "before_cursor_execute", record)
        try:
            response = client.get("/api/v1/configurations", params={"offset": 0, "limit": 20})
            assert response.status_code == 200
            assert {"items", "offset", "limit", "total", "total_pages"} <= response.json().keys()
        finally:
            event.remove(engine, "before_cursor_execute", record)
    assert len(statements) <= 5


def test_plan_list_rejects_invalid_pagination_parameters():
    with TestClient(app) as client:
        assert client.get("/api/v1/configurations", params={"offset": -1}).status_code == 422
        assert client.get("/api/v1/configurations", params={"limit": 0}).status_code == 422
        assert client.get("/api/v1/configurations", params={"limit": 201}).status_code == 422


def test_plan_list_returns_explicit_empty_page_metadata():
    with TestClient(app) as client:
        response = client.get("/api/v1/configurations", params={"offset": 0, "limit": 20})
        assert response.status_code == 200
        page = response.json()
        assert page["items"] == [] or page["total"] >= len(page["items"])
        assert page["offset"] == 0
        assert page["limit"] == 20
        assert page["total_pages"] == ((page["total"] + page["limit"] - 1) // page["limit"] if page["total"] else 0)
