from __future__ import annotations

from repository_miner.authentication.application.ports import AuthenticatedOperator, AuthenticatedOperatorProvider


class RequestOperatorProvider(AuthenticatedOperatorProvider):
    def __init__(self, operator: AuthenticatedOperator | None) -> None:
        self._operator = operator

    def current(self) -> AuthenticatedOperator | None:
        return self._operator

