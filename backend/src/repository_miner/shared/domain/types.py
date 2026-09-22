from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> UUID:
    return uuid4()


class ExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    FAILED = "failed"


class VerificationSource(StrEnum):
    NEW = "new"
    REUSED = "reused"


class GitLabErrorCode(StrEnum):
    TIMEOUT = "gitlab_timeout"
    UNAVAILABLE = "gitlab_unavailable"
    RATE_LIMITED = "gitlab_rate_limited"
    UNEXPECTED_RESPONSE = "gitlab_unexpected_response"
    MALFORMED_PAYLOAD = "gitlab_malformed_payload"

