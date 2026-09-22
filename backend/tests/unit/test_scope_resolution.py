from repository_miner.repositories.application.resolve_scope import resolve_repository_scope


class Gateway:
    def __init__(self, tree):
        self.tree = tree
        self.calls = 0

    def groups_and_repositories(self, *_args):
        self.calls += 1
        return self.tree


def test_repository_scope_is_deduplicated_without_hierarchy_call():
    gateway = Gateway([])
    assert resolve_repository_scope(gateway, base_url="", token="", rules=[{"kind": "repository", "external_id": "r1"}, {"kind": "repository", "external_id": "r1"}]) == ["r1"]
    assert gateway.calls == 0


def test_group_scope_is_expanded_from_hierarchy():
    gateway = Gateway([{"id": "g1", "kind": "group", "full_path": "group", "children": [{"id": "r1", "kind": "repository", "full_path": "group/r1"}]}])
    assert resolve_repository_scope(gateway, base_url="", token="", rules=[{"kind": "group", "external_id": "g1"}]) == ["r1"]
    assert gateway.calls == 1
