"""add agreement, fork, rejection

Revision ID: 4d91543d6c81
Revises: 6cb9574b6abe
Create Date: 2024-03-13 15:22:36.851435

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d91543d6c81'
down_revision = '6cb9574b6abe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('agreement',
    sa.Column('agreement_id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('order_number', sa.BigInteger(), nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['order_number'], ['order.order_number'], ),
    sa.PrimaryKeyConstraint('agreement_id'),
    sa.UniqueConstraint('order_number')
    )
    op.create_table('fork',
    sa.Column('fork_id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('agreement_id', sa.BigInteger(), nullable=False),
    sa.Column('amount', sa.BigInteger(), nullable=True),
    sa.Column('description', sa.String(), autoincrement=False, nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['agreement_id'], ['agreement.agreement_id'], ),
    sa.PrimaryKeyConstraint('fork_id')
    )
    op.create_table('rejection',
    sa.Column('rejection_id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('agreement_id', sa.BigInteger(), nullable=False),
    sa.Column('amount', sa.BigInteger(), nullable=True),
    sa.Column('description', sa.String(), autoincrement=False, nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['agreement_id'], ['agreement.agreement_id'], ),
    sa.PrimaryKeyConstraint('rejection_id'),
    sa.UniqueConstraint('agreement_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rejection')
    op.drop_table('fork')
    op.drop_table('agreement')
    # ### end Alembic commands ###
