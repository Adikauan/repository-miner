from datetime import datetime, timezone
from uuid import uuid4

from repository_miner.gitlab.application.ports import CommitMetadata
from repository_miner.mining.application.verify_commit import normalize_email, verify_commit
from repository_miner.persistence.store import Configuration, Store


def test_author_email_comparison_is_trimmed_and_case_insensitive():
    assert normalize_email("  Dev@Example.COM ") == "dev@example.com"
    assert normalize_email(None) is None
    assert normalize_email(" ") is None


def test_missing_email_is_unauthorized_and_preserves_original_metadata():
    store = Store()
    configuration_id = uuid4()
    execution_id = uuid4()
    store.configurations[configuration_id] = Configuration(configuration_id, "cfg", "https://gitlab.example.com", "token", allowed_emails={"dev@example.com"})
    commit = CommitMetadata("h1", "Unknown", None, datetime.now(timezone.utc), "message")
    verification, created, alert = verify_commit(store, configuration_id, execution_id, "repo", "QA", commit)
    assert created is True
    assert verification.allowed is False
    assert verification.author_email is None
    assert alert is not None and alert.author_email is None


def test_duplicate_verification_does_not_create_second_alert():
    store = Store()
    configuration_id = uuid4()
    execution_id = uuid4()
    store.configurations[configuration_id] = Configuration(configuration_id, "cfg", "https://gitlab.example.com", "token")
    commit = CommitMetadata("h1", "Unknown", "unknown@example.com", datetime.now(timezone.utc), "message")
    first, created, alert = verify_commit(store, configuration_id, execution_id, "repo", "QA", commit)
    second, reused, duplicate_alert = verify_commit(store, configuration_id, uuid4(), "repo", "QA", commit)
    assert created is True and alert is not None
    assert reused is False and duplicate_alert is None
    assert second is first
    assert len(store.alerts) == 1
