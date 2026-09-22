"""Persist explicit, operator-audited baseline resets."""
from alembic import op
import sqlalchemy as sa

revision = "005_baseline_reset_audit"
down_revision = "004_execution_snapshot"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if "baseline_reset_audits" not in inspector.get_table_names():
        op.create_table(
            "baseline_reset_audits",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("configuration_id", sa.String(36), sa.ForeignKey("monitoring_configurations.id"), nullable=False),
            sa.Column("repository_id", sa.String(255), nullable=False),
            sa.Column("branch", sa.String(255), nullable=False),
            sa.Column("previous_checkpoint_hash", sa.String(255), nullable=True),
            sa.Column("new_baseline_hash", sa.String(255), nullable=False),
            sa.Column("operator_id", sa.String(255), nullable=False),
            sa.Column("reason", sa.String(1024), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )


def downgrade() -> None:
    op.drop_table("baseline_reset_audits")
