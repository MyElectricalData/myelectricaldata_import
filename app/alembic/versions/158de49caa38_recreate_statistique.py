"""recreate statistique

Revision ID: 158de49caa38
Revises: 28b7a00bae70
Create Date: 2023-02-05 01:39:40.904230

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '158de49caa38'
down_revision = '28b7a00bae70'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table('statistique')
    op.create_table('statistique',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('usage_point_id', sa.Text(), nullable=False),
                    sa.Column('key', sa.Text(), nullable=False),
                    sa.Column('value', sa.Text(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sqlite_autoincrement=False
                    )
    op.create_index(op.f('ix_statistique_id'), 'statistique', ['id'], unique=True)

def downgrade() -> None:
    op.drop_table('statistique')