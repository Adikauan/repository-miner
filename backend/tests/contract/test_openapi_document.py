from pathlib import Path

import yaml


def test_openapi_document_is_valid_and_keeps_nullable_author_email_required():
    path = Path(__file__).parents[3] / "specs" / "001-gitlab-repository-mining" / "contracts" / "openapi.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert document["openapi"].startswith("3.")
    for schema_name in ("CommitVerification", "UnauthorizedCommitAlert"):
        schema = document["components"]["schemas"][schema_name]
        assert "author_email" in schema["required"]
        assert schema["properties"]["author_email"].get("nullable") is True or "null" in schema["properties"]["author_email"].get("type", [])
