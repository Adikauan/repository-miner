from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from repository_miner.app import app
from repository_miner.persistence.database import SessionLocal
from repository_miner.persistence.models import RepositoryCheckpoint


def test_scope_edit_keeps_existing_checkpoint_history():
    with TestClient(app) as client:
        created = client.post("/api/v1/configurations", json={"name": "scope-history", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "synthetic-scope-token"})
        configuration_id = created.json()["id"]
        with SessionLocal.begin() as session:
            session.add(RepositoryCheckpoint(id=str(uuid4()), configuration_id=configuration_id, repository_id="repo-old", branch="QA", baseline_hash="baseline-old", last_processed_hash="head-old", initialized_at=datetime.now(timezone.utc)))
        assert client.post(f"/api/v1/configurations/{configuration_id}/connection-test").status_code == 200
        assert client.put(f"/api/v1/configurations/{configuration_id}/repository-selections", json={"target_branch": "QA", "rules": [{"kind": "repository", "external_id": "repo-new"}]}).status_code == 200
        with SessionLocal() as session:
            checkpoint = session.query(RepositoryCheckpoint).filter_by(configuration_id=configuration_id, repository_id="repo-old").one()
            assert checkpoint.last_processed_hash == "head-old"
