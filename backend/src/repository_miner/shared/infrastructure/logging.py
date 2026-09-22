from __future__ import annotations

import logging


class SecretRedactionFilter(logging.Filter):
    """Redacts common GitLab credential fields before records leave the process."""

    _markers = ("PRIVATE-TOKEN", "Authorization", "gitlab_token", "access_token")

    def filter(self, record: logging.LogRecord) -> bool:
        message = str(record.getMessage())
        for marker in self._markers:
            if marker in message:
                record.msg = "Sensitive integration details redacted"
                record.args = ()
                break
        return True

