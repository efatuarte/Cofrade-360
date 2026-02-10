"""Add locations table and expand eventos

Revision ID: 003
Revises: 002
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create locations table
    op.create_table(
        'locations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lng', sa.Float(), nullable=True),
        sa.Column('kind', sa.String(), server_default='other', nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_locations_id', 'locations', ['id'])

    # 2. Add new columns to eventos
    op.add_column('eventos', sa.Column('tipo', sa.String(), server_default='otro'))
    op.add_column('eventos', sa.Column('fecha_inicio', sa.DateTime(), nullable=True))
    op.add_column('eventos', sa.Column('fecha_fin', sa.DateTime(), nullable=True))
    op.add_column('eventos', sa.Column('location_id', sa.String(), nullable=True))
    op.add_column('eventos', sa.Column('precio', sa.Float(), server_default='0'))
    op.add_column('eventos', sa.Column('moneda', sa.String(), server_default='EUR'))
    op.add_column('eventos', sa.Column('es_gratuito', sa.Boolean(), server_default='true'))
    op.add_column('eventos', sa.Column('poster_asset_id', sa.String(), nullable=True))
    op.add_column('eventos', sa.Column('estado', sa.String(), server_default='programado'))

    # 3. Copy existing fecha_hora -> fecha_inicio for any existing rows
    op.execute('UPDATE eventos SET fecha_inicio = fecha_hora WHERE fecha_inicio IS NULL')

    # 4. Make fecha_inicio NOT NULL
    op.alter_column('eventos', 'fecha_inicio', nullable=False)

    # 5. Make hermandad_id nullable
    op.alter_column('eventos', 'hermandad_id', existing_type=sa.String(), nullable=True)

    # 6. Add FK for location_id
    op.create_foreign_key('fk_eventos_location', 'eventos', 'locations', ['location_id'], ['id'])

    # 7. Drop old columns
    op.drop_column('eventos', 'fecha_hora')
    op.drop_column('eventos', 'ubicacion')
    # Drop geometry column (spatial index auto-dropped with column in PostGIS)
    op.execute('ALTER TABLE eventos DROP COLUMN IF EXISTS ubicacion_geo')


def downgrade() -> None:
    # Re-add old columns
    op.add_column('eventos', sa.Column('fecha_hora', sa.DateTime(), nullable=True))
    op.add_column('eventos', sa.Column('ubicacion', sa.String(), nullable=True))
    op.execute('UPDATE eventos SET fecha_hora = fecha_inicio')
    op.alter_column('eventos', 'fecha_hora', nullable=False)
    op.alter_column('eventos', 'hermandad_id', existing_type=sa.String(), nullable=False)

    op.drop_constraint('fk_eventos_location', 'eventos', type_='foreignkey')
    op.drop_column('eventos', 'estado')
    op.drop_column('eventos', 'poster_asset_id')
    op.drop_column('eventos', 'es_gratuito')
    op.drop_column('eventos', 'moneda')
    op.drop_column('eventos', 'precio')
    op.drop_column('eventos', 'location_id')
    op.drop_column('eventos', 'fecha_fin')
    op.drop_column('eventos', 'fecha_inicio')
    op.drop_column('eventos', 'tipo')

    op.drop_index('ix_locations_id', table_name='locations')
    op.drop_table('locations')
