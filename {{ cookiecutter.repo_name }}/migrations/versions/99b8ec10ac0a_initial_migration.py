"""Initial Migration

Revision ID: 99b8ec10ac0a
Revises: 
Create Date: 2019-10-19 03:55:28.631412

"""
import sqlalchemy as sa
from alembic import op

from {{ cookiecutter.repo_name }}.models.types import PasswordType

# revision identifiers, used by Alembic.
revision = '99b8ec10ac0a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('password', PasswordType(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('name', name=op.f('uq_users_name'))
    )


def downgrade():
    op.drop_table('users')
