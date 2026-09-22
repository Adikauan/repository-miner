from repository_miner.executions.application.event_publisher import ExecutionEventPublisher


EVENT_TYPES = (
    "execution.started", "repository.started", "repository.progress",
    "unauthorized_commit.detected", "repository.completed", "repository.failed",
    "execution.completed", "execution.partially_completed", "execution.failed",
)


def test_event_publisher_emits_all_contract_types_with_monotonic_revisions():
    publisher = ExecutionEventPublisher()
    for event_type in EVENT_TYPES:
        publisher.publish(event_type, "execution", "configuration", {"status": "running"})
    events = publisher.since("execution")
    assert [event["type"] for event in events] == list(EVENT_TYPES)
    assert [event["revision"] for event in events] == list(range(1, len(EVENT_TYPES) + 1))


def test_event_payload_is_identifier_only_for_unauthorized_commit():
    publisher = ExecutionEventPublisher()
    event = publisher.publish("unauthorized_commit.detected", "execution", "configuration", {"alert_id": "alert", "commit_hash": "abc"}, repository_id="repo")
    assert set(event["payload"]) == {"alert_id", "commit_hash"}
    assert "token" not in str(event).lower()
