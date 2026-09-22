"""Bind executions to their initiating operator when available."""
from alembic import op
import sqlalchemy as sa

revision = "003_execution_operator"
down_revision = "002_execution_support"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("mining_executions", sa.Column("created_by_operator_id", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("mining_executions", "created_by_operator_id")
