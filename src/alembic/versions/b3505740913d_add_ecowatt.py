"""add ecowatt

Revision ID: b3505740913d
Revises: 158de49caa38
Create Date: 2023-02-06 22:41:28.765328

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "b3505740913d"
down_revision = "158de49caa38"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ecowatt",
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("date"),
        sqlite_autoincrement=False,
    )


def downgrade() -> None:
    op.drop_table("ecowatt")
