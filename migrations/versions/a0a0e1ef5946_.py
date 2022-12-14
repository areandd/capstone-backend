"""empty message

Revision ID: a0a0e1ef5946
Revises: 
Create Date: 2022-11-14 14:02:59.279296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0a0e1ef5946'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('user_name', sa.String(length=30), nullable=False),
    sa.Column('banner', sa.String(length=500), nullable=True),
    sa.Column('profile_photo', sa.String(length=500), nullable=True),
    sa.Column('bio', sa.String(length=250), nullable=True),
    sa.Column('following', sa.Integer(), nullable=True),
    sa.Column('followers', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('user_name')
    )
    op.create_table('Posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('headline', sa.String(length=100), nullable=False),
    sa.Column('content', sa.String(length=240), nullable=False),
    sa.Column('date_stamp', sa.String(length=80), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Watchlist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('stock', sa.String(length=10), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Watchlist')
    op.drop_table('Posts')
    op.drop_table('User')
    # ### end Alembic commands ###
