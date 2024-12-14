"""Added phone_password_hash and email_password_hash

Revision ID: d67aa8cd1c8b
Revises: abfbbc92b5f2
Create Date: 2024-12-08 06:46:15.542569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd67aa8cd1c8b'
down_revision = 'abfbbc92b5f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone_password_hash', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('email_password_hash', sa.String(length=255), nullable=True))
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.create_unique_constraint(None, ['phone'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
        batch_op.drop_column('email_password_hash')
        batch_op.drop_column('phone_password_hash')

    # ### end Alembic commands ###
