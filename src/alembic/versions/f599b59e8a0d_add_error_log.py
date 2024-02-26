"""add error log

Revision ID: f599b59e8a0d
Revises: b3505740913d
Create Date: 2023-08-25 23:28:45.184756

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f599b59e8a0d"
down_revision = "b3505740913d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usage_points", sa.Column("last_error", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("usage_points", "last_error")
