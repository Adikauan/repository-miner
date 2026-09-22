from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class CommitMetadata:
    sha: str
    author_name: str
    author_email: str | None
    committed_at: datetime
    message: str


class GitLabGateway(Protocol):
    def validate_connection(self, base_url: str, token: str) -> None: ...
    def groups_and_repositories(self, base_url: str, token: str) -> list[dict[str, object]]: ...
    def branches(self, base_url: str, token: str, repository_id: str) -> list[str]: ...
    def branch_head(self, base_url: str, token: str, repository_id: str, branch: str) -> str: ...
    def commits_after(self, base_url: str, token: str, repository_id: str, branch: str, sha: str | None) -> list[CommitMetadata]: ...

    def is_commit_reachable(self, base_url: str, token: str, repository_id: str, branch: str, commit_hash: str) -> bool: ...
