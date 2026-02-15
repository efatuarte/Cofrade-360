"""Phase 14 crowd reports, signals and analytics

Revision ID: 012
Revises: 011
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa


revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crowd_reports",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("geohash", sa.String(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("is_flagged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crowd_reports_id", "crowd_reports", ["id"])
    op.create_index("ix_crowd_reports_user_id", "crowd_reports", ["user_id"])
    op.create_index("ix_crowd_reports_geohash", "crowd_reports", ["geohash"])
    op.create_index("ix_crowd_reports_created_at", "crowd_reports", ["created_at"])

    op.create_table(
        "crowd_signals",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("geohash", sa.String(), nullable=False),
        sa.Column("bucket_start", sa.DateTime(), nullable=False),
        sa.Column("bucket_end", sa.DateTime(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reports_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crowd_signals_id", "crowd_signals", ["id"])
    op.create_index("ix_crowd_signals_geohash", "crowd_signals", ["geohash"])
    op.create_index("ix_crowd_signals_bucket_start", "crowd_signals", ["bucket_start"])
    op.create_index("ix_crowd_signals_bucket_end", "crowd_signals", ["bucket_end"])

    op.create_table(
        "analytics_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("trace_id", sa.String(), nullable=True),
        sa.Column("payload", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analytics_events_id", "analytics_events", ["id"])
    op.create_index("ix_analytics_events_event_type", "analytics_events", ["event_type"])
    op.create_index("ix_analytics_events_user_id", "analytics_events", ["user_id"])
    op.create_index("ix_analytics_events_trace_id", "analytics_events", ["trace_id"])
    op.create_index("ix_analytics_events_created_at", "analytics_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_analytics_events_created_at", table_name="analytics_events")
    op.drop_index("ix_analytics_events_trace_id", table_name="analytics_events")
    op.drop_index("ix_analytics_events_user_id", table_name="analytics_events")
    op.drop_index("ix_analytics_events_event_type", table_name="analytics_events")
    op.drop_index("ix_analytics_events_id", table_name="analytics_events")
    op.drop_table("analytics_events")

    op.drop_index("ix_crowd_signals_bucket_end", table_name="crowd_signals")
    op.drop_index("ix_crowd_signals_bucket_start", table_name="crowd_signals")
    op.drop_index("ix_crowd_signals_geohash", table_name="crowd_signals")
    op.drop_index("ix_crowd_signals_id", table_name="crowd_signals")
    op.drop_table("crowd_signals")

    op.drop_index("ix_crowd_reports_created_at", table_name="crowd_reports")
    op.drop_index("ix_crowd_reports_geohash", table_name="crowd_reports")
    op.drop_index("ix_crowd_reports_user_id", table_name="crowd_reports")
    op.drop_index("ix_crowd_reports_id", table_name="crowd_reports")
    op.drop_table("crowd_reports")
