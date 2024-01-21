"""add all status data

Revision ID: 4bb5f8f3d841
Revises: 955ac9d18022
Create Date: 2022-12-01 00:34:43.723029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4bb5f8f3d841"
down_revision = "955ac9d18022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usage_points", sa.Column("call_number", sa.Integer(), nullable=True))
    op.add_column("usage_points", sa.Column("quota_reached", sa.Boolean(), nullable=True))
    op.add_column("usage_points", sa.Column("quota_limit", sa.Integer(), nullable=True))
    op.add_column("usage_points", sa.Column("quota_reset_at", sa.DateTime(), nullable=True))
    op.add_column("usage_points", sa.Column("last_call", sa.DateTime(), nullable=True))
    op.add_column("usage_points", sa.Column("ban", sa.Boolean(), nullable=True))


def downgrade() -> None:
    op.drop_column("usage_points", "call_number")
    op.drop_column("usage_points", "quota_reached")
    op.drop_column("usage_points", "quota_limit")
    op.drop_column("usage_points", "quota_reset_at")
    op.drop_column("usage_points", "last_call")
    op.drop_column("usage_points", "ban")
