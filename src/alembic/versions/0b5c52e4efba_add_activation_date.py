"""add activation_date

Revision ID: 0b5c52e4efba
Revises: 4bb5f8f3d841
Create Date: 2022-12-01 11:24:40.203828

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "0b5c52e4efba"
down_revision = "4bb5f8f3d841"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usage_points", sa.Column("consumption_max_date", sa.DateTime(), nullable=True))
    op.add_column(
        "usage_points",
        sa.Column("consumption_detail_max_date", sa.DateTime(), nullable=True),
    )
    op.add_column("usage_points", sa.Column("production_max_date", sa.DateTime(), nullable=True))
    op.add_column(
        "usage_points",
        sa.Column("production_detail_max_date", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("usage_points", "consumption_max_date")
    op.drop_column("usage_points", "consumption_detail_max_date")
    op.drop_column("usage_points", "production_max_date")
    op.drop_column("usage_points", "production_detail_max_date")
