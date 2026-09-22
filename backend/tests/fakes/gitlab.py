from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from repository_miner.gitlab.application.ports import CommitMetadata


class FakeGitLabError(RuntimeError):
    """Failure injected by a test at a specific gateway operation."""


@dataclass
class FakeGitLabGateway:
    """Small deterministic GitLab gateway used without network access.

    The fake stores only metadata needed by the MVP and can inject failures per
    operation or repository. Calls are recorded so tests can assert that a
    commit was not verified twice and that no diff endpoint was requested.
    """

    tree: list[dict[str, object]] = field(default_factory=list)
    heads: dict[tuple[str, str], str] = field(default_factory=dict)
    commits: dict[tuple[str, str], list[CommitMetadata]] = field(default_factory=dict)
    reachable: dict[tuple[str, str, str], bool] = field(default_factory=dict)
    failures: dict[tuple[str, str | None], Exception] = field(default_factory=dict)
    compromised: bool = False
    calls: list[tuple[str, str | None]] = field(default_factory=list)

    def _call(self, operation: str, repository_id: str | None = None) -> None:
        self.calls.append((operation, repository_id))
        if self.compromised:
            raise FakeGitLabError("credential_compromised")
        failure = self.failures.get((operation, repository_id)) or self.failures.get((operation, None))
        if failure:
            raise failure

    def validate_connection(self, base_url: str, token: str) -> None:
        self._call("validate_connection")

    def groups_and_repositories(self, base_url: str, token: str) -> list[dict[str, object]]:
        self._call("groups_and_repositories")
        return list(self.tree)

    def branch_head(self, base_url: str, token: str, repository_id: str, branch: str) -> str:
        self._call("branch_head", repository_id)
        try:
            return self.heads[(repository_id, branch)]
        except KeyError as exc:
            raise FakeGitLabError("branch_not_found") from exc

    def commits_after(self, base_url: str, token: str, repository_id: str, branch: str, sha: str | None) -> list[CommitMetadata]:
        self._call("commits_after", repository_id)
        items = list(self.commits.get((repository_id, branch), []))
        if sha is None:
            return items
        for index, item in enumerate(items):
            if item.sha == sha:
                return items[index + 1 :]
        raise FakeGitLabError("history_diverged")

    def is_commit_reachable(self, base_url: str, token: str, repository_id: str, branch: str, commit_hash: str) -> bool:
        self._call("is_commit_reachable", repository_id)
        return self.reachable.get((repository_id, branch, commit_hash), commit_hash == self.heads.get((repository_id, branch)))

    def add_commit(self, repository_id: str, branch: str, commit_hash: str, *, author_name: str = "Author", author_email: str | None = "author@example.com", committed_at: datetime | None = None, message: str = "commit") -> None:
        self.commits.setdefault((repository_id, branch), []).append(
            CommitMetadata(commit_hash, author_name, author_email, committed_at or datetime.now(), message)
        )
        self.heads[(repository_id, branch)] = commit_hash
