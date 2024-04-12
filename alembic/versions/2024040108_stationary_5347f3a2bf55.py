"""Stationary

Revision ID: 5347f3a2bf55
Revises: 99565cef8f6c
Create Date: 2024-04-01 14:08:48.832145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5347f3a2bf55'
down_revision = '99565cef8f6c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stationary', sa.Column('done', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stationary', 'done')
    # ### end Alembic commands ###