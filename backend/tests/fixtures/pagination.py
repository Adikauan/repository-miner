from datetime import UTC, datetime
from uuid import uuid4

from repository_miner.persistence.models import MiningExecution, MonitoringConfiguration


def configuration_record(configuration_id: str, *, name: str | None = None) -> MonitoringConfiguration:
    """Build a synthetic plan without persisting credentials or contacting GitLab."""
    return MonitoringConfiguration(
        id=configuration_id,
        name=name or f"Plan {configuration_id}",
        gitlab_base_url="https://gitlab.example.com",
        timezone="UTC",
        target_branch="QA",
        enabled=True,
    )


def execution_record(
    configuration_id: str,
    *,
    started_at: datetime | None,
    status: str = "completed",
    execution_id: str | None = None,
) -> MiningExecution:
    return MiningExecution(
        id=execution_id or str(uuid4()),
        configuration_id=configuration_id,
        status=status,
        started_at=started_at,
        repositories_total=1,
        repositories_completed=1,
        repositories_failed=0,
        commits_discovered=1,
        commits_verified=1,
        allowed_commits=1,
        unauthorized_commits=0,
    )


def timestamp(day: int) -> datetime:
    return datetime(2026, 1, day, tzinfo=UTC)
