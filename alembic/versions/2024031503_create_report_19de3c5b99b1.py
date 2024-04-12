"""create Report

Revision ID: 19de3c5b99b1
Revises: e0996b5a43df
Create Date: 2024-03-15 12:03:23.266807

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19de3c5b99b1'
down_revision = 'e0996b5a43df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('report',
    sa.Column('report_id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('order_number', sa.BigInteger(), nullable=False),
    sa.Column('all_amount', sa.BigInteger(), nullable=True),
    sa.Column('clear_amount', sa.BigInteger(), nullable=True),
    sa.Column('photo_of_agreement', sa.String(), autoincrement=False, nullable=False),
    sa.Column('tp_of_pmt_id', sa.BigInteger(), nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['order_number'], ['order.order_number'], ),
    sa.ForeignKeyConstraint(['tp_of_pmt_id'], ['type_of_payment.tp_of_pmt_id'], ),
    sa.PrimaryKeyConstraint('report_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('report')
    # ### end Alembic commands ###