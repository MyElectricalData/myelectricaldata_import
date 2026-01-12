"""add consentement expiration date

Revision ID: 955ac9d18022
Revises: 09d887b265a5
Create Date: 2022-12-01 00:01:47.011642

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "955ac9d18022"
down_revision = "09d887b265a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usage_points",
        sa.Column("consentement_expiration", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("usage_points", "consentement_expiration")
