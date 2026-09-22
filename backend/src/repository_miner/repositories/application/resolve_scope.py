from __future__ import annotations

from collections.abc import Iterable

from repository_miner.gitlab.application.hierarchy import resolve_selection
from repository_miner.gitlab.application.ports import GitLabGateway


def resolve_repository_scope(
    gateway: GitLabGateway,
    *,
    base_url: str,
    token: str,
    rules: Iterable[dict[str, str]],
) -> list[str]:
    """Expand repository/group selection rules into stable repository ids.

    The gateway is called only for group/subgroup rules; repository-only scopes
    remain usable with small fakes and do not require an unnecessary hierarchy
    request. The returned list is de-duplicated while preserving discovery order.
    """
    normalized = [
        {"kind": str(rule.get("kind", "repository")), "external_id": str(rule.get("external_id", ""))}
        for rule in rules
        if rule.get("external_id")
    ]
    if not normalized:
        return []
    if not any(rule["kind"] in {"group", "subgroup"} for rule in normalized):
        return list(dict.fromkeys(rule["external_id"] for rule in normalized))
    tree = gateway.groups_and_repositories(base_url, token)
    return list(dict.fromkeys(resolve_selection(tree, normalized)))
