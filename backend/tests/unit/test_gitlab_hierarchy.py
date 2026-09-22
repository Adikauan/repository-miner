from repository_miner.gitlab.application.hierarchy import resolve_selection


def test_resolves_repository_group_and_subgroup_rules_without_fetching_diffs():
    tree = [
        {
            "id": "g1",
            "kind": "group",
            "full_path": "platform",
            "children": [
                {
                    "id": "sg1",
                    "kind": "subgroup",
                    "full_path": "platform/backend",
                    "children": [
                        {"id": "r1", "kind": "repository", "full_path": "platform/backend/api"},
                    ],
                },
                {"id": "r2", "kind": "repository", "full_path": "platform/web"},
            ],
        }
    ]

    assert resolve_selection(tree, [{"kind": "group", "external_id": "g1"}]) == ["r1", "r2"]
    assert resolve_selection(tree, [{"kind": "subgroup", "external_id": "sg1"}]) == ["r1"]
    assert resolve_selection(tree, [{"kind": "repository", "external_id": "r2"}]) == ["r2"]

