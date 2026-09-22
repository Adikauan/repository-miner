from datetime import datetime, timezone
from uuid import uuid4

from repository_miner.executions.application.event_publisher import ExecutionEventPublisher


def test_execution_event_lifecycle_is_observable_and_revisions_are_monotonic():
    publisher = ExecutionEventPublisher()
    execution_id, configuration_id = str(uuid4()), str(uuid4())
    publisher.publish("execution.started", execution_id, configuration_id, {"status": "running"})
    publisher.publish("execution.completed", execution_id, configuration_id, {"status": "completed", "summary_counts": {"commits_discovered": 0}})
    events = publisher.since(execution_id)
    assert [event["type"] for event in events] == ["execution.started", "execution.completed"]
    assert [event["revision"] for event in events] == [1, 2]
