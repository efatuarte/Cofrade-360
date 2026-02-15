"""Phase 13 notification events

Revision ID: 011
Revises: 010
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa


revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notification_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("plan_id", sa.String(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notification_events_id", "notification_events", ["id"])
    op.create_index("ix_notification_events_plan_id", "notification_events", ["plan_id"])
    op.create_index("ix_notification_events_user_id", "notification_events", ["user_id"])
    op.create_index("ix_notification_events_kind", "notification_events", ["kind"])
    op.create_index("ix_notification_events_created_at", "notification_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_notification_events_created_at", table_name="notification_events")
    op.drop_index("ix_notification_events_kind", table_name="notification_events")
    op.drop_index("ix_notification_events_user_id", table_name="notification_events")
    op.drop_index("ix_notification_events_plan_id", table_name="notification_events")
    op.drop_index("ix_notification_events_id", table_name="notification_events")
    op.drop_table("notification_events")
