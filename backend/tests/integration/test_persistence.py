from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from repository_miner.persistence.models import (
    CommitVerification,
    CredentialReference,
    MiningExecution,
    RepositoryCheckpoint,
    UnauthorizedCommitAlert,
)
from repository_miner.persistence.repositories import (
    advance_checkpoint,
    create_baseline,
    persist_verification_and_alert,
    replace_credential,
)


def seed_execution(session):
    configuration_id, execution_id = str(uuid4()), str(uuid4())
    session.add(MiningExecution(id=execution_id, configuration_id=configuration_id, status="running"))
    session.commit()
    return configuration_id, execution_id


def test_baseline_and_checkpoint_advance_only_after_success(db_session):
    configuration_id, execution_id = seed_execution(db_session)
    checkpoint = create_baseline(db_session, configuration_id=configuration_id, repository_id="repo-1", branch="QA", head_sha="a1")
    db_session.commit()
    assert checkpoint.last_processed_hash == "a1"
    # A failed repository transaction does not call advance_checkpoint.
    assert db_session.scalar(select(RepositoryCheckpoint.last_processed_hash)) == "a1"
    advance_checkpoint(db_session, configuration_id=configuration_id, repository_id="repo-1", branch="QA", head_sha="b2")
    db_session.commit()
    assert db_session.scalar(select(RepositoryCheckpoint.last_processed_hash)) == "b2"


def test_commit_verification_is_idempotent_and_alert_is_not_duplicated(db_session):
    configuration_id, execution_id = seed_execution(db_session)
    kwargs = dict(configuration_id=configuration_id, execution_id=execution_id, repository_id="repo-1", branch="QA", commit_hash="abc", author_name="Alice", author_email="ALICE@example.com", committed_at=datetime.now(timezone.utc), message="change", allowed=False)
    first, first_alert, created = persist_verification_and_alert(db_session, **kwargs)
    db_session.commit()
    second, second_alert, reused = persist_verification_and_alert(db_session, **kwargs)
    db_session.commit()
    assert created is True and reused is False
    assert first.id == second.id
    assert first_alert is not None and second_alert is None
    assert db_session.query(CommitVerification).count() == 1
    assert db_session.query(UnauthorizedCommitAlert).count() == 1


def test_partial_failure_keeps_previous_checkpoint(db_session):
    configuration_id, _ = seed_execution(db_session)
    create_baseline(db_session, configuration_id=configuration_id, repository_id="repo-1", branch="QA", head_sha="base")
    db_session.commit()
    try:
        with db_session.begin():
            raise RuntimeError("repository failed after commit persistence")
    except RuntimeError:
        db_session.rollback()
    assert db_session.scalar(select(RepositoryCheckpoint.last_processed_hash)) == "base"


def test_credential_replacement_preserves_mining_records(db_session):
    configuration_id, execution_id = seed_execution(db_session)
    previous = CredentialReference(id=str(uuid4()), status="active", ciphertext="encrypted-old", key_version="v1", fingerprint="old", created_at=datetime.now(timezone.utc))
    db_session.add(previous)
    db_session.commit()
    replacement = CredentialReference(id=str(uuid4()), status="active", ciphertext="encrypted-new", key_version="v1", fingerprint="new", created_at=datetime.now(timezone.utc))
    replace_credential(db_session, configuration_id=configuration_id, previous=previous, replacement=replacement, operator_id="operator-1", reason="preventive")
    db_session.commit()
    assert previous.status == "replaced"
    assert db_session.get(CredentialReference, replacement.id).status == "active"
    assert db_session.get(MiningExecution, execution_id) is not None
