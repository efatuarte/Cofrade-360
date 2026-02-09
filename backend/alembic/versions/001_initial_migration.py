"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-02-09

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    
    # Create hermandades table
    op.create_table(
        'hermandades',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('escudo', sa.String(), nullable=True),
        sa.Column('sede', sa.String(), nullable=True),
        sa.Column('fecha_fundacion', sa.DateTime(), nullable=True),
        sa.Column('ubicacion', geoalchemy2.Geometry('POINT', srid=4326), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_hermandades_id', 'hermandades', ['id'])
    
    # Create eventos table
    op.create_table(
        'eventos',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('titulo', sa.String(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('fecha_hora', sa.DateTime(), nullable=False),
        sa.Column('hermandad_id', sa.String(), nullable=False),
        sa.Column('ubicacion', sa.String(), nullable=True),
        sa.Column('ubicacion_geo', geoalchemy2.Geometry('POINT', srid=4326), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_eventos_id', 'eventos', ['id'])
    
    # Create rutas table
    op.create_table(
        'rutas',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('puntos', geoalchemy2.Geometry('LINESTRING', srid=4326), nullable=True),
        sa.Column('distancia_metros', sa.Integer(), nullable=True),
        sa.Column('duracion_minutos', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rutas_id', 'rutas', ['id'])
    
    # Create nodos table
    op.create_table(
        'nodos',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('ubicacion', geoalchemy2.Geometry('POINT', srid=4326), nullable=False),
        sa.Column('tipo', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_nodos_id', 'nodos', ['id'])
    
    # Create aristas table
    op.create_table(
        'aristas',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('nodo_origen', sa.String(), nullable=False),
        sa.Column('nodo_destino', sa.String(), nullable=False),
        sa.Column('geometria', geoalchemy2.Geometry('LINESTRING', srid=4326), nullable=True),
        sa.Column('distancia_metros', sa.Integer(), nullable=True),
        sa.Column('costo', sa.Integer(), nullable=True),
        sa.Column('bloqueada', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_aristas_id', 'aristas', ['id'])


def downgrade() -> None:
    op.drop_index('ix_aristas_id', table_name='aristas')
    op.drop_table('aristas')
    op.drop_index('ix_nodos_id', table_name='nodos')
    op.drop_table('nodos')
    op.drop_index('ix_rutas_id', table_name='rutas')
    op.drop_table('rutas')
    op.drop_index('ix_eventos_id', table_name='eventos')
    op.drop_table('eventos')
    op.drop_index('ix_hermandades_id', table_name='hermandades')
    op.drop_table('hermandades')
