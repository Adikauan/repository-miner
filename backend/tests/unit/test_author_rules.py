from repository_miner.mining.application.verify_commit import normalize_email


def test_normalize_email():
    assert normalize_email(" Alice@Example.COM ") == "alice@example.com"
    assert normalize_email(None) is None
    assert normalize_email("  ") is None

