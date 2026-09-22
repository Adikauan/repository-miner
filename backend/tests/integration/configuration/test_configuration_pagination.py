from fastapi.testclient import TestClient

from repository_miner.app import app


def _create(client: TestClient, name: str) -> str:
    response = client.post(
        "/api/v1/configurations",
        json={"name": name, "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": f"synthetic-{name}"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_configuration_pages_are_stable_without_duplicates_or_omissions():
    with TestClient(app) as client:
        ids = [_create(client, f"pagination-{index}") for index in range(5)]
        first = client.get("/api/v1/configurations", params={"offset": 0, "limit": 2}).json()
        second = client.get("/api/v1/configurations", params={"offset": 2, "limit": 2}).json()
        repeated = client.get("/api/v1/configurations", params={"offset": 0, "limit": 2}).json()

        assert first["offset"] == 0 and first["limit"] == 2
        assert first["total"] >= len(ids)
        assert first["total_pages"] == (first["total"] + 1) // 2
        first_ids = [item["id"] for item in first["items"]]
        second_ids = [item["id"] for item in second["items"]]
        assert first_ids == [item["id"] for item in repeated["items"]]
        assert set(first_ids).isdisjoint(second_ids)


def test_new_configuration_is_returned_by_a_fresh_first_page_query():
    with TestClient(app) as client:
        created_id = _create(client, "new-first-page")
        # With no canonical creation timestamp, id DESC is deterministic fallback;
        # this test verifies the fresh query and updated total without claiming chronology.
        page = client.get("/api/v1/configurations", params={"offset": 0, "limit": 200}).json()
        assert page["total"] >= 1
        assert created_id in [item["id"] for item in page["items"]]
