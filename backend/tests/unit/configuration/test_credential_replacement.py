import pytest

from repository_miner.configuration.domain.credential_replacement import validate_replacement


def test_preventive_and_compromise_replacement_rules():
    assert validate_replacement("active", "preventive").new_status == "active"
    assert validate_replacement("compromised", "compromise_remediation").new_status == "active"
    with pytest.raises(ValueError):
        validate_replacement("compromised", "preventive")
    with pytest.raises(ValueError):
        validate_replacement("replaced", "preventive")
