from __future__ import annotations

from fastapi import Header

from repository_miner.authentication.application.ports import AuthenticatedOperator


def host_operator(x_operator_id: str | None = Header(default=None)) -> AuthenticatedOperator | None:
    if not x_operator_id or not x_operator_id.strip():
        return None
    value = x_operator_id.strip()
    if len(value) > 128:
        return None
    return AuthenticatedOperator(value)

