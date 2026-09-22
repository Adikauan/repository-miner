from datetime import datetime, timezone
from types import SimpleNamespace

from repository_miner.gitlab.infrastructure.http_gateway import HttpGitLabGateway


def test_commit_gateway_requests_metadata_only_operations(monkeypatch):
    requests: list[str] = []

    def fake_get(url, **kwargs):
        requests.append(url)
        if "/branches/" in url:
            return SimpleNamespace(status_code=200, json=lambda: {"commit": {"id": "head"}})
        return SimpleNamespace(status_code=200, json=lambda: [{"id": "commit", "author_name": "A", "author_email": "a@example.com", "committed_date": datetime.now(timezone.utc).isoformat(), "message": "msg"}])

    monkeypatch.setattr("httpx.get", fake_get)
    gateway = HttpGitLabGateway()
    assert gateway.branch_head("https://gitlab.example.com", "token", "42", "QA") == "head"
    commits = gateway.commits_after("https://gitlab.example.com", "token", "42", "QA", "base")
    assert commits[0].sha == "commit"
    assert all("diff" not in url and "changes" not in url for url in requests)
