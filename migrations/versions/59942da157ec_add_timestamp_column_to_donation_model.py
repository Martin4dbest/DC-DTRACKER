"""Add timestamp column to Donation model

Revision ID: 59942da157ec
Revises: 254be378cf8a
Create Date: 2024-11-26 23:03:24.825051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59942da157ec'
down_revision = '254be378cf8a'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column with a default value
    with op.batch_alter_table('donations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()))

    # Remove the default for future rows (optional, if no default is needed for new rows)
    with op.batch_alter_table('donations', schema=None) as batch_op:
        batch_op.alter_column('timestamp', server_default=None)


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('donations', schema=None) as batch_op:
        batch_op.drop_column('timestamp')

    # ### end Alembic commands ###