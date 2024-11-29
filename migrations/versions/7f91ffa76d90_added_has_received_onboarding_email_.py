"""Added has_received_onboarding_email field to User model

Revision ID: 7f91ffa76d90
Revises: 4c690fa429f2
Create Date: 2024-11-28 23:38:57.681860

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f91ffa76d90'
down_revision = '4c690fa429f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('has_received_onboarding_email', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('has_received_onboarding_email')

    # ### end Alembic commands ###
