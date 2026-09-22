from datetime import datetime, timezone
from uuid import uuid4

import pytest

from repository_miner.configuration.application.edit import connection_is_validated, update_basic_fields
from repository_miner.persistence.models import MonitoringConfiguration, Schedule


def test_missing_configuration_is_rejected(db_session):
    with pytest.raises(ValueError):
        update_basic_fields(db_session, str(uuid4()), name="missing")


def test_enabled_update_recalculates_schedule_and_disable_clears_next_run(db_session):
    configuration_id = str(uuid4())
    db_session.add(MonitoringConfiguration(id=configuration_id, name="cfg", gitlab_base_url="https://gitlab.example.com", timezone="UTC", target_branch="QA", enabled=True))
    db_session.add(Schedule(id=str(uuid4()), configuration_id=configuration_id, recurrence="daily", local_time="09:00", timezone="UTC", next_run_at=datetime.now(timezone.utc)))
    db_session.commit()
    update_basic_fields(db_session, configuration_id, enabled=False)
    assert db_session.query(Schedule).one().next_run_at is None
    assert not connection_is_validated(db_session.get(MonitoringConfiguration, configuration_id))
