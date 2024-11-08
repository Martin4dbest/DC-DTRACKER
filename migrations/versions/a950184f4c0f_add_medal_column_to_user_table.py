"""Add medal column to user table

Revision ID: a950184f4c0f
Revises: 005c6296c5a4
Create Date: 2024-11-08 03:20:50.420853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a950184f4c0f'
down_revision = '005c6296c5a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('medal', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('medal')

    # ### end Alembic commands ###
