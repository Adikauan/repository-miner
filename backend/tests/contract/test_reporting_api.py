from fastapi.testclient import TestClient

from repository_miner.app import app


def test_reporting_endpoints_use_pagination_and_safe_not_found():
    with TestClient(app) as client:
        response = client.get("/api/v1/executions/not-found/report-v2")
        assert response.status_code == 404
        response = client.get("/api/v1/executions/not-found/unauthorized-commits?offset=0&limit=10")
        assert response.status_code == 200
        assert response.json()["items"] == []


def test_reporting_invalid_pagination_is_rejected():
    with TestClient(app) as client:
        response = client.get("/api/v1/executions/not-found/unauthorized-commits?limit=0")
        assert response.status_code == 422
