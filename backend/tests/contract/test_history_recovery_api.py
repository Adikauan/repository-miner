from pathlib import Path

import yaml


def test_history_recovery_contract_exposes_explicit_reset_and_error():
    document = yaml.safe_load(Path(__file__).parents[3].joinpath("specs/001-gitlab-repository-mining/contracts/openapi.yaml").read_text(encoding="utf-8"))
    path = next(path for path in document["paths"] if path.endswith("baseline-reset"))
    assert "post" in document["paths"][path]
    assert "HistoryDiverged" in str(document["paths"][path])
    schema = document["components"]["schemas"]["BaselineReset"]["required"]
    assert {"previous_checkpoint_hash", "new_baseline_hash"}.issubset(schema)
