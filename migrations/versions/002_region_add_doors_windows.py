"""region add doors and windows columns

Revision ID: 002
Revises: 001
Create Date: 2026-04-09

"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('region', sa.Column('doors', sa.JSON(), nullable=True))
    op.add_column('region', sa.Column('windows', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('region', 'windows')
    op.drop_column('region', 'doors')
