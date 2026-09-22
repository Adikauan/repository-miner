from __future__ import annotations

from dataclasses import dataclass

from repository_miner.mining.application.persistent_runner import run_execution


@dataclass(frozen=True)
class RunExecution:
    execution_id: str


class LocalExecutionDispatcher:
    """In-process dispatcher with durable execution state and independent sessions."""

    def __init__(self, session_factory, gateway, publisher=None) -> None:
        self._session_factory = session_factory
        self._gateway = gateway
        self._publisher = publisher

    def dispatch(self, command: RunExecution):
        with self._session_factory() as session:
            return run_execution(session, self._gateway, command.execution_id, self._publisher)
