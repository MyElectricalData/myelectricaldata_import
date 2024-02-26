"""add powered table

Revision ID: c70a0702d76b
Revises: 0b5c52e4efba
Create Date: 2022-12-18 00:56:08.569184

"""
import sqlalchemy as sa
from sqlalchemy.sql import true

from alembic import op

# revision identifiers, used by Alembic.
revision = "c70a0702d76b"
down_revision = "0b5c52e4efba"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consumption_daily_max_power",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("usage_point_id", sa.Text(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("event_date", sa.DateTime(), nullable=True),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.Column("blacklist", sa.Integer(), nullable=False),
        sa.Column("fail_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["usage_point_id"],
            ["usage_points.usage_point_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sqlite_autoincrement=True,
    )
    op.create_index(
        op.f("ix_consumption_daily_max_power_id"),
        "consumption_daily_max_power",
        ["id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_consumption_daily_max_power_usage_point_id"),
        "consumption_daily_max_power",
        ["usage_point_id"],
        unique=False,
    )

    op.add_column(
        "usage_points",
        sa.Column("consumption_max_power", sa.Boolean(), nullable=False, server_default=true()),
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_consumption_daily_max_power_usage_point_id"),
        table_name="consumption_daily_max_power",
    )
    op.drop_index(
        op.f("ix_consumption_daily_max_power_id"),
        table_name="consumption_daily_max_power",
    )
    op.drop_table("consumption_daily_max_power")
    op.drop_column("usage_points", "consumption_max_power")
