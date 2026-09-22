from uuid import uuid4

from repository_miner.configuration.application.queries import configuration_detail
from repository_miner.persistence.models import CredentialReference, MonitoringConfiguration
from repository_miner.persistence.crypto import encrypt_secret, fingerprint
from repository_miner.shared.domain.types import utc_now


def test_configuration_projection_contains_status_but_no_secret(db_session):
    credential_id = str(uuid4())
    config_id = str(uuid4())
    secret = "synthetic-projection-token"
    db_session.add(CredentialReference(id=credential_id, status="active", ciphertext=encrypt_secret(secret), key_version="v1", fingerprint=fingerprint(secret), created_at=utc_now()))
    db_session.add(MonitoringConfiguration(id=config_id, name="projection", gitlab_base_url="https://gitlab.example.com", timezone="UTC", target_branch="QA", enabled=True, current_credential_id=credential_id))
    db_session.commit()
    result = configuration_detail(db_session, config_id)
    assert result["credential_status"] == "active"
    assert secret not in str(result)
