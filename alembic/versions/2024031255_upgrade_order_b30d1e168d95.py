"""upgrade Order

Revision ID: b30d1e168d95
Revises: f49929903143
Create Date: 2024-03-12 20:55:46.381934

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b30d1e168d95'
down_revision = 'f49929903143'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('name_of_customer', sa.String(length=255), nullable=True))
    op.add_column('order', sa.Column('address', sa.String(length=1000), nullable=True))
    op.alter_column('order', 'description',
               existing_type=sa.VARCHAR(length=255),
               type_=sa.String(length=1000),
               existing_nullable=True)
    op.drop_constraint('order_state_engineers_number_fkey', 'order', type_='foreignkey')
    op.drop_column('order', 'state_engineers_number')
    op.drop_column('order', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('order', sa.Column('state_engineers_number', sa.BIGINT(), autoincrement=False, nullable=True))
    op.create_foreign_key('order_state_engineers_number_fkey', 'order', 'state_engineer', ['state_engineers_number'], ['state_engineers_number'])
    op.alter_column('order', 'description',
               existing_type=sa.String(length=1000),
               type_=sa.VARCHAR(length=255),
               existing_nullable=True)
    op.drop_column('order', 'address')
    op.drop_column('order', 'name_of_customer')
    # ### end Alembic commands ###