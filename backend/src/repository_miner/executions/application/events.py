from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

EVENT_TYPES = {"execution.started", "repository.started", "repository.progress", "unauthorized_commit.detected", "repository.completed", "repository.failed", "execution.completed", "execution.partially_completed", "execution.failed"}


@dataclass(frozen=True)
class ExecutionEvent:
    type: str
    execution_id: str
    configuration_id: str
    revision: int
    payload: dict[str, object]
    repository_id: str | None = None
    event_id: str = ""
    occurred_at: str = ""

    def envelope(self) -> dict[str, object]:
        if self.type not in EVENT_TYPES:
            raise ValueError("unsupported execution event")
        return {"schema_version": "1", "event_id": self.event_id or str(uuid4()), "type": self.type, "occurred_at": self.occurred_at or datetime.now(timezone.utc).isoformat(), "execution_id": self.execution_id, "configuration_id": self.configuration_id, "repository_id": self.repository_id, "revision": self.revision, "payload": self.payload}
