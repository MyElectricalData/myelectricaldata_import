"""add enable, progress & progress_status to usage_points

Revision ID: 09d887b265a5
Revises: 0c07baa8d7b2
Create Date: 2022-11-21 00:40:16.407209

"""
import sqlalchemy as sa
from sqlalchemy.sql import true

from alembic import op

# revision identifiers, used by Alembic.
revision = "09d887b265a5"
down_revision = "0c07baa8d7b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usage_points",
        sa.Column("progress", sa.Integer, nullable=False, server_default="0"),
    )
    op.add_column(
        "usage_points",
        sa.Column("progress_status", sa.Text, nullable=False, server_default=""),
    )
    op.add_column(
        "usage_points",
        sa.Column("enable", sa.Boolean, nullable=False, server_default=true()),
    )


def downgrade() -> None:
    op.drop_column("usage_points", "progress")
    op.drop_column("usage_points", "progress_status")
    op.drop_column("usage_points", "enable")
