import logging

from repository_miner.shared.api.errors import safe_gitlab_error
from repository_miner.shared.domain.types import GitLabErrorCode
from repository_miner.shared.infrastructure.logging import SecretRedactionFilter


def test_secret_redaction_filter_replaces_sensitive_log_message():
    record = logging.LogRecord("test", logging.ERROR, __file__, 1, "token=%s", (), None)
    record.msg = "Authorization: Bearer super-secret"
    SecretRedactionFilter().filter(record)
    assert "super-secret" not in record.getMessage()
    assert "redacted" in record.getMessage().lower()


def test_gitlab_errors_are_stable_and_secret_free():
    secret = "glpat-private-value"
    for code in GitLabErrorCode:
        error = safe_gitlab_error(code)
        assert error.code == code.value
        assert secret not in error.message
        assert error.details is None
