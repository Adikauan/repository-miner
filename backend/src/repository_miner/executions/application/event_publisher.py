from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4


class ExecutionEventPublisher:
    """Best-effort in-process event hub; durable state remains in SQLAlchemy."""
    def __init__(self) -> None:
        self._events: dict[str, list[dict[str, object]]] = {}
        self._revisions: dict[str, int] = {}
        self._lock = Lock()

    def publish(self, event_type: str, execution_id: str, configuration_id: str, payload: dict[str, object], *, repository_id: str | None = None) -> dict[str, object]:
        with self._lock:
            revision = self._revisions.get(execution_id, 0) + 1
            event = {
                "schema_version": "1", "event_id": str(uuid4()), "type": event_type,
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "execution_id": execution_id, "configuration_id": configuration_id,
                "repository_id": repository_id, "revision": revision, "payload": payload,
            }
            self._revisions[execution_id] = revision
            self._events.setdefault(execution_id, []).append(event)
            return event

    def since(self, execution_id: str, revision: int = 0) -> list[dict[str, object]]:
        with self._lock:
            return [event for event in self._events.get(execution_id, []) if int(event["revision"]) > revision]


publisher = ExecutionEventPublisher()
