"""create_engineer_model3

Revision ID: f49929903143
Revises: 246a0ce69aa7
Create Date: 2024-03-12 13:28:55.327972

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f49929903143'
down_revision = '246a0ce69aa7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('engineers_number', sa.BigInteger(), nullable=True))
    op.add_column('order', sa.Column('state_engineers_number', sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, 'order', 'state_engineer', ['state_engineers_number'], ['state_engineers_number'])
    op.create_foreign_key(None, 'order', 'engineer', ['engineers_number'], ['engineers_number'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.drop_column('order', 'state_engineers_number')
    op.drop_column('order', 'engineers_number')
    # ### end Alembic commands ###
