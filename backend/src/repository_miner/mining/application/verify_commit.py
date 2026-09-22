from __future__ import annotations

from repository_miner.gitlab.application.ports import CommitMetadata
from repository_miner.persistence.store import Alert, Store, Verification
from repository_miner.shared.domain.types import utc_now


def normalize_email(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    return value.strip().casefold()


def verify_commit(store: Store, configuration_id, execution_id, repository_id: str, branch: str, commit: CommitMetadata) -> tuple[Verification, bool, Alert | None]:
    key = (configuration_id, repository_id, branch, commit.sha)
    existing = store.verifications.get(key)
    if existing:
        return existing, False, None
    author_email = normalize_email(commit.author_email)
    allowed = author_email is not None and author_email in store.configurations[configuration_id].allowed_emails
    verification = Verification(configuration_id, repository_id, branch, commit.sha, commit.author_name, commit.author_email, commit.committed_at, commit.message, allowed, execution_id)
    store.verifications[key] = verification
    alert = None
    if not allowed:
        alert = Alert(__import__("uuid").uuid4(), configuration_id, execution_id, repository_id, branch, commit.sha, commit.author_name, commit.author_email, commit.committed_at, utc_now())
        store.alerts[alert.id] = alert
    return verification, True, alert

