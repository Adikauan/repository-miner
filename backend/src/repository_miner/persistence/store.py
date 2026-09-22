from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from repository_miner.shared.domain.types import ExecutionStatus, VerificationSource


@dataclass
class Configuration:
    id: UUID
    name: str
    gitlab_base_url: str
    credential_token: str
    credential_status: str = "active"
    target_branch: str = "QA"
    timezone: str = "UTC"
    enabled: bool = True
    allowed_emails: set[str] = field(default_factory=set)
    selections: list[dict[str, str]] = field(default_factory=list)
    connection_validated: bool = False


@dataclass
class Execution:
    id: UUID
    configuration_id: UUID
    status: ExecutionStatus = ExecutionStatus.PENDING
    commits_discovered: int = 0
    commits_verified: int = 0
    allowed_commits: int = 0
    unauthorized_commits: int = 0
    repositories_completed: int = 0
    repositories_failed: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None
    terminal_reason: str | None = None


@dataclass
class Verification:
    configuration_id: UUID
    repository_id: str
    branch: str
    commit_hash: str
    author_name: str
    author_email: str | None
    committed_at: datetime
    message: str
    allowed: bool
    first_execution_id: UUID


@dataclass
class Alert:
    id: UUID
    configuration_id: UUID
    execution_id: UUID
    repository_id: str
    branch: str
    commit_hash: str
    author_name: str
    author_email: str | None
    committed_at: datetime
    detected_at: datetime


@dataclass
class Ticket:
    digest: str
    operator_id: str
    execution_id: UUID
    expires_at: datetime
    consumed_at: datetime | None = None


class Store:
    def __init__(self) -> None:
        self.configurations: dict[UUID, Configuration] = {}
        self.executions: dict[UUID, Execution] = {}
        self.verifications: dict[tuple[UUID, str, str, str], Verification] = {}
        self.alerts: dict[UUID, Alert] = {}
        self.checkpoints: dict[tuple[UUID, str, str], str] = {}
        self.tickets: dict[str, Ticket] = {}
        self.ticket_pepper = secrets.token_bytes(32)

    def digest_ticket(self, value: str) -> str:
        return hmac.new(self.ticket_pepper, value.encode(), hashlib.sha256).hexdigest()

    def issue_ticket(self, operator_id: str, execution_id: UUID) -> str:
        plaintext = secrets.token_urlsafe(32)
        self.tickets[self.digest_ticket(plaintext)] = Ticket(
            self.digest_ticket(plaintext), operator_id, execution_id,
            datetime.now(timezone.utc) + timedelta(seconds=60),
        )
        return plaintext

    def consume_ticket(self, plaintext: str, operator_id: str, execution_id: UUID) -> bool:
        ticket = self.tickets.get(self.digest_ticket(plaintext))
        now = datetime.now(timezone.utc)
        if not ticket or ticket.consumed_at or ticket.expires_at <= now:
            return False
        if ticket.operator_id != operator_id or ticket.execution_id != execution_id:
            return False
        ticket.consumed_at = now
        return True


store = Store()
