"""Add brotherhood phase-3 fields and media assets

Revision ID: 004
Revises: 003
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa


revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "media_assets",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("mime", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("brotherhood_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["brotherhood_id"], ["hermandades.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_media_assets_id", "media_assets", ["id"])

    op.add_column("hermandades", sa.Column("name_short", sa.String(), nullable=True))
    op.add_column("hermandades", sa.Column("name_full", sa.String(), nullable=True))
    op.add_column("hermandades", sa.Column("logo_asset_id", sa.String(), nullable=True))
    op.add_column("hermandades", sa.Column("church_id", sa.String(), nullable=True))
    op.add_column("hermandades", sa.Column("ss_day", sa.String(), nullable=True))
    op.add_column("hermandades", sa.Column("history", sa.Text(), nullable=True))
    op.add_column("hermandades", sa.Column("highlights", sa.Text(), nullable=True))
    op.add_column("hermandades", sa.Column("stats", sa.Text(), nullable=True))

    op.create_foreign_key(
        "fk_hermandades_logo_asset",
        "hermandades",
        "media_assets",
        ["logo_asset_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_hermandades_church",
        "hermandades",
        "locations",
        ["church_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_hermandades_church", "hermandades", type_="foreignkey")
    op.drop_constraint("fk_hermandades_logo_asset", "hermandades", type_="foreignkey")

    op.drop_column("hermandades", "stats")
    op.drop_column("hermandades", "highlights")
    op.drop_column("hermandades", "history")
    op.drop_column("hermandades", "ss_day")
    op.drop_column("hermandades", "church_id")
    op.drop_column("hermandades", "logo_asset_id")
    op.drop_column("hermandades", "name_full")
    op.drop_column("hermandades", "name_short")

    op.drop_index("ix_media_assets_id", table_name="media_assets")
    op.drop_table("media_assets")
