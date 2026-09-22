from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AuthenticatedOperator:
    operator_id: str


class AuthenticatedOperatorProvider(Protocol):
    def current(self) -> AuthenticatedOperator | None: ...

