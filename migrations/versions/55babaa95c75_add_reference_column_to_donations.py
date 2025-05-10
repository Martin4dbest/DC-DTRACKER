"""Add reference column to donations

Revision ID: 55babaa95c75
Revises: 
Create Date: 2025-02-14 13:04:43.799518

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55babaa95c75'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add reference column to donations table
    op.add_column('donations', sa.Column('reference', sa.String(length=100), nullable=False))

    # Create unique constraint with a proper name
    op.create_unique_constraint('uq_donations_reference', 'donations', ['reference'])

    # Drop duplicate unique constraints on user.phone
    op.drop_constraint('user_phone_key', 'user', type_='unique', if_exists=True)
    op.drop_constraint('user_phone_key1', 'user', type_='unique', if_exists=True)

    # Drop password hash columns from user table (Ensure data migration if necessary)
    op.drop_column('user', 'email_password_hash', if_exists=True)
    op.drop_column('user', 'phone_password_hash', if_exists=True)


def downgrade():
    # Re-add removed columns
    op.add_column('user', sa.Column('phone_password_hash', sa.VARCHAR(length=255), nullable=True))
    op.add_column('user', sa.Column('email_password_hash', sa.VARCHAR(length=255), nullable=True))

    # Restore unique constraint on user.phone
    op.create_unique_constraint('user_phone_key', 'user', ['phone'])

    # Drop unique constraint from donations.reference
    op.drop_constraint('uq_donations_reference', 'donations', type_='unique')

    # Remove reference column from donations table
    op.drop_column('donations', 'reference')
