from pathlib import Path

import yaml

from repository_miner.persistence.models import CommitVerification, RepositoryCheckpoint


def _contracts():
    return yaml.safe_load(Path(__file__).parents[3].joinpath("specs/001-gitlab-repository-mining/contracts/openapi.yaml").read_text(encoding="utf-8"))


def test_openapi_uses_canonical_execution_states_and_counters():
    document = _contracts()
    execution = document["components"]["schemas"]["Execution"]
    status_ref = execution["properties"]["status"]["$ref"].split("/")[-1]
    assert document["components"]["schemas"][status_ref]["enum"] == ["pending", "running", "completed", "partially_completed", "failed"]
    report = document["components"]["schemas"]["Report"]
    counters = {"repositories_total", "repositories_completed", "repositories_failed", "commits_discovered", "commits_verified", "allowed_commits", "unauthorized_commits"}
    assert counters.issubset(set(report["required"]))


def test_openapi_uses_canonical_checkpoint_and_alert_identity():
    document = _contracts()
    verification = document["components"]["schemas"]["CommitVerification"]["properties"]
    assert {"configuration_id", "repository_id", "branch", "commit_hash"}.issubset(verification)
    alert = document["components"]["schemas"]["UnauthorizedCommitAlert"]["properties"]
    assert "commit_hash" in alert and "commit_sha" not in alert
    assert "execution_id" in alert


def test_persistence_identities_match_canonical_keys():
    checkpoint_columns = {column.name for column in RepositoryCheckpoint.__table__.columns}
    verification_columns = {column.name for column in CommitVerification.__table__.columns}
    assert {"configuration_id", "repository_id", "branch"}.issubset(checkpoint_columns)
    assert {"configuration_id", "repository_id", "branch", "commit_hash"}.issubset(verification_columns)


def test_pagination_contract_preserves_canonical_report_fields():
    document = _contracts()
    execution = document["components"]["schemas"]["Execution"]
    assert {"started_at", "finished_at", "status"}.issubset(execution["properties"])
    alert = document["components"]["schemas"]["UnauthorizedCommitAlert"]
    assert {"execution_id", "configuration_id", "commit_hash"}.issubset(alert["properties"])
