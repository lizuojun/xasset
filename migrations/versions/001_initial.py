"""initial

Revision ID: 001
Revises:
Create Date: 2026-03-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 实际执行时由 alembic revision --autogenerate 生成
    # 此占位文件仅用于记录迁移链起点
    pass


def downgrade() -> None:
    pass
