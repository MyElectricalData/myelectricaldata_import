"""add enable, progress & progress_status to usage_points

Revision ID: 3bfb136b0221
Revises: 
Create Date: 2022-11-20 23:14:25.960204

"""
import sqlalchemy as sa
from sqlalchemy.sql import false

from alembic import op

# revision identifiers, used by Alembic.
revision = '3bfb136b0221'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('usage_points', sa.Column('progress', sa.Integer, nullable=False, server_default="0"))

    op.add_column('usage_points', sa.Column('progress_status', sa.Text, nullable=False, server_default=""))

    op.add_column('usage_points', sa.Column('enable', sa.Boolean, nullable=False, server_default=false()))


def downgrade() -> None:
    op.drop_column('usage_points', 'progress')
    op.drop_column('usage_points', 'progress_status')
    op.drop_column('usage_points', 'enable')
