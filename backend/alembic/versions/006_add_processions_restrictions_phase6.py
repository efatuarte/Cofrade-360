"""Add processions, street segments and restrictions

Revision ID: 006
Revises: 005
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa


revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(), nullable=False, server_default="user"))

    op.create_table(
        "street_segments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("geom", sa.Text(), nullable=False),
        sa.Column("width_estimate", sa.Float(), nullable=True),
        sa.Column("kind", sa.String(), nullable=False, server_default="street"),
        sa.Column("is_walkable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_street_segments_id", "street_segments", ["id"])

    op.create_table(
        "restricted_areas",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("geom", sa.Text(), nullable=False),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_restricted_areas_id", "restricted_areas", ["id"])

    op.create_table(
        "processions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("brotherhood_id", sa.String(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="scheduled"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["brotherhood_id"], ["hermandades.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_processions_id", "processions", ["id"])
    op.create_index("ix_processions_brotherhood_id", "processions", ["brotherhood_id"])
    op.create_index("ix_processions_date", "processions", ["date"])

    op.create_table(
        "procession_segment_occupations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("procession_id", sa.String(), nullable=False),
        sa.Column("street_segment_id", sa.String(), nullable=False),
        sa.Column("start_datetime", sa.DateTime(), nullable=False),
        sa.Column("end_datetime", sa.DateTime(), nullable=False),
        sa.Column("direction", sa.String(), nullable=False, server_default="unknown"),
        sa.Column("crowd_factor", sa.Float(), nullable=False, server_default="1.0"),
        sa.ForeignKeyConstraint(["procession_id"], ["processions.id"]),
        sa.ForeignKeyConstraint(["street_segment_id"], ["street_segments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_procession_segment_occupations_id", "procession_segment_occupations", ["id"])
    op.create_index("ix_procession_segment_occupations_procession_id", "procession_segment_occupations", ["procession_id"])
    op.create_index("ix_procession_segment_occupations_street_segment_id", "procession_segment_occupations", ["street_segment_id"])


def downgrade() -> None:
    op.drop_index("ix_procession_segment_occupations_street_segment_id", table_name="procession_segment_occupations")
    op.drop_index("ix_procession_segment_occupations_procession_id", table_name="procession_segment_occupations")
    op.drop_index("ix_procession_segment_occupations_id", table_name="procession_segment_occupations")
    op.drop_table("procession_segment_occupations")

    op.drop_index("ix_processions_date", table_name="processions")
    op.drop_index("ix_processions_brotherhood_id", table_name="processions")
    op.drop_index("ix_processions_id", table_name="processions")
    op.drop_table("processions")

    op.drop_index("ix_restricted_areas_id", table_name="restricted_areas")
    op.drop_table("restricted_areas")

    op.drop_index("ix_street_segments_id", table_name="street_segments")
    op.drop_table("street_segments")

    op.drop_column("users", "role")
