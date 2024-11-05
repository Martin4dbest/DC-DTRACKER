"""Create pledge table

Revision ID: 34f25945432a
Revises: a096aae20bde
Create Date: 2024-11-03 06:23:36.626046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34f25945432a'
down_revision = 'a096aae20bde'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pledge',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('date_pledged', sa.Date(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Ensure password_hash remains as TEXT to accommodate longer hashes
        batch_op.alter_column('password_hash',
            existing_type=sa.String(length=255),  # Keeping it as VARCHAR(255)
            type_=sa.Text(),  # Change to TEXT to allow longer values
            existing_nullable=False)
        
        # Allow pledged_amount to be nullable
        batch_op.alter_column('pledged_amount',
            existing_type=sa.NUMERIC(precision=10, scale=2),
            nullable=True,
            existing_server_default=sa.text('0.00'))
        
        # Allow pledge_currency to be nullable
        batch_op.alter_column('pledge_currency',
            existing_type=sa.String(length=3),
            nullable=True,
            existing_server_default=sa.text("'USD'::character varying"))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('pledge_currency',
            existing_type=sa.String(length=3),
            nullable=False,
            existing_server_default=sa.text("'USD'::character varying"))
        
        batch_op.alter_column('pledged_amount',
            existing_type=sa.NUMERIC(precision=10, scale=2),
            nullable=False,
            existing_server_default=sa.text('0.00'))
        
        # Change back to VARCHAR(255) when downgrading
        batch_op.alter_column('password_hash',
            existing_type=sa.Text(),
            type_=sa.String(length=255),  # Change back to VARCHAR(255)
            existing_nullable=False)

    op.drop_table('pledge')
    # ### end Alembic commands ###
