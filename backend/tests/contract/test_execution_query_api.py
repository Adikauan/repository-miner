from fastapi.testclient import TestClient

from repository_miner.app import app


CANONICAL_COUNTERS = {
    "repositories_total", "repositories_completed", "repositories_failed",
    "commits_discovered", "commits_verified", "allowed_commits", "unauthorized_commits",
}


def test_execution_history_exposes_canonical_state_and_counter_names():
    with TestClient(app) as client:
        response = client.get("/api/v1/executions")
        assert response.status_code == 200
        for item in response.json()["items"]:
            assert set(item) >= {"id", "configuration_id", "status", *CANONICAL_COUNTERS}
            assert item["status"] in {"pending", "running", "completed", "partially_completed", "failed"}


def test_unknown_execution_queries_return_not_found():
    with TestClient(app) as client:
        response = client.get("/api/v1/executions/not-found/commits")
        assert response.status_code == 404
