"""Add schedules, commit metadata, execution observations, and failures."""
from alembic import op
import sqlalchemy as sa

revision = "002_execution_support"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("schedules", sa.Column("id", sa.String(36), primary_key=True), sa.Column("configuration_id", sa.String(36), sa.ForeignKey("monitoring_configurations.id"), unique=True, nullable=False), sa.Column("recurrence", sa.String(16), nullable=False), sa.Column("local_time", sa.String(16), nullable=False), sa.Column("weekday", sa.Integer()), sa.Column("day_of_month", sa.Integer()), sa.Column("timezone", sa.String(64), nullable=False), sa.Column("next_run_at", sa.DateTime(timezone=True)))
    op.create_table("schedule_occurrences", sa.Column("id", sa.String(36), primary_key=True), sa.Column("configuration_id", sa.String(36), sa.ForeignKey("monitoring_configurations.id"), nullable=False), sa.Column("due_at", sa.DateTime(timezone=True), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("execution_id", sa.String(36), sa.ForeignKey("mining_executions.id")), sa.Column("safe_reason", sa.String(512)), sa.UniqueConstraint("configuration_id", "due_at", name="uq_schedule_occurrence"))
    op.create_table("commits", sa.Column("id", sa.String(36), primary_key=True), sa.Column("repository_id", sa.String(255), nullable=False), sa.Column("commit_hash", sa.String(255), nullable=False), sa.Column("author_name", sa.String(320), nullable=False), sa.Column("author_email", sa.String(320)), sa.Column("committed_at", sa.DateTime(timezone=True), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("source_url", sa.String(1024)), sa.UniqueConstraint("repository_id", "commit_hash", name="uq_repository_commit"))
    op.create_table("execution_commits", sa.Column("id", sa.String(36), primary_key=True), sa.Column("execution_id", sa.String(36), sa.ForeignKey("mining_executions.id"), nullable=False), sa.Column("repository_execution_id", sa.String(36), sa.ForeignKey("repository_executions.id"), nullable=False), sa.Column("commit_hash", sa.String(255), nullable=False), sa.Column("verification_source", sa.String(16), nullable=False), sa.UniqueConstraint("execution_id", "repository_execution_id", "commit_hash", name="uq_execution_commit"))
    op.create_table("repository_failures", sa.Column("id", sa.String(36), primary_key=True), sa.Column("execution_id", sa.String(36), sa.ForeignKey("mining_executions.id"), nullable=False), sa.Column("repository_execution_id", sa.String(36), sa.ForeignKey("repository_executions.id"), nullable=False), sa.Column("stage", sa.String(64), nullable=False), sa.Column("code", sa.String(64), nullable=False), sa.Column("safe_reason", sa.String(512), nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False), sa.Column("continued", sa.Boolean(), nullable=False), sa.Column("correlation_id", sa.String(64), nullable=False))


def downgrade() -> None:
    for table in ["repository_failures", "execution_commits", "commits", "schedule_occurrences", "schedules"]:
        op.drop_table(table)

