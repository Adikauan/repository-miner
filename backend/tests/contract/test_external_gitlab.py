import pytest


@pytest.mark.external_gitlab
def test_external_gitlab_contract_is_opt_in():
    pytest.skip("External GitLab contract suite is opt-in and requires explicit credentials.")
