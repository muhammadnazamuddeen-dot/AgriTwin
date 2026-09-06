"""add_crop_profile_fields

Revision ID: d4e2f1a8b3c7
Revises: c73918b910fa
Create Date: 2026-09-02 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e2f1a8b3c7'
down_revision: Union[str, None] = 'c73918b910fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('crops', sa.Column('irrigation', sa.String(length=50), nullable=True))
    op.add_column('crops', sa.Column('soil_type', sa.String(length=50), nullable=True))
    op.add_column('crops', sa.Column('farming_method', sa.String(length=50), nullable=True))
    op.add_column('crops', sa.Column('previous_crop', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('crops', 'previous_crop')
    op.drop_column('crops', 'farming_method')
    op.drop_column('crops', 'soil_type')
    op.drop_column('crops', 'irrigation')
