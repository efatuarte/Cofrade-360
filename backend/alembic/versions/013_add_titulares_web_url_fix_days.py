"""Add titulares table, web_url to hermandades, fix viernes_dolores/sabado_pasion

Revision ID: 013
Revises: 012
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add web_url to hermandades
    op.add_column("hermandades", sa.Column("web_url", sa.String(), nullable=True))

    # Create titulares table
    op.create_table(
        "titulares",
        sa.Column("id", sa.String(), primary_key=True, index=True),
        sa.Column("brotherhood_id", sa.String(), sa.ForeignKey("hermandades.id"), nullable=False, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False, server_default="unknown"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Fix ss_day values: viernes_santo -> viernes_dolores for Viernes de Dolores brotherhoods,
    # sabado_santo -> sabado_pasion for Sabado de Pasion brotherhoods.
    # We identify them by name_short since that's what the seed/import uses.
    viernes_dolores_names = (
        "Pino Montano", "La Misión", "Dulce Nombre (Bellavista)",
        "Pasión y Muerte", "Bendición y Esperanza", "Stmo. Cristo de la Corona",
    )
    sabado_pasion_names = (
        "Padre Pío", "Divino Perdón", "Torreblanca",
        "San José Obrero", "La Milagrosa",
    )

    conn = op.get_bind()
    for name in viernes_dolores_names:
        conn.execute(
            sa.text("UPDATE hermandades SET ss_day = 'viernes_dolores' WHERE name_short = :name AND ss_day = 'viernes_santo'"),
            {"name": name},
        )
    for name in sabado_pasion_names:
        conn.execute(
            sa.text("UPDATE hermandades SET ss_day = 'sabado_pasion' WHERE name_short = :name AND ss_day = 'sabado_santo'"),
            {"name": name},
        )


def downgrade() -> None:
    # Revert ss_day values
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE hermandades SET ss_day = 'viernes_santo' WHERE ss_day = 'viernes_dolores'"))
    conn.execute(sa.text("UPDATE hermandades SET ss_day = 'sabado_santo' WHERE ss_day = 'sabado_pasion'"))

    op.drop_table("titulares")
    op.drop_column("hermandades", "web_url")
