from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from repository_miner.gitlab.application.ports import CommitMetadata
from repository_miner.shared.api.errors import DomainError, safe_gitlab_error
from repository_miner.shared.domain.types import GitLabErrorCode


class HttpGitLabGateway:
    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    def _request(self, base_url: str, token: str, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            response = httpx.get(
                f"{base_url.rstrip('/')}/api/v4/{path.lstrip('/')}",
                headers={"PRIVATE-TOKEN": token}, params=params, timeout=self.timeout,
                # GitLab credentials must not be sent through an inherited, opaque
                # proxy configuration. Provider access is direct unless explicitly
                # configured by the application deployment.
                trust_env=False,
            )
        except httpx.TimeoutException as exc:
            raise safe_gitlab_error(GitLabErrorCode.TIMEOUT) from exc
        except httpx.HTTPError as exc:
            raise safe_gitlab_error(GitLabErrorCode.UNAVAILABLE) from exc
        if response.status_code == 429:
            raise safe_gitlab_error(GitLabErrorCode.RATE_LIMITED, 429)
        if response.status_code >= 500:
            raise safe_gitlab_error(GitLabErrorCode.UNAVAILABLE)
        if response.status_code >= 400:
            raise safe_gitlab_error(GitLabErrorCode.UNEXPECTED_RESPONSE, 502)
        try:
            return response.json()
        except ValueError as exc:
            raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD) from exc

    def validate_connection(self, base_url: str, token: str) -> None:
        payload = self._request(base_url, token, "user")
        if not isinstance(payload, dict) or not payload.get("id"):
            raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)

    def groups_and_repositories(self, base_url: str, token: str) -> list[dict[str, object]]:
        groups_payload = self._request(base_url, token, "groups", {"per_page": 100, "all_available": True})
        projects_payload = self._request(base_url, token, "projects", {"per_page": 100, "simple": True})
        if not isinstance(groups_payload, list) or not isinstance(projects_payload, list):
            raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)
        groups: dict[str, dict[str, object]] = {}
        for item in groups_payload:
            if not isinstance(item, dict) or item.get("id") is None:
                raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)
            group = {"id": str(item["id"]), "kind": "group", "full_path": str(item.get("full_path") or item.get("path") or item["id"]), "children": []}
            groups[str(item["id"])] = group
        roots: list[dict[str, object]] = []
        for item in groups_payload:
            if not isinstance(item, dict):
                continue
            group = groups.get(str(item.get("id")))
            if group is None:
                continue
            parent = item.get("parent_id")
            if parent is not None and str(parent) in groups:
                groups[str(parent)]["children"].append(group)
            else:
                roots.append(group)
        for item in projects_payload:
            if not isinstance(item, dict) or item.get("id") is None:
                raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)
            namespace = item.get("namespace") if isinstance(item.get("namespace"), dict) else {}
            repo = {"id": str(item["id"]), "kind": "repository", "full_path": str(item.get("path_with_namespace") or item.get("path") or item["id"])}
            group_id = namespace.get("id")
            if group_id is not None and str(group_id) in groups:
                groups[str(group_id)]["children"].append(repo)
            else:
                roots.append(repo)
        return roots

    def branches(self, base_url: str, token: str, repository_id: str) -> list[str]:
        payload = self._request(base_url, token, f"projects/{repository_id}/repository/branches", {"per_page": 100})
        if not isinstance(payload, list):
            raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)
        result: list[str] = []
        for item in payload:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not item["name"]:
                raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)
            result.append(item["name"])
        return result

    def branch_head(self, base_url: str, token: str, repository_id: str, branch: str) -> str:
        payload = self._request(base_url, token, f"projects/{repository_id}/repository/branches/{branch}")
        if not isinstance(payload, dict) or not isinstance(payload.get("commit"), dict):
            raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)
        sha = payload["commit"].get("id")
        if not isinstance(sha, str) or not sha:
            raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)
        return sha

    def commits_after(self, base_url: str, token: str, repository_id: str, branch: str, sha: str | None) -> list[CommitMetadata]:
        params: dict[str, Any] = {"ref_name": branch, "per_page": 100}
        if sha:
            params["after"] = sha
        payload = self._request(base_url, token, f"projects/{repository_id}/repository/commits", params)
        if not isinstance(payload, list):
            raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)
        result: list[CommitMetadata] = []
        for item in payload:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)
            authored = item.get("authored_date") or item.get("committed_date")
            try:
                committed_at = datetime.fromisoformat(str(authored).replace("Z", "+00:00"))
            except ValueError:
                committed_at = datetime.now(timezone.utc)
            result.append(CommitMetadata(item["id"], str(item.get("author_name") or ""), item.get("author_email"), committed_at, str(item.get("title") or item.get("message") or "")))
        return result

    def is_commit_reachable(self, base_url: str, token: str, repository_id: str, branch: str, commit_hash: str) -> bool:
        """Validate that a checkpoint is still part of the configured branch.

        GitLab's compare endpoint is used instead of cloning a repository. A missing
        commit/branch or an invalid comparison is reported as a divergence rather than
        being silently converted into a new baseline by the mining layer.
        """
        try:
            payload = self._request(
                base_url, token,
                f"projects/{repository_id}/repository/compare",
                {"from": commit_hash, "to": branch, "straight": False},
            )
        except DomainError as exc:
            if exc.code in {"gitlab_unexpected_response", "gitlab_malformed_payload"}:
                return False
            raise
        if not isinstance(payload, dict):
            raise safe_gitlab_error(GitLabErrorCode.MALFORMED_PAYLOAD)
        # GitLab returns compare_same_ref when the checkpoint equals the branch tip.
        # A successful compare payload with a commit list means the checkpoint is an
        # ancestor; an explicit false comparison means it is not reachable.
        if payload.get("compare_same_ref") is True:
            return True
        return isinstance(payload.get("commits"), list) and payload.get("compare_timeout") is not True
