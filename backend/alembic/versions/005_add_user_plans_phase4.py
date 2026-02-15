"""Add user plans and plan items for itinerary phase 4

Revision ID: 005
Revises: 004
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa


revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_plans",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("plan_date", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_plans_id", "user_plans", ["id"])
    op.create_index("ix_user_plans_user_id", "user_plans", ["user_id"])

    op.create_table(
        "plan_items",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("plan_id", sa.String(), nullable=False),
        sa.Column("item_type", sa.String(), nullable=False),
        sa.Column("event_id", sa.String(), nullable=True),
        sa.Column("brotherhood_id", sa.String(), nullable=True),
        sa.Column("desired_time_start", sa.DateTime(), nullable=False),
        sa.Column("desired_time_end", sa.DateTime(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["brotherhood_id"], ["hermandades.id"]),
        sa.ForeignKeyConstraint(["event_id"], ["eventos.id"]),
        sa.ForeignKeyConstraint(["plan_id"], ["user_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_plan_items_id", "plan_items", ["id"])
    op.create_index("ix_plan_items_plan_id", "plan_items", ["plan_id"])


def downgrade() -> None:
    op.drop_index("ix_plan_items_plan_id", table_name="plan_items")
    op.drop_index("ix_plan_items_id", table_name="plan_items")
    op.drop_table("plan_items")

    op.drop_index("ix_user_plans_user_id", table_name="user_plans")
    op.drop_index("ix_user_plans_id", table_name="user_plans")
    op.drop_table("user_plans")
