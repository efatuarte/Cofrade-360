"""Add procession schedules, itinerary text and provenance metadata

Revision ID: 008
Revises: 007
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "procession_schedule_points",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("procession_id", sa.String(), nullable=False),
        sa.Column("point_type", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("scheduled_datetime", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["procession_id"], ["processions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_procession_schedule_points_id", "procession_schedule_points", ["id"])
    op.create_index("ix_procession_schedule_points_procession_id", "procession_schedule_points", ["procession_id"])

    op.create_table(
        "procession_itinerary_texts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("procession_id", sa.String(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(), nullable=True),
        sa.Column("accessed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["procession_id"], ["processions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("procession_id"),
    )
    op.create_index("ix_procession_itinerary_texts_id", "procession_itinerary_texts", ["id"])
    op.create_index("ix_procession_itinerary_texts_procession_id", "procession_itinerary_texts", ["procession_id"])

    op.create_table(
        "data_provenance",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("source_url", sa.String(), nullable=False),
        sa.Column("accessed_at", sa.DateTime(), nullable=False),
        sa.Column("fields_extracted", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_provenance_id", "data_provenance", ["id"])
    op.create_index("ix_data_provenance_entity_id", "data_provenance", ["entity_id"])


def downgrade() -> None:
    op.drop_index("ix_data_provenance_entity_id", table_name="data_provenance")
    op.drop_index("ix_data_provenance_id", table_name="data_provenance")
    op.drop_table("data_provenance")

    op.drop_index("ix_procession_itinerary_texts_procession_id", table_name="procession_itinerary_texts")
    op.drop_index("ix_procession_itinerary_texts_id", table_name="procession_itinerary_texts")
    op.drop_table("procession_itinerary_texts")

    op.drop_index("ix_procession_schedule_points_procession_id", table_name="procession_schedule_points")
    op.drop_index("ix_procession_schedule_points_id", table_name="procession_schedule_points")
    op.drop_table("procession_schedule_points")
