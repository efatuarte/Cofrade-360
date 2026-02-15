"""Add user notification settings for phase 9

Revision ID: 007
Revises: 006
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa


revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("notifications_processions", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column(
        "users",
        sa.Column("notifications_restrictions", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade() -> None:
    op.drop_column("users", "notifications_restrictions")
    op.drop_column("users", "notifications_processions")
