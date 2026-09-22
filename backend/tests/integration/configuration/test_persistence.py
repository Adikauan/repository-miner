from tests.integration.test_persistence import (
    test_baseline_and_checkpoint_advance_only_after_success,
    test_commit_verification_is_idempotent_and_alert_is_not_duplicated,
    test_credential_replacement_preserves_mining_records,
)

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from repository_miner.persistence.models import AllowedUser, CredentialReference, RepositorySelectionRule, Schedule
from repository_miner.persistence.crypto import encrypt_secret


def test_configuration_supporting_constraints(db_session):
    configuration_id = str(uuid4())
    db_session.add(CredentialReference(id=str(uuid4()), status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint="fp", created_at=datetime.now(timezone.utc)))
    db_session.add(AllowedUser(id=str(uuid4()), configuration_id=configuration_id, original_email="A@example.com", normalized_email="a@example.com"))
    db_session.commit()
    assert db_session.query(AllowedUser).count() == 1
    db_session.add(AllowedUser(id=str(uuid4()), configuration_id=configuration_id, original_email="a@example.com", normalized_email="a@example.com"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
