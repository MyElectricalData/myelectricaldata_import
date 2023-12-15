"""add temporal plan

Revision ID: 77be9c54cd4f
Revises: e990284249e4
Create Date: 2023-12-13 23:10:36.731326

"""
from alembic import op
import sqlalchemy as sa
# from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '77be9c54cd4f'
down_revision = 'e990284249e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usage_point_id', sa.Text(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('price', sa.Text(), nullable=True),
        sa.Column('offpeak_hours', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sqlite_autoincrement=True
    )
    op.create_index(op.f('ix_plan_id'), 'plan', ['id'], unique=True)
    op.create_index(op.f('ix_plan_usage_point_id'), 'plan', ['usage_point_id'], unique=False)
    op.create_index(op.f('ix_plan_date'), 'plan', ['date'], unique=False)


def downgrade() -> None:
    op.drop_table('plan')
