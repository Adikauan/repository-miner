from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException

from repository_miner.shared.domain.types import GitLabErrorCode


@dataclass
class DomainError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: dict[str, Any] | None = None


def to_http(error: DomainError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={"code": error.code, "message": error.message, "details": error.details or {}},
    )


def safe_gitlab_error(code: GitLabErrorCode, status_code: int = 502) -> DomainError:
    messages = {
        GitLabErrorCode.TIMEOUT: "GitLab did not respond within the configured time.",
        GitLabErrorCode.UNAVAILABLE: "GitLab is temporarily unavailable.",
        GitLabErrorCode.RATE_LIMITED: "GitLab rate limit reached.",
        GitLabErrorCode.UNEXPECTED_RESPONSE: "GitLab returned an unexpected response.",
        GitLabErrorCode.MALFORMED_PAYLOAD: "GitLab returned an invalid payload.",
    }
    return DomainError(code.value, messages[code], status_code)

