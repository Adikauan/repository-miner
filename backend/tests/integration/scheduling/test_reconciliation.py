from datetime import datetime, timezone, timedelta
from uuid import uuid4

from repository_miner.persistence.models import CredentialReference, MiningExecution, MonitoringConfiguration, Schedule, ScheduleOccurrence
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.scheduling.infrastructure.scheduler import claim_due_occurrences


def test_reconciliation_collapses_missed_occurrences_to_latest(db_session):
    cid, cred = str(uuid4()), str(uuid4())
    db_session.add(CredentialReference(id=cred, status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
    db_session.add(MonitoringConfiguration(id=cid, name="cfg", gitlab_base_url="https://gitlab.local", current_credential_id=cred, enabled=True))
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    db_session.add(Schedule(id=str(uuid4()), configuration_id=cid, recurrence="daily", local_time=(now - timedelta(days=3)).strftime("%H:%M"), timezone="UTC", next_run_at=now - timedelta(days=3)))
    db_session.commit()
    claimed = claim_due_occurrences(db_session, now)
    assert len(claimed) == 1
    assert claimed[0].due_at.replace(tzinfo=timezone.utc) <= now
    assert db_session.query(ScheduleOccurrence).count() == 1
    assert db_session.query(Schedule).one().next_run_at.replace(tzinfo=timezone.utc) > now


def test_reconciliation_skips_disabled_without_execution(db_session):
    cid, cred = str(uuid4()), str(uuid4())
    db_session.add(CredentialReference(id=cred, status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
    db_session.add(MonitoringConfiguration(id=cid, name="cfg", gitlab_base_url="https://gitlab.local", current_credential_id=cred, enabled=False))
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    db_session.add(Schedule(id=str(uuid4()), configuration_id=cid, recurrence="daily", local_time="00:00", timezone="UTC", next_run_at=now - timedelta(days=1)))
    db_session.commit()
    assert claim_due_occurrences(db_session, now) == []
    occurrence = db_session.query(ScheduleOccurrence).one()
    assert occurrence.status == "skipped_disabled"
    assert db_session.query(MiningExecution).count() == 0


def test_reconciliation_skips_compromised_and_active_configurations(db_session):
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    for status, execution_status in (("compromised", None), ("active", "running")):
        cid, cred = str(uuid4()), str(uuid4())
        db_session.add(CredentialReference(id=cred, status=status, ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
        db_session.add(MonitoringConfiguration(id=cid, name=status, gitlab_base_url="https://gitlab.local", current_credential_id=cred, enabled=True))
        db_session.add(Schedule(id=str(uuid4()), configuration_id=cid, recurrence="daily", local_time="00:00", timezone="UTC", next_run_at=now - timedelta(days=1)))
        if execution_status:
            db_session.add(MiningExecution(id=str(uuid4()), configuration_id=cid, status=execution_status))
    db_session.commit()
    assert claim_due_occurrences(db_session, now) == []
    statuses = {o.status for o in db_session.query(ScheduleOccurrence).all()}
    assert statuses == {"skipped_compromised", "skipped_active"}


def test_reconciliation_is_idempotent_for_existing_occurrence(db_session):
    cid, cred = str(uuid4()), str(uuid4())
    db_session.add(CredentialReference(id=cred, status="active", ciphertext=encrypt_secret("token"), key_version="v1", fingerprint=fingerprint("token"), created_at=datetime.now(timezone.utc)))
    db_session.add(MonitoringConfiguration(id=cid, name="cfg", gitlab_base_url="https://gitlab.local", current_credential_id=cred, enabled=True))
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    due = now.replace(hour=0, minute=0)
    db_session.add(Schedule(id=str(uuid4()), configuration_id=cid, recurrence="daily", local_time="00:00", timezone="UTC", next_run_at=due))
    db_session.add(ScheduleOccurrence(id=str(uuid4()), configuration_id=cid, due_at=due, status="completed"))
    db_session.commit()
    assert claim_due_occurrences(db_session, now) == []
    assert db_session.query(ScheduleOccurrence).count() == 1
