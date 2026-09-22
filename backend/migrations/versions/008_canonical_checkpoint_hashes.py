"""Use canonical hash terminology for incremental checkpoints."""

from alembic import op
import sqlalchemy as sa


revision = "008_canonical_checkpoint_hashes"
down_revision = "007_websocket_ticket_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("repository_checkpoints")}
    with op.batch_alter_table("repository_checkpoints") as batch:
        if "baseline_sha" in columns and "baseline_hash" not in columns:
            batch.alter_column("baseline_sha", new_column_name="baseline_hash", existing_type=sa.String(length=255), existing_nullable=False)
        if "last_processed_sha" in columns and "last_processed_hash" not in columns:
            batch.alter_column("last_processed_sha", new_column_name="last_processed_hash", existing_type=sa.String(length=255), existing_nullable=False)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("repository_checkpoints")}
    with op.batch_alter_table("repository_checkpoints") as batch:
        if "baseline_hash" in columns and "baseline_sha" not in columns:
            batch.alter_column("baseline_hash", new_column_name="baseline_sha", existing_type=sa.String(length=255), existing_nullable=False)
        if "last_processed_hash" in columns and "last_processed_sha" not in columns:
            batch.alter_column("last_processed_hash", new_column_name="last_processed_sha", existing_type=sa.String(length=255), existing_nullable=False)
