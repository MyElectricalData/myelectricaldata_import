"""add annual period start

Revision ID: d4f21c9a8b6e
Revises: e990284249e4
Create Date: 2026-09-11 00:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

revision = "d4f21c9a8b6e"
down_revision = "e990284249e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usage_points",
        sa.Column("annual_period_start", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("usage_points", "annual_period_start")
