"""add tempo_config

Revision ID: e990284249e4
Revises: f599b59e8a0d
Create Date: 2023-08-26 23:33:03.239637

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "e990284249e4"
down_revision = "f599b59e8a0d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tempo_config",
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("tempo_config")
