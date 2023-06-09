"""fix: column name

Revision ID: cb8bd3fe2c2d
Revises: 64da2ee7d260
Create Date: 2023-03-26 17:47:19.389262

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cb8bd3fe2c2d'
down_revision = '64da2ee7d260'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('store_hours', sa.Column('end_time_local', sa.TIME(), nullable=True))
    op.drop_column('store_hours', 'start_time_end')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('store_hours', sa.Column('start_time_end', postgresql.TIME(), autoincrement=False, nullable=True))
    op.drop_column('store_hours', 'end_time_local')
    # ### end Alembic commands ###
