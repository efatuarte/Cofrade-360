"""Phase 12 street graph and routing restrictions

Revision ID: 010
Revises: 009
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa


revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "street_nodes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("geom", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_street_nodes_id", "street_nodes", ["id"])

    op.create_table(
        "street_edges",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("source_node", sa.String(), nullable=False),
        sa.Column("target_node", sa.String(), nullable=False),
        sa.Column("geom", sa.Text(), nullable=False),
        sa.Column("length_m", sa.Float(), nullable=False),
        sa.Column("width_estimate", sa.Float(), nullable=True),
        sa.Column("highway_type", sa.String(), nullable=True),
        sa.Column("is_walkable", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["source_node"], ["street_nodes.id"]),
        sa.ForeignKeyConstraint(["target_node"], ["street_nodes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_street_edges_id", "street_edges", ["id"])
    op.create_index("ix_street_edges_source_node", "street_edges", ["source_node"])
    op.create_index("ix_street_edges_target_node", "street_edges", ["target_node"])

    op.create_table(
        "route_restrictions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("edge_id", sa.String(), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("severity", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["edge_id"], ["street_edges.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_route_restrictions_id", "route_restrictions", ["id"])
    op.create_index("ix_route_restrictions_edge_id", "route_restrictions", ["edge_id"])
    op.create_index("ix_route_restrictions_starts_at", "route_restrictions", ["starts_at"])
    op.create_index("ix_route_restrictions_ends_at", "route_restrictions", ["ends_at"])


def downgrade() -> None:
    op.drop_index("ix_route_restrictions_ends_at", table_name="route_restrictions")
    op.drop_index("ix_route_restrictions_starts_at", table_name="route_restrictions")
    op.drop_index("ix_route_restrictions_edge_id", table_name="route_restrictions")
    op.drop_index("ix_route_restrictions_id", table_name="route_restrictions")
    op.drop_table("route_restrictions")

    op.drop_index("ix_street_edges_target_node", table_name="street_edges")
    op.drop_index("ix_street_edges_source_node", table_name="street_edges")
    op.drop_index("ix_street_edges_id", table_name="street_edges")
    op.drop_table("street_edges")

    op.drop_index("ix_street_nodes_id", table_name="street_nodes")
    op.drop_table("street_nodes")
