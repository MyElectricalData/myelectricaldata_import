"""add tempo

Revision ID: 28b7a00bae70
Revises: 0b59c59dad3c
Create Date: 2023-02-01 00:04:06.641495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "28b7a00bae70"
down_revision = "0b59c59dad3c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tempo",
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("color", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("date"),
        sqlite_autoincrement=False,
    )


def downgrade() -> None:
    op.drop_table("tempo")
