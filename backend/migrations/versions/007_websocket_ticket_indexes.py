"""Index websocket tickets for expiry cleanup and consumed-ticket checks."""

from alembic import op

revision = "007_websocket_ticket_indexes"
down_revision = "006_canonical_execution_counters"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_websocket_tickets_expires_at", "websocket_tickets", ["expires_at"])
    op.create_index("ix_websocket_tickets_consumed_at", "websocket_tickets", ["consumed_at"])


def downgrade() -> None:
    op.drop_index("ix_websocket_tickets_consumed_at", table_name="websocket_tickets")
    op.drop_index("ix_websocket_tickets_expires_at", table_name="websocket_tickets")
