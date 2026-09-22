from __future__ import annotations

from repository_miner.persistence.store import Configuration


def require_validated_scope(configuration: Configuration) -> None:
    if not configuration.connection_validated:
        raise ValueError("connection_not_validated")

