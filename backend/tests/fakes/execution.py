from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from repository_miner.authentication.application.ports import AuthenticatedOperator


class FakeClock:
    def __init__(self, current: datetime | None = None) -> None:
        self.current_time = current or datetime.now(timezone.utc)

    def now(self) -> datetime:
        return self.current_time

    def advance(self, **kwargs: int) -> datetime:
        from datetime import timedelta

        self.current_time += timedelta(**kwargs)
        return self.current_time


class FakeAuthenticatedOperatorProvider:
    def __init__(self, operator_id: str | None = "operator-1") -> None:
        self.operator_id = operator_id

    def current(self) -> AuthenticatedOperator | None:
        return AuthenticatedOperator(self.operator_id) if self.operator_id else None


class RecordingEventPublisher:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def publish(self, event_type: str, execution_id: str, configuration_id: str, payload: dict[str, object], *, repository_id: str | None = None) -> dict[str, object]:
        event = {"type": event_type, "execution_id": execution_id, "configuration_id": configuration_id, "repository_id": repository_id, "payload": payload, "revision": len(self.events) + 1}
        self.events.append(event)
        return event

    def since(self, execution_id: str, revision: int = 0) -> list[dict[str, object]]:
        return [event for event in self.events if event["execution_id"] == execution_id and int(event["revision"]) > revision]


class LocalDispatcher:
    """Synchronous dispatcher for tests; no queue or background worker needed."""
    def __init__(self) -> None:
        self.commands: list[object] = []

    def dispatch(self, command: object, handler: Callable[[object], object] | None = None) -> object | None:
        self.commands.append(command)
        return handler(command) if handler else None
