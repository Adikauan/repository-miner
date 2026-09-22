from __future__ import annotations


def resolve_selection(tree: list[dict[str, object]], rules: list[dict[str, str]]) -> list[str]:
    """Resolve repository IDs from a provider-neutral nested GitLab hierarchy."""
    repositories: list[dict[str, object]] = []

    def walk(nodes: list[dict[str, object]], ancestors: tuple[str, ...] = ()) -> None:
        for node in nodes:
            node_id = str(node.get("id", node.get("external_id", "")))
            kind = str(node.get("kind", node.get("type", ""))).lower()
            path = str(node.get("full_path", node.get("path", node_id)))
            if kind in {"repository", "project"} or "repository_id" in node:
                repositories.append({"id": node.get("repository_id", node_id), "path": path, "ancestors": ancestors, "group_id": node.get("group_id")})
            children = node.get("children") or node.get("repositories") or []
            if isinstance(children, list):
                walk(children, ancestors + (node_id,))
    walk(tree)
    selected: list[str] = []
    for rule in rules:
        target = rule.get("external_id", "")
        kind = rule.get("kind", "repository")
        for repository in repositories:
            matches = repository["id"] == target if kind == "repository" else target in repository["ancestors"] or repository["path"].startswith(target)
            if matches and str(repository["id"]) not in selected:
                selected.append(str(repository["id"]))
    return selected
