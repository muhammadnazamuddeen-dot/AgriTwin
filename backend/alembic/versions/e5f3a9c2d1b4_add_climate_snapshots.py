"""add_climate_snapshots

Revision ID: e5f3a9c2d1b4
Revises: d4e2f1a8b3c7
Create Date: 2026-09-03 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f3a9c2d1b4'
down_revision: Union[str, None] = 'd4e2f1a8b3c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'climate_snapshots',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('farm_id', sa.Integer(), sa.ForeignKey('farms.id', ondelete='CASCADE'), nullable=False),
        sa.Column('baseline_period', sa.String(length=20), nullable=False),
        sa.Column('historical_mean_temp_c', sa.Float(), nullable=True),
        sa.Column('temp_anomaly_c', sa.Float(), nullable=True),
        sa.Column('historical_mean_humidity_pct', sa.Float(), nullable=True),
        sa.Column('humidity_anomaly_pct', sa.Float(), nullable=True),
        sa.Column('historical_total_precip_mm', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    )
    op.create_index('idx_climate_snap_farm', 'climate_snapshots', ['farm_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('idx_climate_snap_farm', table_name='climate_snapshots')
    op.drop_table('climate_snapshots')
