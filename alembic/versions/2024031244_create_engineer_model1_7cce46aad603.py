"""create_engineer_model1

Revision ID: 7cce46aad603
Revises: 9e1fd8b06583
Create Date: 2024-03-12 12:44:33.016608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cce46aad603'
down_revision = '9e1fd8b06583'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('engineer',
    sa.Column('engineers_number', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.Uuid(as_uuid=False), nullable=True),
    sa.Column('link', sa.String(), autoincrement=False, nullable=True),
    sa.Column('name', sa.String(), autoincrement=False, nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user_account.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('engineers_number')
    )
    op.create_table('state_engineer',
    sa.Column('state_engineers_number', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.Uuid(as_uuid=False), nullable=True),
    sa.Column('link', sa.String(), autoincrement=False, nullable=True),
    sa.Column('name', sa.String(), autoincrement=False, nullable=False),
    sa.Column('create_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user_account.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('state_engineers_number')
    )
    op.create_unique_constraint(None, 'tutor', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tutor', type_='unique')
    op.drop_table('state_engineer')
    op.drop_table('engineer')
    # ### end Alembic commands ###
