from fastapi.testclient import TestClient

from repository_miner.app import app
from repository_miner.persistence.database import SessionLocal
from repository_miner.persistence.models import CredentialIncident, CredentialReference, MonitoringConfiguration


def test_compromise_requires_operator_and_records_secret_free_incident():
    with TestClient(app) as client:
        config = client.post("/api/v1/configurations", json={"name": "incident", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "original-secret"}).json()
        unauthenticated = client.post(f"/api/v1/configurations/{config['id']}/credential-incidents")
        assert unauthenticated.status_code == 401
        response = client.post(f"/api/v1/configurations/{config['id']}/credential-incidents", headers={"x-operator-id": "operator-1"})
        assert response.status_code == 201
        assert response.json()["credential_status"] == "compromised"
        with SessionLocal() as session:
            incident = session.query(CredentialIncident).join(CredentialReference).filter(CredentialReference.status == "compromised").order_by(CredentialIncident.suspected_at.desc()).first()
            assert incident is not None
            assert "secret" not in (incident.safe_reason or "").lower()


def test_compromised_credential_requires_remediation_reason():
    with TestClient(app) as client:
        config = client.post("/api/v1/configurations", json={"name": "incident-replace", "gitlab_base_url": "https://gitlab.example.com", "gitlab_token": "original-secret"}).json()
        client.post(f"/api/v1/configurations/{config['id']}/credential-incidents", headers={"x-operator-id": "operator-1"})
        response = client.post(f"/api/v1/configurations/{config['id']}/credential-replacements", headers={"x-operator-id": "operator-1"}, json={"gitlab_token": "new-secret", "reason": "preventive"})
        assert response.status_code == 409
