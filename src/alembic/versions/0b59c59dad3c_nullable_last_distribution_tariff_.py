"""nullable last_distribution_tariff_change_date in contract

Revision ID: 0b59c59dad3c
Revises: c70a0702d76b
Create Date: 2022-12-30 16:29:42.282094

"""
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import column, table

from alembic import op

# revision identifiers, used by Alembic.
revision = "0b59c59dad3c"
down_revision = "c70a0702d76b"
branch_labels = None
depends_on = None

Base = declarative_base()


def upgrade() -> None:
    conn = op.get_bind()
    res = conn.execute("select * from contracts order by id;")
    contracts_data = res.fetchall()

    op.rename_table("contracts", "contracts_old")
    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usage_point_id", sa.Text(), nullable=False),
        sa.Column("usage_point_status", sa.Text(), nullable=True),
        sa.Column("meter_type", sa.Text(), nullable=True),
        sa.Column("segment", sa.Text(), nullable=True),
        sa.Column("subscribed_power", sa.Text(), nullable=True),
        sa.Column("last_activation_date", sa.DateTime(), nullable=True),
        sa.Column("distribution_tariff", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_0", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_1", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_2", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_3", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_4", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_5", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_6", sa.Text(), nullable=True),
        sa.Column("contract_status", sa.Text(), nullable=True),
        sa.Column("last_distribution_tariff_change_date", sa.DateTime(), nullable=True),
        sa.Column("count", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["usage_point_id"],
            ["usage_points.usage_point_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    contracts = table(
        "contracts",
        column("id", Integer),
        column("usage_point_id", Text),
        column("usage_point_status", Text),
        column("meter_type", Text),
        column("segment", Text),
        column("subscribed_power", Text),
        column("last_activation_date", DateTime),
        column("distribution_tariff", Text),
        column("offpeak_hours_0", Text),
        column("offpeak_hours_1", Text),
        column("offpeak_hours_2", Text),
        column("offpeak_hours_3", Text),
        column("offpeak_hours_4", Text),
        column("offpeak_hours_5", Text),
        column("offpeak_hours_6", Text),
        column("contract_status", Text),
        column("last_distribution_tariff_change_date", DateTime),
        column("count", Integer),
    )

    data = []
    for contract in contracts_data:
        last_activation_date = datetime.strptime(contract[6], "%Y-%m-%d %H:%M:%S.%f")
        last_distribution_tariff_change_date = datetime.strptime(contract[16], "%Y-%m-%d %H:%M:%S.%f")
        data.append(
            {
                "id": contract[0],
                "usage_point_id": contract[1],
                "usage_point_status": contract[2],
                "meter_type": contract[3],
                "segment": contract[4],
                "subscribed_power": contract[5],
                "last_activation_date": last_activation_date,
                "distribution_tariff": contract[7],
                "offpeak_hours_0": contract[8],
                "offpeak_hours_1": contract[9],
                "offpeak_hours_2": contract[10],
                "offpeak_hours_3": contract[11],
                "offpeak_hours_4": contract[12],
                "offpeak_hours_5": contract[13],
                "offpeak_hours_6": contract[14],
                "contract_status": contract[15],
                "last_distribution_tariff_change_date": last_distribution_tariff_change_date,
                "count": contract[17],
            }
        )

    op.bulk_insert(contracts, data)
    op.drop_table("contracts_old")


def downgrade() -> None:
    conn = op.get_bind()
    res = conn.execute("select * from contracts order by id;")
    contracts_data = res.fetchall()

    op.rename_table("contracts", "contracts_old")
    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usage_point_id", sa.Text(), nullable=False),
        sa.Column("usage_point_status", sa.Text(), nullable=False),
        sa.Column("meter_type", sa.Text(), nullable=False),
        sa.Column("segment", sa.Text(), nullable=False),
        sa.Column("subscribed_power", sa.Text(), nullable=False),
        sa.Column("last_activation_date", sa.DateTime(), nullable=False),
        sa.Column("distribution_tariff", sa.Text(), nullable=False),
        sa.Column("offpeak_hours_0", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_1", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_2", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_3", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_4", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_5", sa.Text(), nullable=True),
        sa.Column("offpeak_hours_6", sa.Text(), nullable=True),
        sa.Column("contract_status", sa.Text(), nullable=False),
        sa.Column("last_distribution_tariff_change_date", sa.DateTime(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["usage_point_id"],
            ["usage_points.usage_point_id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    contracts = table(
        "contracts",
        column("id", Integer),
        column("usage_point_id", Text),
        column("usage_point_status", Text),
        column("meter_type", Text),
        column("segment", Text),
        column("subscribed_power", Text),
        column("last_activation_date", DateTime),
        column("distribution_tariff", Text),
        column("offpeak_hours_0", Text),
        column("offpeak_hours_1", Text),
        column("offpeak_hours_2", Text),
        column("offpeak_hours_3", Text),
        column("offpeak_hours_4", Text),
        column("offpeak_hours_5", Text),
        column("offpeak_hours_6", Text),
        column("contract_status", Text),
        column("last_distribution_tariff_change_date", DateTime),
        column("count", Integer),
    )

    data = []
    for contract in contracts_data:
        last_activation_date = datetime.strptime(contract[6], "%Y-%m-%d %H:%M:%S.%f")
        last_distribution_tariff_change_date = datetime.strptime(contract[16], "%Y-%m-%d %H:%M:%S.%f")
        data.append(
            {
                "id": contract[0],
                "usage_point_id": contract[1],
                "usage_point_status": contract[2],
                "meter_type": contract[3],
                "segment": contract[4],
                "subscribed_power": contract[5],
                "last_activation_date": last_activation_date,
                "distribution_tariff": contract[7],
                "offpeak_hours_0": contract[8],
                "offpeak_hours_1": contract[9],
                "offpeak_hours_2": contract[10],
                "offpeak_hours_3": contract[11],
                "offpeak_hours_4": contract[12],
                "offpeak_hours_5": contract[13],
                "offpeak_hours_6": contract[14],
                "contract_status": contract[15],
                "last_distribution_tariff_change_date": last_distribution_tariff_change_date,
                "count": contract[17],
            }
        )

    op.bulk_insert(contracts, data)
    op.drop_table("contracts_old")
