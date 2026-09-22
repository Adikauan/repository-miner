import pytest

from repository_miner.shared.api.errors import safe_gitlab_error
from repository_miner.shared.domain.types import GitLabErrorCode


@pytest.mark.parametrize("code", list(GitLabErrorCode))
def test_gitlab_failures_are_safe(code):
    error = safe_gitlab_error(code)
    assert error.code == code.value
    assert "token" not in error.message.lower()
    assert "secret" not in error.message.lower()

