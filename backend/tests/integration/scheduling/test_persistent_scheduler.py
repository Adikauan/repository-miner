from datetime import datetime, timezone
from uuid import uuid4

from repository_miner.persistence.models import CredentialReference, MonitoringConfiguration, Schedule
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.scheduling.infrastructure.scheduler import reconcile_schedules, claim_due_occurrences


def test_reconcile_and_claim_persisted_schedule_once(db_session):
    cid, cred = str(uuid4()), str(uuid4())
    db_session.add(CredentialReference(id=cred, status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
    db_session.add(MonitoringConfiguration(id=cid, name="scheduled", gitlab_base_url="https://gitlab.local", target_branch="QA", current_credential_id=cred, enabled=True))
    db_session.add(Schedule(id=str(uuid4()), configuration_id=cid, recurrence="monthly", local_time="12:00", day_of_month=31, timezone="UTC"))
    db_session.commit()
    reconcile_schedules(db_session, datetime(2024, 2, 1, tzinfo=timezone.utc))
    occurrences = claim_due_occurrences(db_session, datetime(2024, 2, 29, 12, 0, tzinfo=timezone.utc))
    assert len(occurrences) == 1
    assert claim_due_occurrences(db_session, datetime(2024, 2, 29, 12, 0, tzinfo=timezone.utc)) == []
