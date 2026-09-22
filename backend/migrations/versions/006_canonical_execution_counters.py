"""Add canonical execution repository counters."""
from alembic import op
import sqlalchemy as sa

revision = "006_canonical_execution_counters"
down_revision = "005_baseline_reset_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    existing = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("mining_executions")}
    if "repositories_total" not in existing:
        op.add_column("mining_executions", sa.Column("repositories_total", sa.Integer(), nullable=False, server_default="0"))
    if "repositories_completed" not in existing:
        op.add_column("mining_executions", sa.Column("repositories_completed", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("mining_executions", "repositories_completed")
    op.drop_column("mining_executions", "repositories_total")
