"""Persist immutable execution input snapshot."""
from alembic import op
import sqlalchemy as sa

revision = "004_execution_snapshot"
down_revision = "003_execution_operator"
branch_labels = None
depends_on = None


def upgrade() -> None:
    existing = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("mining_executions")}
    if "snapshot_json" not in existing:
        op.add_column("mining_executions", sa.Column("snapshot_json", sa.Text(), nullable=True))
    if "snapshot_created_at" not in existing:
        op.add_column("mining_executions", sa.Column("snapshot_created_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("mining_executions", "snapshot_created_at")
    op.drop_column("mining_executions", "snapshot_json")
